#!/bin/bash

# Set the Python path
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install Uvicorn (if not already installed)
apt install uvicorn -y

# Install necessary Python dependencies from requirements.txt
pip install -r requirements.txt

# Start the Uvicorn app on port 8081
uvicorn app:app --reload --host 0.0.0.0 --port 8081

