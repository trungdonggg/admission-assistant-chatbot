#!/bin/bash

# Set the PYTHONPATH environment variable to the parent directory of the current directory
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install Python dependencies listed in the requirements file
pip install -r requirements.txt

# Start the application
python3 service.py

