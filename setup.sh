#!/bin/bash
# Setup script for Car Scraper

echo "================================"
echo "Car Scraper - Setup"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Installing Playwright browsers..."
playwright install chromium

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To run the scraper:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
