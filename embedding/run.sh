#!/bin/bash

# Set the PYTHONPATH environment variable to the parent directory of the current directory
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install Uvicorn, a lightweight ASGI server for Python
apt install uvicorn -y

# Install Python dependencies listed in the requirements file
pip install -r requirements.txt

# Start the application using Uvicorn, listening on all network interfaces at port 5000
uvicorn app:app --reload --host 0.0.0.0 --port 5000

