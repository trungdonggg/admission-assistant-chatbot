#!/bin/bash

# Set PYTHONPATH
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install/Upgrade required Python packages
pip install -r requirements.txt

# Start the service
python3 service.py
