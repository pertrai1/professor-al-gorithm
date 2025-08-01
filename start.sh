#!/bin/bash

# Start script for Professor Al Gorithm on Hugging Face Spaces
# Runs both backend (Node.js) and frontend (Gradio) concurrently

echo "🎓 Starting Professor Al Gorithm..."

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend && npm install

# Start backend server in background
echo "🚀 Starting backend server..."
cd ../backend && npm run start &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 10

# Start Gradio frontend
echo "🎨 Starting Gradio frontend..."
cd ..
python app.py

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT