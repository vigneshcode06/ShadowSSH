#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Try to run this file as sudo!"
    exit 1
fi

echo "🔄 Setting up ShadowSSH..."

# Define project name and paths
PROJECT_NAME="shadossh"
INSTALL_DIR="/usr/bin"
VENV_DIR="/opt/shadowssh/env"
SCRIPT_PATH="$(pwd)/shadossh.py"

# Ensure the script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Error: shadossh.py not found in the current directory!"
    exit 1
fi

# Update package lists and install required system dependencies
echo "📦 Installing required system dependencies..."
apt update && apt install -y python3 python3-venv python3-pip

# Create the installation directory if it doesn't exist
mkdir -p /opt/shadowssh

# Create a virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate the virtual environment and install dependencies
echo "📥 Installing required Python packages..."
"$VENV_DIR/bin/pip" install --break-system-packages paramiko

# Move the Python project to the installation directory
echo "🚀 Moving ShadowSSH to $INSTALL_DIR..."
mv "$SCRIPT_PATH" "/opt/shadowssh/$PROJECT_NAME.py"

# Make it executable
chmod +x "/opt/shadowssh/$PROJECT_NAME.py"

# Create a shortcut command
echo "🔗 Creating shortcut command..."
echo "#!/bin/bash" > /usr/bin/shadowssh
echo "$VENV_DIR/bin/python3 /opt/shadowssh/$PROJECT_NAME.py" >> /usr/bin/shadowssh
chmod +x /usr/bin/shadowssh

# Confirm file is removed from the original directory
echo "File has been secured"
rm -f "$SCRIPT_PATH"

echo "✅ All set and good! Just type 'shadowssh' in a new terminal to run ShadowSSH."
