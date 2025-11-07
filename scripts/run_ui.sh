#!/bin/bash

# SpendSense UI Runner
# This script starts the FastAPI server and opens the UI in your browser

set -e

echo "🚀 Starting SpendSense Dashboard..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "Installing uvicorn..."
    pip install uvicorn
fi

echo "✓ Environment ready"
echo ""
echo "📊 Starting server at http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python -m uvicorn spendsense.api.main:app --reload --host 0.0.0.0 --port 8000
