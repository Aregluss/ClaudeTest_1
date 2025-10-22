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

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "   Install uv by running: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi
echo "✓ uv is installed"
echo ""

# Sync dependencies using uv
echo "Syncing dependencies with uv..."
uv sync

echo ""
echo "Installing Playwright browsers..."
uv run playwright install chromium

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To run the data gatherer:"
echo "  uv run python main.py"
echo ""
