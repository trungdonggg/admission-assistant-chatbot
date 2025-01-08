#!/bin/bash

start_docker=true
if [ "$1" == "docker=false" ]; then
    start_docker=false
fi

if $start_docker; then
    echo "Starting Docker services..."
    # Start Docker for vector database (Weaviate)
    docker run -p 8080:8080 -p 50051:50051 cr.weaviate.io/semitechnologies/weaviate
else
    echo "Skipping Docker services setup."
fi

# Set the PYTHONPATH environment variable to the parent directory of the current directory
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install Uvicorn, a lightweight ASGI server for Python
apt install uvicorn -y

# Upgrade and install Python dependencies listed in the requirements file
pip install --upgrade -r requirements.txt

# Start the application using Uvicorn, listening on all network interfaces at port 7000
uvicorn app:app --reload --host 0.0.0.0 --port 7000
