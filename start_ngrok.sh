#!/bin/bash

# Start both ngrok tunnels from a single session
# This works with free ngrok accounts

echo "=========================================="
echo "Starting ngrok tunnels"
echo "=========================================="
echo ""

# Check if ngrok.yml exists
if [ ! -f "ngrok.yml" ]; then
    echo "❌ Error: ngrok.yml not found"
    echo "Please create it with your authtoken"
    exit 1
fi

# Check if authtoken is set
if grep -q "YOUR_NGROK_AUTHTOKEN_HERE" ngrok.yml; then
    echo "❌ Error: Please set your ngrok authtoken in ngrok.yml"
    echo ""
    echo "Steps:"
    echo "1. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "2. Replace 'YOUR_NGROK_AUTHTOKEN_HERE' in ngrok.yml with your token"
    exit 1
fi

echo "Starting both tunnels (port 5000 and 5001)..."
echo ""
echo "Once running, you'll see:"
echo "  - Forwarding URL for port 5000 (use this as WEBHOOK_BASE_URL)"
echo "  - Forwarding URL for port 5001 (WebSocket)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start ngrok with config file
ngrok start --all --config ngrok.yml

