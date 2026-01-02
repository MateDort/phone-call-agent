#!/bin/bash

# Elderly Care Phone Agent Startup Script

echo "=========================================="
echo "Elderly Care Phone Agent"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy env.example to .env and configure it:"
    echo "  cp env.example .env"
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
pip install -q -r requirements.txt

# Check if database exists, if not, set it up
if [ ! -f "elderly_care.db" ]; then
    echo "🗄️  Setting up database..."
    python setup_elderly_db.py
fi

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

echo ""
echo "✅ Configuration validated"
echo ""
echo "🚀 Starting Elderly Care Phone Agent..."
echo ""
echo "Features:"
echo "  🔔 Smart medication reminders (automatic calls)"
echo "  👥 Family contacts with birthdays"
echo "  📖 Personal biographical information"
echo "  🔍 Google Search for current info"
echo "  🎤 Natural voice conversations"
echo ""
echo "Make sure you have ngrok running:"
echo "  Use: ./start_ngrok.sh (runs both ports from one session)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the agent using venv's Python explicitly
# Use the venv Python to ensure we use the right environment
./venv/bin/python main_elderly.py

