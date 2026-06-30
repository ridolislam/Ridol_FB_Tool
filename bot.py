#!/usr/bin/env python3
"""
Ridol SaaS Tool v12.1 - Facebook OTP Sender (Forgot Password)
Author: Ridol Islam
"""

import os
import sys
import time
import json
import random
import threading
import subprocess
import requests
from datetime import datetime

# ==================== CONFIGURATION ====================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = 'https://ridol-fb-tool.onrender.com' 
APP_VERSION = 'v12.1'

os.makedirs(os.path.join(SCRIPT_DIR, 'sounds'), exist_ok=True)

# ==================== COLOR CODES ====================
class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    GOLD = '\033[38;5;214m'
    PINK = '\033[38;5;206m'

# ==================== FIND CHROMEDRIVER PATH ====================
def find_chromedriver():
    possible_paths = [
        '/data/data/com.termux/files/usr/bin/chromedriver',
        '/data/data/com.termux/files/usr/lib/chromium/chromedriver',
        '/data/data/com.termux/files/usr/libexec/chromedriver',
        '/data/data/com.termux/files/usr/bin/chromedriver.exe',
        '/usr/bin/chromedriver',
        '/usr/lib/chromium/chromedriver',
        '/usr/libexec/chromedriver',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    try:
        result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    return None

CHROMEDRIVER_PATH = find_chromedriver()

# ==================== CORE MANAGER ====================
class CoreManager:
    def __init__(self):
        self.config = self.load_config()
        self.license_key = self.config.get('license_key', '')
        self.data_dir = self.config.get('data_dir', SCRIPT_DIR)
        self.credits = 0
        self.user_id = "None"
        self.is_valid = False
        self.browser_ready = CHROMEDRIVER_PATH is not None

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f: return json.load(f)
        except: return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'license_key': self.license_key,
                'data_dir': self.data_dir
            }, f, indent=2)

    def verify_license(self, key=None):
        target = key if key else self.license_key
        if not target: return False
        try:
            resp = requests.post(f"{SERVER_URL}/api/license/verify", json={'license_key': target}, timeout=10)
            data = resp.json()
            if data.get('valid'):
                self.is_valid = True
                self.credits = data.get('credits', 0)
                self.user_id = data.get('user_id', 'User')
                self.license_key = target
                self.save_config()
                return True
        except: pass
        return False

    def get_proxy_and_deduct(self):
        try:
            resp = requests.post(f"{SERVER_URL}/api/proxy/get", json={
                'license_key': self.license_key,
                'country': 'Rand'
            }, timeout=15)
            data = resp.json()
            if data.get('success'):
                self.credits = data.get('remaining_credits', 0)
                ip = data.get('ip')
                port = data.get('port', 3010)
                return f"socks5://{ip}:{port}"
        except: pass
        return None

