#!/bin/bash
# Run all SpendSense dashboards locally

echo "================================================"
echo "  Starting All SpendSense Dashboards"
echo "================================================"
echo ""
echo "This will start 3 services:"
echo "  1. Backend API Server (Port 8000)"
echo "  2. React Frontend/Operator Dashboard (Port 3000)"
echo "  3. Evaluation Metrics Dashboard (Port 5000)"
echo ""
echo "================================================"
echo ""

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Check if node_modules exists for frontend
if [ ! -d "spendsense/ui/node_modules" ]; then
    echo "❌ Frontend dependencies not installed!"
    echo "Please run: cd spendsense/ui && npm install"
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "================================================"
    echo "  Shutting down all dashboards..."
    echo "================================================"
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo "================================================"
echo "  Starting services..."
echo "================================================"
echo ""

# Start Backend API Server (Port 8000)
echo "🚀 Starting Backend API Server on http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
uvicorn spendsense.api.main:app --reload --port 8000 > /tmp/spendsense-api.log 2>&1 &
API_PID=$!
sleep 2

# Start React Frontend (Port 3000)
echo "🚀 Starting React Frontend on http://localhost:3000"
cd spendsense/ui
npm run dev > /tmp/spendsense-frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"
sleep 3

# Start Evaluation Dashboard (Port 5000)
echo "🚀 Starting Evaluation Dashboard on http://localhost:5000"
python scripts/run_dashboard.py > /tmp/spendsense-eval.log 2>&1 &
EVAL_PID=$!
sleep 2

echo ""
echo "================================================"
echo "  ✓ All Dashboards Running!"
echo "================================================"
echo ""
echo "Access URLs:"
echo "  • Backend API & Docs:  http://localhost:8000/docs"
echo "  • Frontend Dashboard:  http://localhost:3000"
echo "  • Eval Metrics:        http://localhost:5000"
echo ""
echo "Logs:"
echo "  • Backend:    tail -f /tmp/spendsense-api.log"
echo "  • Frontend:   tail -f /tmp/spendsense-frontend.log"
echo "  • Evaluation: tail -f /tmp/spendsense-eval.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "================================================"
echo ""

# Wait for all background processes
wait
