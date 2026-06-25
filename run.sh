#!/bin/bash
# Ridol FB Tool - Safe Launcher
# Author: Ridol Islam

clear
echo "╔══════════════════════════════════════════╗"
echo "║     Ridol FB Tool v4.0 - Launcher       ║"
echo "║     Complete Audio Experience           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found! Please run setup.sh first."
    exit 1
fi

# Check if sounds exist
if [ ! -d "sounds" ] || [ -z "$(ls -A sounds/*.wav 2>/dev/null)" ]; then
    echo "🎵 Generating sounds..."
    python sounds/generate_sounds.py
fi

# Check for config
if [ ! -f "config.json" ]; then
    echo "⚙️ Creating default config..."
    cat > config.json << 'EOF'
{
    "license_key": "",
    "device_serial": "",
    "data_dir": "/storage/emulated/0/Download/Ridol FB Tool"
}
EOF
fi

echo "🚀 Starting Ridol FB Tool..."
echo ""
python bot.py