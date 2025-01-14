#!/bin/bash


# Set PYTHONPATH
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install Uvicorn
apt install uvicorn -y

# Install/Upgrade required Python packages
pip install -r requirements.txt

# Start the application
uvicorn app:app --reload --host 0.0.0.0 --port 8000
