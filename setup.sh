#!/bin/bash
# setup.sh - Ridol FB Tool Auto Setup for Termux
echo "====================================="
echo "  Ridol FB Tool v2.0 - Setup"
echo "====================================="
echo ""

echo "[1/5] Updating Termux..."
pkg update -y && pkg upgrade -y

echo "[2/5] Installing packages..."
pkg install python python-pip git android-tools -y

echo "[3/5] Installing Python modules..."
pip install requests pyotp

echo "[4/5] Downloading tool..."
git clone https://github.com/YourUsername/ridol-fb-tool.git
cd ridol-fb-tool

echo "[5/5] Setting up ADB..."
adb start-server 2>/dev/null
sleep 2
adb devices

echo ""
echo "====================================="
echo "  ✅ Setup Complete!"
echo "====================================="
echo ""
echo "📁 আপনার ফাইল রাখুন:"
echo "   Internal Storage/Download/Ridol FB Tool/"
echo "   ├── numbers.txt"
echo "   ├── names.txt"
echo "   └── proxies.txt"
echo ""
echo "🚀 চালানোর জন্য:"
echo "   cd ~/ridol-fb-tool && python bot.py"
echo ""
