#!/bin/bash

# Set PYTHONPATH
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install/Upgrade required Python packages
pip install -r requirements.txt

# Start the application
python3 app.py
