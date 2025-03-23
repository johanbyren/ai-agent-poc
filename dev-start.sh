#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run the program
echo "Starting the program..."
python src/main.py

# Keep the shell open with the virtual environment activated
echo "Development environment is ready. You can now run './start.sh' to run the program again."
exec $SHELL 