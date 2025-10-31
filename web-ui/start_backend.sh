#!/bin/bash
# Start Jarvis Web UI Backend

cd "$(dirname "$0")/backend"

echo "🚀 Starting Jarvis X V2 Web Backend..."
echo ""

# Check if in venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    cd ../..
    source venv/bin/activate
    cd web-ui/backend
fi

# Install dependencies if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Start server
echo ""
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔌 WebSocket: ws://localhost:8000/ws/{client_id}"
echo ""

python3 api.py

