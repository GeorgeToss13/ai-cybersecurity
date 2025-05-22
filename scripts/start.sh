#!/bin/bash

echo "=================================================="
echo "  CyberSec AI Bot - Starting Services"
echo "=================================================="
echo ""
echo "Starting backend, frontend, and database services..."
echo ""

# Check if MongoDB is running
echo "Checking MongoDB status..."
if systemctl is-active --quiet mongodb; then
    echo "✅ MongoDB is running"
else
    echo "⚠️  MongoDB is not running. Starting MongoDB..."
    sudo systemctl start mongodb
    sleep 2
    if systemctl is-active --quiet mongodb; then
        echo "✅ MongoDB started successfully"
    else
        echo "❌ Failed to start MongoDB"
    fi
fi

# Restart backend and frontend services
echo ""
echo "Restarting services..."
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
echo "✅ Services restarted"

# Display service status
echo ""
echo "Service status:"
sudo supervisorctl status

# Display access information
echo ""
echo "=================================================="
echo "  Access Information"
echo "=================================================="
echo ""
echo "Frontend Dashboard: http://localhost:3000"
echo "Backend API: http://localhost:8001/api"
echo ""
echo "For external access, use the provided URL from your"
echo "deployment environment."
echo ""
echo "=================================================="
echo "  Configuration Required"
echo "=================================================="
echo ""
echo "⚠️  Important: Before using the application, you need to configure:"
echo ""
echo "1. OpenAI API Key - For AI assistant capabilities"
echo "   Get it from: https://platform.openai.com/account/api-keys"
echo ""
echo "2. Telegram Bot Token - For Telegram integration"
echo "   Get it by creating a bot with @BotFather on Telegram"
echo ""
echo "You can configure these in the Configuration tab of the dashboard."
echo ""
echo "=================================================="
echo ""
echo "CyberSec AI Bot is now running!"
echo ""
