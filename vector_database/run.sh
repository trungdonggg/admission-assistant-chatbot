#!/bin/bash

# Set the Python path
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install necessary Python dependencies from requirements.txt
pip install -r requirements.txt

# Start the Uvicorn app on port 8081
python3 service.py

