#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your configuration"
    exit 1
fi

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000