# ==================== STEALTH BROWSER ====================
class StealthBrowser:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.driver = None

    def start(self):
        global CHROMEDRIVER_PATH
        
        if not CHROMEDRIVER_PATH:
            print(f"{Color.RED}[-] Chromedriver not found! Please run Option 4 to install.{Color.RESET}")
            return False
            
        try:
            try:
                import undetected_chromedriver as uc
                print(f"{Color.CYAN}[*] Using undetected-chromedriver{Color.RESET}")
                
                options = uc.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--blink-settings=imagesEnabled=false')
                options.add_argument('--disable-blink-features=AutomationControlled')
                
                if self.proxy:
                    options.add_argument(f'--proxy-server={self.proxy}')
                
                self.driver = uc.Chrome(
                    options=options,
                    driver_executable_path=CHROMEDRIVER_PATH
                )
                
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return True
                
            except Exception as e:
                print(f"{Color.YELLOW}[!] undetected-chromedriver error: {e}{Color.RESET}")
                print(f"{Color.CYAN}[*] Falling back to standard Selenium{Color.RESET}")
                
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.chrome.options import Options
                
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--blink-settings=imagesEnabled=false')
                options.add_argument('--disable-blink-features=AutomationControlled')
                
                ua_list = [
                    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
                    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
                ]
                options.add_argument(f'user-agent={random.choice(ua_list)}')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                if self.proxy:
                    options.add_argument(f'--proxy-server={self.proxy}')
                
                service = Service(CHROMEDRIVER_PATH)
                self.driver = webdriver.Chrome(service=service, options=options)
                
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return True
                
        except Exception as e:
            print(f"{Color.RED}[-] Browser error: {e}{Color.RESET}")
            return False

    def stop(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

# ==================== AUDIO ENGINE ====================
class AudioEngine:
    def speak(self, text):
        try: 
            subprocess.Popen(['espeak', text, '-v', 'en+m3', '-s', '140'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

# ==================== OTP SENDER LOGIC (FORGOT PASSWORD) ====================
def forgot_password_otp_sender(driver, phone_number):
    """
    Facebook Forgot Password - OTP Sender
    শুধু OTP পাঠাবে, সাবমিট করবে না
    """
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print(f"{Color.CYAN}[*] Processing: {phone_number}{Color.RESET}")
        
        # 1. Facebook Forgot Password Page
        print(f"{Color.CYAN}[*] Navigating to Facebook Forgot Password...{Color.RESET}")
        driver.get("https://www.facebook.com/login/identify/?ctx=recover")
        time.sleep(2)
        
        # 2. Find and fill phone/email field
        print(f"{Color.CYAN}[*] Entering phone number...{Color.RESET}")
        phone_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identify_email"))
        )
        phone_field.clear()
        phone_field.send_keys(phone_number)
        time.sleep(1)
        
        # 3. Click Search button
        print(f"{Color.CYAN}[*] Clicking Search...{Color.RESET}")
        search_btn = driver.find_element(By.ID, "did_submit")
        search_btn.click()
        time.sleep(3)
        
        # 4. Check if account exists
        try:
            select_account = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'recover')]"))
            )
            select_account.click()
            time.sleep(2)
            print(f"{Color.GREEN}[+] Account found for: {phone_number}{Color.RESET}")
        except:
            print(f"{Color.YELLOW}[!] No account found for: {phone_number}{Color.RESET}")
            return False
        
        # 5. Click "Try Another Way"
        try:
            try_another = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Try another way')]"))
            )
            try_another.click()
            time.sleep(2)
        except:
            pass
        
        # 6. Select "Send code via SMS"
        try:
            sms_option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send code via SMS')]"))
            )
            sms_option.click()
            time.sleep(2)
        except:
            try:
                sms_option = driver.find_element(By.ID, "send_email")
                sms_option.click()
                time.sleep(2)
            except:
                pass
        
        # 7. Click Send/Continue
        try:
            send_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@name='reset_action']"))
            )
            send_btn.click()
            time.sleep(3)
            print(f"{Color.GREEN}[+] OTP sent to: {phone_number}{Color.RESET}")
            return True
        except:
            print(f"{Color.RED}[-] Failed to send OTP to: {phone_number}{Color.RESET}")
            return False
            
    except Exception as e:
        print(f"{Color.RED}[-] Error: {e}{Color.RESET}")
        return False

