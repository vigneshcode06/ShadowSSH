import os
import subprocess
import sys
import venv

def create_virtualenv(env_path):
    print("[*] Creating virtual environment...")
    venv.EnvBuilder(clear=True, with_pip=True).create(env_path)
    print("[+] Virtual environment created at:", env_path)

def install_requirements(env_path):
    print("[*] Installing Python dependencies...")
    pip_executable = os.path.join(env_path, "bin", "pip")
    requirements = ["paramiko"]

    for package in requirements:
        print(f"[*] Installing {package}...")
        subprocess.run([pip_executable, "install", package])

def install_system_packages():
    # Check if system packages are installed
    required_packages = ["figlet", "lolcat"]
    for package in required_packages:
        if not is_package_installed(package):
            print(f"[*] Installing missing system package: {package}")
            os.system(f"sudo apt install -y {package}")
        else:
            print(f"[+] {package} is already installed.")

def is_package_installed(package):
    """ Check if a system package is installed. """
    result = subprocess.run(['dpkg', '-s', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def uninstall_setup():
    """ Uninstall the setup.py script after completion. """
    try:
        print("[*] Removing setup.py...")
        os.remove('setup.py')
        print("[+] setup.py has been removed.")
    except Exception as e:
        print(f"[-] Error removing setup.py: {e}")

def main():
    print("[*] Setting up your environment...")
    try:
        # Define the virtual environment path inside the ShadowSSH folder
        env_path = os.path.join(os.getcwd(), "venv")
        
        # Create a virtual environment
        create_virtualenv(env_path)
        
        # Install system-level packages
        install_system_packages()

        # Install Python packages into the virtual environment
        install_requirements(env_path)

        # print("[+] All packages installed successfully!")
        print(" _________________________________________")
        print("|[+] All packages installed successfully! |")
        print("|[+] Know try to run the Shadowssh.py     |")
        print("|-----------------------------------------|")
        print(f"[INFO] To activate the virtual environment, run:\n  source {env_path}/bin/activate")

        # Uninstall setup.py after successful installation
        uninstall_setup()

    except Exception as e:
        print(f"[-] An error occurred: {e}")

if __name__ == "__main__":
    main()
