#!/bin/bash

echo "Setting up Python 3.13 Virtual Environment on Linux..."

# Check if Python 3.13 is installed
if ! command -v python3.13 &> /dev/null; then
    echo "Python 3.13 not found!"
    
    # Check if the system is Debian-based (Ubuntu)
    if [[ -f "/etc/debian_version" ]]; then
        echo "Installing Python 3.13 (Debian/Ubuntu)..."
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update
        sudo apt install python3.13 python3.13-venv python3.13-dev -y
    else
        echo "Python 3.13 is not installed and cannot be installed automatically."
        echo "Please install Python 3.13 manually and re-run this script."
        exit 1
    fi
fi

# Define virtual environment name
VENV_DIR="venv"

# Remove old virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    echo "Removing old virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create a new virtual environment using Python 3.13
echo "Creating new virtual environment with Python 3.13..."
python3.13 -m venv "$VENV_DIR"

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt (if exists)
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping dependency installation."
fi

# Confirm installation
echo "Virtual environment setup complete!"
which python
python --version
pip list