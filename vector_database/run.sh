#!/bin/bash

# Function to check if Docker part should run
start_docker=true

# Check if "docker=false" argument is passed
if [ "$1" == "docker=false" ]; then
    start_docker=false
fi

# If Docker services need to be started
if $start_docker; then
    echo "Starting Docker services..."

    # Start Docker for vector database (Weaviate)
    docker run -p 8080:8080 -p 50051:50051 cr.weaviate.io/semitechnologies/weaviate
else
    echo "Skipping Docker services setup."
fi

# Set the Python path
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install Uvicorn (if not already installed)
apt install uvicorn

# Install necessary Python dependencies from requirements.txt
pip install -r requirements.txt

# Start the Uvicorn app on port 8081
uvicorn app:app --reload --host 0.0.0.0 --port 8081

