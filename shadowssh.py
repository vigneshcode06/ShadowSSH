import socket
import paramiko
import threading
import sys
import os
import time
import hashlib
import base64

# Integrity check function
def verify_integrity():
    script_path = os.path.abspath(__file__)
    with open(script_path, "rb") as f:
        content = f.read()
    original_hash = "d41d8cd98f00b204e9800998ecf8427e"  # Placeholder, will be set later
    current_hash = hashlib.md5(content).hexdigest()
    if current_hash != original_hash:
        print("[!] Integrity check failed! Unauthorized modifications detected.")
        sys.exit(1)

# Run integrity check before anything else
verify_integrity()

# Valid credentials for testing
valid_credentials = {
    base64.b64decode(b'YWRtaW4=').decode(): base64.b64decode(b'YWRtaW4=').decode(),
    base64.b64decode(b'cm9vdA==').decode(): base64.b64decode(b'dG9vcg==').decode(),
    base64.b64decode(b'dXNlcg==').decode(): base64.b64decode(b'cGFzc3dvcmQxMjM=').decode()
}

pwd = ["/home"]

host_key = paramiko.RSAKey.generate(2048)

os.system("clear")
os.system("figlet -f slant \"ShadowSSH\" | lolcat")

def type_text(text, color_code, speed=0.03):
    for char in text:
        sys.stdout.write(f"\033[{color_code}m{char}\033[0m")
        sys.stdout.flush()
        time.sleep(speed)
    print()

def home_logo():
    type_text("      WELCOME TO FAKE SSH HONEYPOT                   ", "92", speed=0.01)
    type_text("      DEVELOPED BY VIGNESH                           ", "92", speed=0.01)
    type_text("      MY GITHUB URL: https://github.com/vigneshcode06", "92", speed=0.01)
    print("\n")

class SSHHoneypot(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == 'session' else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username in valid_credentials and valid_credentials[username] == password:
            print(f"[+] {username} successfully logged in with {password}")
            return paramiko.AUTH_SUCCESSFUL
        print(f"[-] Invalid login attempt: {username}/{password}")
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

def get_pwd():
    return pwd[0]

def change_directory(cmd):
    global pwd
    spl = cmd.split(" ")
    if len(spl) > 1:
        pwd[0] = os.path.dirname(pwd[0]) if spl[1] == ".." else os.path.join(pwd[0], spl[1])
    return "\r\n$ "

def command_handler(cmd):
    if cmd == "pwd":
        return f"\r\n{get_pwd()} \r\n$ "
    elif cmd == "ls":
        return f"\r\nfile1.txt  file2.log  folder1  folder2 \r\n$ "
    elif "cd " in cmd:
        return change_directory(cmd)
    elif cmd.startswith("cat "):
        return f"\r\nContents of {cmd.split(' ')[1]} \r\n$ "
    return f"\r\nCommand '{cmd}' not found\r\n$ "

def handle_client(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)
    server = SSHHoneypot()
    try:
        transport.start_server(server=server)
        chan = transport.accept(20)
        if chan is None:
            print("[-] No channel request")
            return
        print("[+] Channel opened")
        server.event.wait(10)
        if not server.event.is_set():
            print("[-] No shell request")
            return
        chan.send("Welcome to Fake SSH Honeypot!\r\n$ ")
        command_buffer = ""
        while True:
            data = chan.recv(1024).decode('utf-8')
            if not data:
                break
            if data in ('\r', '\n'):
                command = command_buffer.strip()
                if command:
                    print(f"Command received: {command}")
                    output = command_handler(command)
                    chan.send(output)
                command_buffer = ""
            else:
                command_buffer += data
                chan.send(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        transport.close()

def start_honeypot():
    host = input("Enter your device IP: ")
    port = 2222
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[+] SSH Honeypot running on {host}:{port}")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[+] Connection from {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("Exiting...")
        server_socket.close()
        sys.exit()

if __name__ == "__main__":
    home_logo()
    start_honeypot()