# ==================== UI & APP CONTROLLER ====================
class SaaSApp:
    def __init__(self):
        self.core = CoreManager()
        self.audio = AudioEngine()
        self.core.verify_license()

    def draw_ui(self):
        os.system('clear')
        # Title Art
        print(f"""{Color.GOLD}
   ██████╗ ██╗██████╗  ██████╗ ██╗     
   ██╔══██╗██║██╔══██╗██╔═══██╗██║     
   ██████╔╝██║██║  ██║██║   ██║██║     
   ██╔══██╗██║██║  ██║██║   ██║██║     
   ██║  ██║██║██████╔╝╚██████╔╝███████╗
   ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝{Color.RESET}""")
        print(f"            {Color.WHITE}{Color.BOLD}RIDOL FB TOOL {APP_VERSION}{Color.RESET}")
        print(f"         {Color.PINK}Facebook OTP Sender (Forgot Password){Color.RESET}")
        
        # Status Box
        print(f"  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
        br_status = f"{Color.GREEN}Active{Color.RESET}" if self.core.browser_ready else f"{Color.RED}Missing{Color.RESET}"
        lic_status = f"{Color.GREEN}Active{Color.RESET}" if self.core.is_valid else f"{Color.RED}Inactive{Color.RESET}"
        
        try:
            srv_check = requests.get(SERVER_URL, timeout=3)
            srv_status = f"{Color.GREEN}Online{Color.RESET}" if srv_check.status_code == 200 else f"{Color.RED}Offline{Color.RESET}"
        except: srv_status = f"{Color.RED}Offline{Color.RESET}"

        print(f"  {Color.CYAN}│{Color.RESET}  Browser : {br_status}  | License : {lic_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  Credits : {Color.GOLD}{self.core.credits}{Color.RESET}  | Server  : {srv_status}")
        print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")
        
        if CHROMEDRIVER_PATH:
            print(f"  {Color.DIM}Chromedriver: {CHROMEDRIVER_PATH}{Color.RESET}")

    def run_otp_sender(self):
        if not self.core.is_valid:
            print(f"\n{Color.RED}[!] Verify License First!{Color.RESET}"); time.sleep(2); return
        
        if not CHROMEDRIVER_PATH:
            print(f"\n{Color.RED}[!] Chromedriver not found!{Color.RESET}")
            print(f"{Color.YELLOW}[*] Please run Option 4 to install dependencies.{Color.RESET}")
            time.sleep(3); return
        
        data_file = os.path.join(self.core.data_dir, 'numbers.txt')
        if not os.path.exists(data_file):
            print(f"\n{Color.RED}[-] numbers.txt not found!{Color.RESET}")
            print(f"{Color.YELLOW}[*] Please add phone numbers to numbers.txt{Color.RESET}")
            time.sleep(2); return
        
        with open(data_file, 'r') as f:
            numbers = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        
        if not numbers:
            print(f"\n{Color.RED}[-] No numbers found in numbers.txt!{Color.RESET}")
            time.sleep(2); return
        
        print(f"\n{Color.GREEN}[+] Starting OTP Sender...{Color.RESET}")
        print(f"{Color.CYAN}[+] Total numbers: {len(numbers)}{Color.RESET}")
        print(f"{Color.YELLOW}[!] Each number costs 1 credit{Color.RESET}")
        print(f"{Color.YELLOW}[!] Press Ctrl+C to stop anytime{Color.RESET}")
        print("-" * 50)
        
        self.audio.speak("Starting OTP sender")

        success_count = 0
        failed_count = 0
        
        for idx, phone in enumerate(numbers, 1):
            if self.core.credits <= 0:
                print(f"\n{Color.RED}[!] Insufficient Credits!{Color.RESET}")
                print(f"{Color.YELLOW}[*] Credits remaining: 0{Color.RESET}")
                break
            
            print(f"\n{Color.GOLD}[{idx}/{len(numbers)}] Processing: {phone}{Color.RESET}")
            
            # Get proxy (deducts 1 credit)
            proxy = self.core.get_proxy_and_deduct()
            if not proxy:
                print(f"{Color.RED}[✗] No proxy available! Credits: {self.core.credits}{Color.RESET}")
                failed_count += 1
                continue

            print(f"{Color.CYAN}[*] Proxy: {proxy}{Color.RESET}")
            print(f"{Color.CYAN}[*] Remaining Credits: {self.core.credits}{Color.RESET}")

            # Start browser and send OTP
            browser = StealthBrowser(proxy)
            if browser.start():
                success = forgot_password_otp_sender(browser.driver, phone)
                if success:
                    success_count += 1
                    print(f"{Color.GREEN}[✓] OTP sent to: {phone}{Color.RESET}")
                    self.audio.speak("OTP sent")
                else:
                    failed_count += 1
                    print(f"{Color.RED}[✗] Failed: {phone}{Color.RESET}")
                browser.stop()
                print(f"{Color.DIM}[*] Browser closed{Color.RESET}")
            else:
                failed_count += 1
                print(f"{Color.RED}[✗] Browser failed to start!{Color.RESET}")
            
            # কোন Delay নেই - সাথে সাথেই পরবর্তী নাম্বারের জন্য যাবে
            # ব্রাউজার ক্লোজ হওয়ার পর সাথে সাথেই লুপের পরবর্তী ইটারেশন শুরু হবে

        # Final Summary
        print("\n" + "="*50)
        print(f"{Color.GREEN}OTP SENDER COMPLETE{Color.RESET}")
        print("="*50)
        print(f"Total Processed: {len(numbers)}")
        print(f"Success: {Color.GREEN}{success_count}{Color.RESET}")
        print(f"Failed: {Color.RED}{failed_count}{Color.RESET}")
        print(f"Credits Used: {Color.CYAN}{success_count + failed_count}{Color.RESET}")
        print(f"Credits Remaining: {Color.GOLD}{self.core.credits}{Color.RESET}")
        print("="*50)
        
        self.audio.speak("All tasks finished")
        input("\nPress Enter to continue...")

    def main_loop(self):
        self.audio.speak("Welcome to Ridol FB tool")
        while True:
            self.draw_ui()
            print(f"\n  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}   MAIN MENU - OTP SENDER                {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}├──────────────────────────────────────────┤{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Start OTP Sender                   {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Data Folder Setup                  {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[3]{Color.RESET} License Management                 {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[4]{Color.RESET} One-Click Dependencies             {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")

            choice = input(f"\n{Color.BOLD} Enter choice: {Color.RESET}").strip()
            
            if choice == '1': self.run_otp_sender()
            elif choice == '2':
                path = input(f"\n{Color.CYAN} Enter Data Folder Path: {Color.RESET}").strip()
                if os.path.exists(path):
                    self.core.data_dir = path
                    self.core.save_config()
                    print(f"{Color.GREEN}[+] Path Saved!{Color.RESET}")
                time.sleep(1)
            elif choice == '3':
                key = input(f"\n{Color.CYAN} Enter License Key: {Color.RESET}").strip().upper()
                if self.core.verify_license(key): 
                    print(f"{Color.GREEN}Verified! Credits: {self.core.credits}{Color.RESET}")
                else: 
                    print(f"{Color.RED}Invalid!{Color.RESET}")
                time.sleep(2)
            elif choice == '4':
                print(f"\n{Color.CYAN}[*] Installing Tools...{Color.RESET}")
                subprocess.run("pkg update -y && pkg install tur-repo -y && pkg install python chromium chromedriver espeak -y && pip install selenium requests undetected-chromedriver", shell=True)
                global CHROMEDRIVER_PATH
                CHROMEDRIVER_PATH = find_chromedriver()
                self.core.browser_ready = CHROMEDRIVER_PATH is not None
                if CHROMEDRIVER_PATH:
                    print(f"{Color.GREEN}[+] Chromedriver found at: {CHROMEDRIVER_PATH}{Color.RESET}")
                else:
                    print(f"{Color.RED}[-] Chromedriver still not found! Try: pkg install chromedriver{Color.RESET}")
                input("\nSetup Done. Press Enter...")
            elif choice == '0':
                self.audio.speak("Goodbye")
                sys.exit()

if __name__ == '__main__':
    try: SaaSApp().main_loop()
    except KeyboardInterrupt: 
        print(f"\n{Color.YELLOW}[!] Interrupted by user{Color.RESET}")
        sys.exit()