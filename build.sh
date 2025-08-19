# !/usr/bin/env bash

# Set the Python version
PYTHON_VERSION=3.9.19

# Install pyenv if not already installed (Render has it)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Install the desired Python version
pyenv install -s $PYTHON_VERSION
pyenv global $PYTHON_VERSION

# Create a virtual environment
python -m venv venv

# Activate the virtualenv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
