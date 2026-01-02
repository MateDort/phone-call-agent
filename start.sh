#!/bin/bash

# Phone Call Agent Startup Script
# This script helps you start the new Gemini Live Audio system

echo "=========================================="
echo "Phone Call Agent - Gemini Live Audio"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy env_new.example to .env and configure it:"
    echo "  cp env_new.example .env"
    echo "  # Then edit .env with your credentials"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements_new.txt

# Check for required env vars
source .env

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not set in .env"
    exit 1
fi

if [ -z "$TWILIO_ACCOUNT_SID" ]; then
    echo "❌ Error: TWILIO_ACCOUNT_SID not set in .env"
    exit 1
fi

if [ -z "$WEBHOOK_BASE_URL" ]; then
    echo "⚠️  Warning: WEBHOOK_BASE_URL not set, using default: http://localhost:5000"
fi

echo ""
echo "✅ Configuration validated"
echo ""
echo "🚀 Starting Phone Call Agent..."
echo ""
echo "Make sure you have ngrok running:"
echo "  Terminal 1: ngrok http 5000"
echo "  Terminal 2: ngrok http 5001"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the agent
python main_new.py

