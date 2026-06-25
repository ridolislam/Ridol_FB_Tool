#!/bin/bash
# Ridol FB Tool - Setup Script
# Author: Ridol Islam

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     Ridol FB Tool v4.0 - Setup          ║"
echo "║     Complete Audio Experience           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check if running in Termux
if [ -d "/data/data/com.termux" ]; then
    echo "📱 Termux detected - installing dependencies..."
    pkg update -y
    pkg upgrade -y
    pkg install python python-pip git android-tools sox espeak -y
else
    echo "🐧 Linux detected - installing dependencies..."
    sudo apt update
    sudo apt install python3 python3-pip git android-tools sox espeak -y
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python packages..."
pip install requests flask gunicorn

# Create sounds directory
echo ""
echo "🎵 Generating sound effects..."
mkdir -p sounds
python3 sounds/generate_sounds.py

# Create config file
echo ""
echo "⚙️ Creating configuration..."
if [ ! -f config.json ]; then
    cat > config.json << 'EOF'
{
    "license_key": "",
    "device_serial": "",
    "data_dir": "/storage/emulated/0/Download/Ridol FB Tool"
}
EOF
fi

# Make scripts executable
chmod +x run.sh bot.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "┌──────────────────────────────────────────┐"
echo "│  🚀 To run the tool:                    │"
echo "│     ./run.sh                            │"
echo "│  or                                    │"
echo "│     python bot.py                       │"
echo "└──────────────────────────────────────────┘"
echo ""
echo "📚 For help: https://ridol-fb-tool.onrender.com"
echo ""