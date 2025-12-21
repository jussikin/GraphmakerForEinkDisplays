#!/bin/bash

# Convenience script to run graph_maker.py in the virtual environment

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Activate venv and run the script
source venv/bin/activate
python graph_maker.py
deactivate
