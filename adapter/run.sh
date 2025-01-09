#!/bin/bash


# Check if the first argument is "firsttime"
if [ "$1" == "firsttime" ]; then
    echo "Running setup for the first time..."
    
    # Initialize project if package.json doesn't exist
    if [ ! -f package.json ]; then
        npm init -y
    fi

    # Install dependencies
    npm install express body-parser axios dotenv
fi

# Start the server
echo "Starting the server..."
node index.js
