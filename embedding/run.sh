#!/bin/bash

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Activate the virtual environment (if you have one)
# source venv/bin/activate

# Set the FLASK_APP environment variable
export FLASK_APP=app.py

# Run the Flask app
python3 app.py

# Or if you want to run it in production mode:
# flask run --host=0.0.0.0 --port=8000
