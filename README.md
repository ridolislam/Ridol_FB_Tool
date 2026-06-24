# Ridol FB Tool v2.0

Facebook Lite Account Creator with Smart Proxy Rotation & Country Matching

## Features
- ✅ Automated Facebook Lite account creation
- ✅ Smart proxy rotation by country code
- ✅ Phone number → country auto-detection
- ✅ User data files from Download folder
- ✅ License-based access control (Render server)
- ✅ Admin panel (HTML + CSS + JS)
- ✅ OTP auto-read via SMS

## User Setup (Termux)
```bash
pkg update && pkg upgrade -y
pkg install python python-pip git android-tools -y
pip install requests
git clone https://github.com/YourUsername/ridol-fb-tool.git
cd ridol-fb-tool

# Enable Developer Options > USB Debugging
adb start-server
adb devices   # Must show "device"

python bot.py
