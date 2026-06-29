#!/usr/bin/env python3
"""
Ridol FB Tool v8.8 - Professional OTP Sender
Integrated with PostgreSQL Server & Browser Pilot
"""

import os
import sys
import time
import json
import random
import threading
import subprocess
import requests
import re
from datetime import datetime

# ==================== CONFIGURATION ====================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(SCRIPT_DIR, 'sounds')
SERVER_URL = 'https://ridol-fb-tool.onrender.com' 
APP_VERSION = 'v8.8'

# Ensure directories exist
os.makedirs(SOUND_DIR, exist_ok=True)

# ==================== COLOR CODES ====================
class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    GOLD = '\033[38;5;214m'
    ORANGE = '\033[38;5;208m'

# ==================== HELPERS ====================
def load_json(path):
    try:
        with open(path, 'r') as f: return json.load(f)
    except: return {}

def save_json(path, data):
    try:
        with open(path, 'w') as f: json.dump(data, f, indent=2); return True
    except: return False

def load_file_lines(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [l.strip() for l in f if l.strip() and not l.startswith('#')]
    except: return []

# ==================== AUDIO ENGINE ====================
class AudioEngine:
    def speak(self, text):
        try: subprocess.Popen(['espeak', text, '-v', 'en+m3', '-s', '140'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

# ==================== DATA GENERATOR ====================
class DataGenerator:
    @staticmethod
    def get_user_data():
        first = ['Mohammad', 'Abdullah', 'Rafiq', 'Shahid', 'Kamal', 'Jamal', 'Rahim', 'Karim', 'Hasan', 'Ali', 'Ayesha', 'Fatima', 'Nadia', 'Taslima']
        last = ['Rahman', 'Ahmed', 'Islam', 'Hossain', 'Khan', 'Haque', 'Sarkar', 'Mia', 'Pramanik']
        return {
            'first': random.choice(first),
            'last': random.choice(last),
            'day': str(random.randint(1, 28)),
            'month': str(random.randint(1, 12)),
            'year': str(random.randint(1992, 2005)),
            'gender': random.choice(['1', '2']) # 1=Female, 2=Male
        }

# ==================== LICENSE & PROXY MANAGER ====================
class CoreManager:
    def __init__(self):
        self.config = load_json(CONFIG_FILE)
        self.license_key = self.config.get('license_key', '')
        self.credits = 0
        self.user_id = "None"
        self.is_valid = False
        self.browser_ready = self._check_browser()

    def _check_browser(self):
        try:
            import termux_browser_pilot
            return True
        except: return False

    def verify_license(self, key=None):
        target = key if key else self.license_key
        if not target: return False
        try:
            resp = requests.post(f"{SERVER_URL}/api/license/verify", json={'license_key': target}, timeout=10)
            data = resp.json()
            if data.get('valid'):
                self.is_valid = True
                self.credits = data.get('credits', 0)
                self.user_id = data.get('user_id', 'Ridol')
                self.license_key = target
                self.config['license_key'] = target
                save_json(CONFIG_FILE, self.config)
                return True
        except: pass
        return False

    def get_proxy(self):
        try:
            resp = requests.post(f"{SERVER_URL}/api/proxy/get", json={'license_key': self.license_key, 'country': 'Rand'}, timeout=15)
            data = resp.json()
            if data.get('success'):
                self.credits = data.get('remaining_credits')
                return f"socks5://{data.get('ip')}:3010"
        except: pass
        return None

# ==================== AUTOMATION ENGINE ====================
class AutomationEngine:
    def __init__(self, core, audio):
        self.core = core
        self.audio = audio

    def start_task(self, phone):
        proxy = self.core.get_proxy()
        if not proxy: return False, "Proxy/Credit Error"

        from termux_browser_pilot import Browser
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy
        
        browser = None
        try:
            browser = Browser(headless=False)
            data = DataGenerator.get_user_data()
            
            browser.goto("https://m.facebook.com/reg")
            time.sleep(2)
            
            # Fill Form
            browser.type('input[name="firstname"]', data['first'])
            browser.type('input[name="lastname"]', data['last'])
            browser.select('select[id="day"]', data['day'])
            browser.select('select[id="month"]', data['month'])
            browser.select('select[id="year"]', data['year'])
            
            if data['gender'] == '1': browser.click('input[value="1"]') # Female
            else: browser.click('input[value="2"]') # Male
            
            browser.type('input[name="reg_email__"]', phone)
            time.sleep(1)
            
            # Submit to send OTP
            browser.click('button[name="submit"]')
            time.sleep(5) # Wait for SMS trigger
            return True, "Success"
        except Exception as e:
            return False, str(e)
        finally:
            if browser: browser.close()

# ==================== UI DESIGN ====================
class UI:
    @staticmethod
    def draw_banner(core):
        os.system('clear')
        # ASCII Art Title
        print(f"""{Color.GOLD}  
   ██████╗ ██╗██████╗  ██████╗ ██╗     
   ██╔══██╗██║██╔══██╗██╔═══██╗██║     
   ██████╔╝██║██║  ██║██║   ██║██║     
   ██╔══██╗██║██║  ██║██║   ██║██║     
   ██║  ██║██║██████╔╝╚██████╔╝███████╗
   ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝{Color.RESET}""")
        
        print(f"            {Color.WHITE}{Color.BOLD}RIDOL FB TOOL v{APP_VERSION}{Color.RESET}")
        print(f"      {Color.DIM}Proxy Rotation + Auto Name Gen{Color.RESET}")
        
        # Status Box
        print(f"{Color.CYAN}  ┌──────────────────────────────────────────┐{Color.RESET}")
        
        br_status = f"{Color.GREEN}Active{Color.RESET}" if core.browser_ready else f"{Color.RED}Missing{Color.RESET}"
        lic_status = f"{Color.GREEN}Active{Color.RESET}" if core.is_valid else f"{Color.RED}Inactive{Color.RESET}"
        
        # Check server online
        try:
            srv_resp = requests.get(SERVER_URL, timeout=3)
            srv_status = f"{Color.GREEN}Online{Color.RESET}" if srv_resp.status_code == 200 else f"{Color.RED}Offline{Color.RESET}"
        except: srv_status = f"{Color.RED}Offline{Color.RESET}"

        print(f"  {Color.CYAN}│{Color.RESET}  Browser  : {br_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}●{Color.RESET} License : {lic_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.RED}●{Color.RESET} Server  : {srv_status}")
        print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")

    @staticmethod
    def show_menu():
        print(f"\n  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}   MAIN MENU - PROXY + AUTO NAME        {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}├──────────────────────────────────────────┤{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Browser Pilot Setup                {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Data Folder                        {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[3]{Color.RESET} License Management                 {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Start Bot                          {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Status                             {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[6]{Color.RESET} Audio Settings                    {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[7]{Color.RESET} Demo                               {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[8]{Color.RESET} Help                               {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}│{Color.RESET}")
        print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")

# ==================== MAIN CONTROLLER ====================
class RidolBot:
    def __init__(self):
        self.core = CoreManager()
        self.audio = AudioEngine()
        self.automation = AutomationEngine(self.core, self.audio)
        self.core.verify_license()

    def start_process(self):
        if not self.core.is_valid:
            print(f"\n{Color.RED}[!] Please verify license first!{Color.RESET}"); time.sleep(2); return
        
        data_path = os.path.join(self.core.config.get('data_dir', SCRIPT_DIR), 'numbers.txt')
        numbers = load_file_lines(data_path)
        
        if not numbers:
            print(f"\n{Color.RED}[-] numbers.txt is empty!{Color.RESET}"); time.sleep(2); return
        
        UI.draw_banner(self.core)
        print(f"\n{Color.GREEN}[+] Batch Started: {len(numbers)} numbers{Color.RESET}")
        self.audio.speak("Starting batch process")
        
        for num in numbers:
            if self.core.credits <= 0:
                print(f"{Color.RED}[-] Out of credits!{Color.RESET}"); break
            
            print(f"\n{Color.GOLD}>>> Task: {num}{Color.RESET}")
            success, msg = self.automation.start_task(num)
            
            if success:
                print(f"{Color.GREEN}[✓] OTP Sent to {num}{Color.RESET}")
            else:
                print(f"{Color.RED}[✗] Error: {msg}{Color.RESET}")
            
            time.sleep(2)
        
        print(f"\n{Color.GREEN}[+] All Tasks Finished!{Color.RESET}")
        self.audio.speak("Process completed")
        input("Press Enter...")

    def run(self):
        self.audio.speak("Welcome to Ridol F B tool")
        while True:
            UI.draw_banner(self.core)
            UI.show_menu()
            
            choice = input(f"\n{Color.BOLD} Enter choice: {Color.RESET}").strip()
            
            if choice == '1':
                print(f"\n{Color.CYAN}[*] Installing dependencies...{Color.RESET}")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'termux-browser-pilot'])
                self.core.browser_ready = self.core._check_browser()
                input("\nInstallation done. Press Enter...")
            
            elif choice == '2':
                path = input(f"\n{Color.CYAN} Enter Data Path: {Color.RESET}").strip()
                if os.path.exists(path):
                    self.core.config['data_dir'] = path
                    save_json(CONFIG_FILE, self.core.config)
                    print(f"{Color.GREEN}[+] Path Saved!{Color.RESET}")
                else: print(f"{Color.RED}[-] Invalid Path!{Color.RESET}")
                time.sleep(1)

            elif choice == '3':
                key = input(f"\n{Color.CYAN} Enter License Key: {Color.RESET}").strip().upper()
                if self.core.verify_license(key):
                    print(f"{Color.GREEN}[+] License Verified!{Color.RESET}")
                else: print(f"{Color.RED}[-] Invalid Key!{Color.RESET}")
                time.sleep(2)

            elif choice == '4':
                self.start_process()

            elif choice == '5':
                UI.draw_banner(self.core)
                print(f"\n  {Color.WHITE}User ID  : {self.core.user_id}")
                print(f"  Credits  : {self.core.credits}")
                print(f"  Key      : {self.core.license_key}")
                input("\nPress Enter...")

            elif choice == '0':
                print(f"\n{Color.YELLOW}Goodbye!{Color.RESET}")
                self.audio.speak("Goodbye")
                sys.exit()

if __name__ == '__main__':
    try:
        bot = RidolBot()
        bot.run()
    except KeyboardInterrupt:
        sys.exit()