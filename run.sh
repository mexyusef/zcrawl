#!/bin/bash

# Run ZCrawl application
echo "Starting ZCrawl application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Run the application
python3 -m zcrawl

echo "ZCrawl application closed."
