#!/bin/bash

# Function to check if Docker part should run
start_docker=true
if [ "$1" == "docker=false" ]; then
    start_docker=false
fi

if $start_docker; then
    echo "Starting Docker services..."

    # Start Docker for database (MongoDB)
    docker run --name mongodb -d -p 27017:27017 mongo

    # Start Docker for object storage (MinIO)
    mkdir -p ~/minio/data

    docker run \
        -p 9000:9000 \
        -p 9001:9001 \
        --name minio \
        -v ~/minio/data:/data \
        -e "MINIO_ROOT_USER=minio" \
        -e "MINIO_ROOT_PASSWORD=minio123" \
        quay.io/minio/minio server /data --console-address ":9001"
else
    echo "Skipping Docker services setup."
fi

# Set PYTHONPATH
export PYTHONPATH=$(dirname "$(pwd -P)")

# Install Uvicorn
apt install uvicorn -y

# Install/Upgrade required Python packages
pip install --upgrade -r requirements.txt

# Start the application
uvicorn app:app --reload --host 0.0.0.0 --port 8000
