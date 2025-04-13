#!/bin/bash

# Ensure MongoDB is running
echo "Checking if MongoDB is running..."
if ! pgrep -x mongod > /dev/null; then
    echo "MongoDB is not running. Starting MongoDB..."
    # Uncomment and modify the line below based on your MongoDB installation method
    # mongod --dbpath /usr/local/var/mongodb --logpath /usr/local/var/log/mongodb/mongo.log --fork
    
    echo "⚠️  Please ensure MongoDB is running before continuing"
    echo "You may need to start it manually with: brew services start mongodb-community"
    exit 1
fi

echo "MongoDB is running."

# Set environment variables if needed
export FLASK_APP=run.py
export FLASK_ENV=development

# Install dependencies if needed
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting Flask server..."
python run.py
