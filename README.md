# 🎵 Ridol FB Tool v4.0 - Complete Audio Experience

<div align="center">

![Version](https://img.shields.io/badge/version-4.0-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux-lightgrey.svg)

**Complete Facebook account creation automation tool with sound effects, voice feedback, animations, and license management**

[![Run on Repl.it](https://repl.it/badge/github/ridolislam/Ridol_FB_Tool)](https://repl.it/github/ridolislam/Ridol_FB_Tool)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Installation](#-quick-installation)
- [Manual Installation](#-manual-installation)
- [License Server](#-license-server)
- [Usage Guide](#-usage-guide)
- [Audio System](#-audio-system)
- [Bot Configuration](#-bot-configuration)
- [Troubleshooting](#-troubleshooting)
- [Legal Disclaimer](#-legal-disclaimer)

---

## ✨ Features

### 🎵 Audio Experience
- **6 High-quality sound effects** (click, success, fail, done, startup, binary rain)
- **Deep male voice feedback** via eSpeak (en+m3)
- **Background ambiance** with cyberpunk binary rain
- **Multi-threaded playback** for smooth experience

### 🎨 Visual Animations
- **Matrix rain effect** (real-time)
- **Typing text animation**
- **Spinner & progress bar**
- **Logo animation on startup**
- **Graceful exit animation**

### 📱 Device Management
- **ADB integration** for Android devices
- **WiFi device connection** support
- **Device ID retrieval** (Android ID)
- **USB & wireless debugging** support

### 🔐 License System
- **Server-based license verification**
- **Admin panel** for license management
- **Auto-expiry** with configurable days
- **Ban/Unban** functionality
- **Device registration** tracking

### 🤖 Facebook Bot
- **Phone number processing** with country detection
- **Proxy support** for anonymity
- **Success/Failure statistics**
- **Configurable workers** (1-5)
- **Auto-retry** mechanism
- **Audio feedback** on each operation

---

## 🚀 Quick Installation

### One-Line Command (Termux)

```bash
pkg update -y && pkg upgrade -y && pkg install python python-pip git android-tools sox espeak -y && pip install requests && git clone https://github.com/ridolislam/Ridol_FB_Tool.git && cd Ridol_FB_Tool && bash setup.sh && python bot.py