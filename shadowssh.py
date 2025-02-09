import socket
import paramiko
import threading
import sys
import os
import time

# Valid credentials for testing
valid_credentials = {
    'admin': 'admin',
    'root': 'toor',
    'user': 'password123'
}

# Simulated current working directory
pwd = ["/home"]

# Simulate a host key
host_key = paramiko.RSAKey.generate(2048)

# Display welcome logo
os.system("clear")
os.system("figlet -f slant \"ShadowSSH\" | lolcat")

# Function to print text with typing effect
def type_text(text, color_code, speed=0.03):
    for char in text:
        sys.stdout.write(f"\033[{color_code}m{char}\033[0m")
        sys.stdout.flush()
        time.sleep(speed)  # Adjust for typing speed
    print()  # To move to the next line after the text finishes

# Display the intro text
def home_logo():
    # Set both texts to hacker green (Bright Green - 92)
    type_text("   WELCOME TO SHADOWSSH - THE DARK SIDE OF CYBERSPACE", "92", speed=0.02)  # Bright Green text
    time.sleep(0.5)  # Pause before next line
    type_text("   POWERED BY ZENTHHACKER.", "92", speed=0.02)  # Bright Green text
    print("\n")

# SSH Server Interface
class SSHHoneypot(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username in valid_credentials and valid_credentials[username] == password:
            print(f"[+] {username} successfully logged in with {password}")
            return paramiko.AUTH_SUCCESSFUL
        print(f"[-] Invalid login attempt: {username}/{password}")
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

# Command handlers
def get_pwd():
    return pwd[0]

def change_directory(cmd):
    global pwd
    spl = cmd.split(" ")
    if len(spl) > 1:
        if spl[1] == "..":
            pwd[0] = os.path.dirname(pwd[0])
        else:
            pwd[0] = os.path.join(pwd[0], spl[1])
    return f"\r\n$ "

def command_handler(cmd):
    if cmd == "pwd":
        return f"\r\n{get_pwd()} \r\n$ "
    elif cmd == "ls":
        # Simulated directory contents
        return f"\r\nfile1.txt  file2.log  folder1  folder2 \r\n$ "
    elif "cd " in cmd:
        return change_directory(cmd)
    elif cmd.startswith("cat "):
        return f"\r\nContents of {cmd.split(' ')[1]} \r\n$ "
    else:
        return f"\r\nCommand '{cmd}' not found\r\n$ "

# Handle client connections
def handle_client(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)
    server = SSHHoneypot()

    try:
        transport.start_server(server=server)
        chan = transport.accept(20)  # Wait for a channel to open

        if chan is None:
            print("[-] No channel request")
            return

        print("[+] Channel opened")
        server.event.wait(10)  # Wait for the shell request

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

# Start the honeypot
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
    home_logo()  # Display intro with animation
    start_honeypot()  # Start the honeypot

