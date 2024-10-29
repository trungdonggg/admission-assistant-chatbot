#!/bin/bash

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Set environment variables for Flask
export FLASK_APP=app.py

# Run the Flask application
python app.py

