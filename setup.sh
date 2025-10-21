#!/bin/bash
# Setup script for Car Data Gatherer

echo "================================"
echo "Car Data Gatherer - Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.12 or higher is required"
    echo "   Current version: $python_version"
    echo "   Please upgrade Python and try again"
    exit 1
fi
echo "✓ Python version $python_version (meets requirement >= 3.12)"
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
echo "To run the data gatherer:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
