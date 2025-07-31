#!/bin/bash

# Gaming Marketplace Bot Deployment Script
# ========================================

echo "🎮 Gaming Marketplace Bot - Deployment Script"
echo "=============================================="

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure it:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

echo "✅ Environment file found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check if PostgreSQL is running
if command -v pg_isready >/dev/null 2>&1; then
    if ! pg_isready -q; then
        echo "⚠️  Warning: PostgreSQL doesn't seem to be running"
        echo "   Please start PostgreSQL service before running the bot"
    else
        echo "✅ PostgreSQL is running"
    fi
else
    echo "⚠️  Warning: PostgreSQL client not found. Make sure PostgreSQL is installed and running"
fi

# Check if Redis is running
if command -v redis-cli >/dev/null 2>&1; then
    if ! redis-cli ping >/dev/null 2>&1; then
        echo "⚠️  Warning: Redis doesn't seem to be running"
        echo "   Please start Redis service before running the bot"
    else
        echo "✅ Redis is running"
    fi
else
    echo "⚠️  Warning: Redis client not found. Make sure Redis is installed and running"
fi

# Load environment variables
export $(cat .env | grep -v ^# | xargs)

# Validate required environment variables
required_vars=("BOT_TOKEN" "DATABASE_URL" "REDIS_URL" "CHANNEL_ID" "MODERATOR_GROUP_ID" "ADMIN_IDS")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    printf "   %s\n" "${missing_vars[@]}"
    echo "   Please configure them in .env file"
    exit 1
fi

echo "✅ Environment variables validated"

# Create logs directory
mkdir -p logs

echo ""
echo "🚀 Starting Gaming Marketplace Bot..."
echo "📝 Logs will be saved to bot.log"
echo "🛑 Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python main.py

echo ""
echo "🛑 Bot stopped"
echo "👋 Thank you for using Gaming Marketplace Bot!"