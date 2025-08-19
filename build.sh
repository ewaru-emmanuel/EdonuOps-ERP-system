#!/usr/bin/env bash

set -e  # Exit on error

# Use pyenv to install and switch Python version
PYTHON_VERSION=$(cat .python-version)

# Ensure pyenv is available
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Install and set Python
pyenv install -s $PYTHON_VERSION
pyenv global $PYTHON_VERSION
python --version  # Debugging info

# Create virtualenv and install dependencies
python -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
