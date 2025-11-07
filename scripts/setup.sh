#!/bin/bash

# SpendSense Setup Script
# This script automates the initial project setup

set -e  # Exit on error

echo "🚀 Setting up SpendSense..."
echo

# Check Python version
echo "📝 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.10 or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"
echo

# Check Node.js version
echo "📝 Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "   Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
node_version=$(node --version)
echo "✅ Node.js version: $node_version"
echo

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"
echo

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"
echo

# Install frontend dependencies
echo "⚛️  Installing frontend dependencies..."
cd spendsense/ui
npm install
cd ../..
echo "✅ Frontend dependencies installed"
echo

# Initialize data directories (already created, but ensure .gitkeep files exist)
echo "📁 Initializing data directories..."
touch data/synthetic/.gitkeep
touch data/sqlite/.gitkeep
touch data/parquet/.gitkeep
touch data/logs/.gitkeep
echo "✅ Data directories initialized"
echo

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
pytest tests/test_setup.py -v
echo "✅ Tests passed"
echo

echo "🎉 Setup complete!"
echo
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run backend tests: pytest"
echo "3. Start the frontend dev server: cd spendsense/ui && npm run dev"
echo "4. Start the API server (when implemented): uvicorn spendsense.api.main:app --reload"
echo
