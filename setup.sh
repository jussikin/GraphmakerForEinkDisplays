#!/bin/bash

# Setup script for Graph Maker project
# Creates virtual environment and installs dependencies

echo "Setting up Graph Maker virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "To use the project:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the script: python graph_maker.py"
echo "  3. When done, deactivate: deactivate"
