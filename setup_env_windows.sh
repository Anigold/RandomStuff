#!/bin/bash

echo "Setting up Python 3.13 Virtual Environment on Windows (Git Bash)..."

echo "Checking Python version..."

# Get the first two digits of the Python version
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

REQUIRED_VERSION="3.13"

if [ "$PYTHON_VERSION" == "$REQUIRED_VERSION" ]; then
    echo "Python $PYTHON_VERSION is set correctly!"
else
    echo "Python $PYTHON_VERSION is active instead of $REQUIRED_VERSION!"
    echo "Please update your default Python version."
    exit 1  # Exit with error
fi

# Define the virtual environment directory
VENV_DIR="venv"

# Remove old virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    echo "Removing old virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create a new virtual environment
echo "Creating new virtual environment with Python 3.13..."
python -m venv "$VENV_DIR"

# Activate the virtual environment
source "$VENV_DIR/Scripts/activate"

# Upgrade pip inside venv
echo "Upgrading pip and setuptools..."
python -m pip install --upgrade pip setuptools wheel

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping dependency installation."
fi

# Keep the environment activated
echo "Virtual environment setup complete!"
python --version
pip list
