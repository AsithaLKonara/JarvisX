#!/bin/bash
# Start Jarvis Web UI Frontend

cd "$(dirname "$0")/frontend"

echo "🎨 Starting Jarvis X V2 Web Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start Vite dev server
echo ""
echo "✅ Starting Vite dev server on http://localhost:3000"
echo "🎨 UI will auto-reload on changes"
echo ""

npm run dev

