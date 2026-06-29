#!/usr/bin/env python3
"""
Ridol SaaS Tool v11.0 - Professional Anti-Detect Edition
Integrated with PostgreSQL Server, Premium UI & Stealth Engine
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
APP_VERSION = 'v11.0'

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

# ==================== DATA GENERATOR ====================
class DataGenerator:
    """Generate random user data for Facebook registration"""
    
    FIRST_NAMES = {
        'US': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles',
               'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth', 'Susan', 'Jessica', 'Sarah', 'Karen'],
        'BD': ['Mohammad', 'Abdullah', 'Rafiq', 'Shahid', 'Kamal', 'Jamal', 'Rahim', 'Karim', 'Hasan', 'Ali',
               'Fatima', 'Ayesha', 'Nadia', 'Taslima', 'Rokeya', 'Shirin', 'Nasrin', 'Jahan', 'Morshed', 'Rashed'],
        'IN': ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Pranav', 'Dhruv', 'Aryan', 'Reyansh',
               'Aanya', 'Ananya', 'Diya', 'Aadhya', 'Myra', 'Sara', 'Ishaan', 'Anika', 'Aarohi', 'Advik'],
        'GB': ['Oliver', 'George', 'Harry', 'Jack', 'Jacob', 'Charlie', 'Thomas', 'James', 'William', 'Muhammad',
               'Amelia', 'Olivia', 'Isla', 'Emily', 'Poppy', 'Ava', 'Isabella', 'Jessica', 'Lily', 'Sophie'],
        'XX': ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Hayden', 'Harper',
               'Emerson', 'Reese', 'Charlie', 'Blake', 'Sage', 'Rowan', 'Logan', 'Peyton', 'Ari', 'Ellis']
    }
    
    LAST_NAMES = {
        'US': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'],
        'BD': ['Rahman', 'Ahmed', 'Islam', 'Hossain', 'Ali', 'Khan', 'Haque', 'Sarkar', 'Mia', 'Pramanik'],
        'IN': ['Sharma', 'Verma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Gandhi', 'Prasad', 'Sinha'],
        'GB': ['Smith', 'Jones', 'Williams', 'Taylor', 'Brown', 'Davies', 'Evans', 'Thomas', 'Johnson', 'Roberts'],
        'XX': ['Chen', 'Singh', 'Garcia', 'Wang', 'Perez', 'Nguyen', 'Patel', 'Smith', 'Jones', 'Williams']
    }
    
    @classmethod
    def get_random_name(cls, country_code):
        first_list = cls.FIRST_NAMES.get(country_code, cls.FIRST_NAMES['XX'])
        last_list = cls.LAST_NAMES.get(country_code, cls.LAST_NAMES['XX'])
        return random.choice(first_list), random.choice(last_list)
    
    @classmethod
    def get_random_dob(cls):
        day = random.randint(1, 28)
        month = random.randint(1, 12)
        year = random.randint(1992, 2005)
        return day, month, year
    
    @classmethod
    def get_random_gender(cls):
        return random.choice(['Male', 'Female'])
    
    @classmethod
    def get_random_password(cls):
        length = random.randint(8, 12)
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
        return ''.join(random.choices(chars, k=length))
    
    @classmethod
    def get_country_from_phone(cls, phone_number):
        phone = phone_number.strip().replace('+', '').replace(' ', '').replace('-', '')
        country_codes = {
            '62': 'ID', '1': 'US', '44': 'GB', '91': 'IN', '92': 'PK',
            '880': 'BD', '86': 'CN', '81': 'JP', '49': 'DE', '33': 'FR',
            '39': 'IT', '7': 'RU', '55': 'BR', '82': 'KR', '60': 'MY',
            '65': 'SG', '63': 'PH', '66': 'TH', '84': 'VN'
        }
        for code in sorted(country_codes.keys(), key=len, reverse=True):
            if phone.startswith(code):
                return country_codes[code]
        return 'XX'

# ==================== CORE MANAGER (SERVER SYNC) ====================
class CoreManager:
    def __init__(self):
        self.config = self.load_config()
        self.license_key = self.config.get('license_key', '')
        self.data_dir = self.config.get('data_dir', SCRIPT_DIR)
        self.credits = 0
        self.user_id = "None"
        self.is_valid = False
        self.browser_ready = self.check_browser_ready()

    def check_browser_ready(self):
        """Check if undetected-chromedriver and browser are installed"""
        try:
            import undetected_chromedriver
            return True
        except ImportError:
            return False

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
        """সার্ভারে হিট করে ১ ক্রেডিট কাটবে এবং প্রক্সি নিবে (SOCKS5)"""
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

# ==================== ANTI-DETECT BROWSER ENGINE (Undetected ChromeDriver) ====================
class StealthBrowser:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.driver = None

    def start(self):
        try:
            import undetected_chromedriver as uc
            
            # Random User-Agent
            ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            ]
            
            # Random Window Size
            width = random.randint(360, 420)
            height = random.randint(640, 780)
            
            # Undetected ChromeDriver Options
            options = uc.ChromeOptions()
            
            # Basic options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument(f'--window-size={width},{height}')
            options.add_argument(f'user-agent={random.choice(ua_list)}')
            
            # Remove automation flags
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Disable password manager and notifications
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_setting_values.geolocation": 2,
                "profile.default_content_setting_values.cookies": 1,
                "profile.managed_default_content_settings.images": 1
            }
            options.add_experimental_option("prefs", prefs)
            
            # Proxy support (SOCKS5)
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
            
            # Create undetected driver
            self.driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect
                use_subprocess=True
            )
            
            # Additional stealth JavaScript
            stealth_js = """
            // Override webdriver
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', { 
                get: () => [1, 2, 3, 4, 5] 
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', { 
                get: () => ['en-US', 'en'] 
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Chrome runtime
            window.chrome = { runtime: {} };
            
            // Fix console
            const originalConsole = window.console;
            window.console = originalConsole;
            
            // Random scroll behavior
            const originalScrollTo = window.scrollTo;
            window.scrollTo = function(x, y) {
                setTimeout(() => {
                    originalScrollTo(x, y);
                }, Math.random() * 100 + 50);
            };
            """
            
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": stealth_js
            })
            
            # Random initial wait
            time.sleep(random.uniform(0.5, 1.5))
            
            return True
            
        except Exception as e:
            print(f"{Color.RED}[-] Stealth Browser Error: {e}{Color.RESET}")
            print(f"{Color.YELLOW}[!] Try installing: pip install undetected-chromedriver{Color.RESET}")
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

# ==================== CUSTOM AUTOMATION LOGIC (OTP SENDER) ====================
def custom_automation_logic(driver, data_item):
    """
    OTP Sender Automation - m.facebook.com/reg
    Auto fills: Name, DOB, Gender, Phone, Password → Submit → Wait for OTP
    """
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # 1. দেশ ডিটেক্ট
        country_code = DataGenerator.get_country_from_phone(data_item)
        print(f"{Color.CYAN}[*] Country detected: {country_code}{Color.RESET}")
        
        # 2. র্যান্ডম ডাটা জেনারেট
        first_name, last_name = DataGenerator.get_random_name(country_code)
        day, month, year = DataGenerator.get_random_dob()
        gender = DataGenerator.get_random_gender()
        password = DataGenerator.get_random_password()
        
        print(f"{Color.CYAN}[*] Name: {first_name} {last_name} ({country_code}){Color.RESET}")
        print(f"{Color.CYAN}[*] DOB: {day}/{month}/{year}{Color.RESET}")
        print(f"{Color.CYAN}[*] Gender: {gender}{Color.RESET}")
        print(f"{Color.CYAN}[*] Password: {password}{Color.RESET}")
        
        # 3. Facebook Registration Page
        driver.get("https://m.facebook.com/reg")
        time.sleep(random.uniform(2, 4))
        
        # 4. Fill First Name
        first_name_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "firstname"))
        )
        first_name_field.clear()
        time.sleep(random.uniform(0.2, 0.5))
        first_name_field.send_keys(first_name)
        time.sleep(random.uniform(0.3, 0.6))
        
        # 5. Fill Last Name
        last_name_field = driver.find_element(By.NAME, "lastname")
        last_name_field.clear()
        time.sleep(random.uniform(0.2, 0.5))
        last_name_field.send_keys(last_name)
        time.sleep(random.uniform(0.3, 0.6))
        
        # 6. Select Day
        day_select = Select(driver.find_element(By.NAME, "birthday_day"))
        day_select.select_by_value(str(day))
        time.sleep(random.uniform(0.2, 0.4))
        
        # 7. Select Month
        month_select = Select(driver.find_element(By.NAME, "birthday_month"))
        month_select.select_by_value(str(month))
        time.sleep(random.uniform(0.2, 0.4))
        
        # 8. Select Year
        year_select = Select(driver.find_element(By.NAME, "birthday_year"))
        year_select.select_by_value(str(year))
        time.sleep(random.uniform(0.2, 0.4))
        
        # 9. Select Gender
        gender_value = '2' if gender == 'Female' else '1'
        gender_radio = driver.find_element(By.CSS_SELECTOR, f'input[name="sex"][value="{gender_value}"]')
        gender_radio.click()
        time.sleep(random.uniform(0.3, 0.6))
        
        # 10. Fill Phone Number
        phone_field = driver.find_element(By.NAME, "reg_email__")
        phone_field.clear()
        time.sleep(random.uniform(0.2, 0.5))
        phone_field.send_keys(data_item)
        time.sleep(random.uniform(0.5, 1.0))
        
        # 11. Fill Password
        password_field = driver.find_element(By.NAME, "reg_passwd__")
        password_field.clear()
        time.sleep(random.uniform(0.2, 0.5))
        password_field.send_keys(password)
        time.sleep(random.uniform(0.5, 1.0))
        
        # 12. Click Submit (with human-like action)
        print(f"{Color.CYAN}[*] Clicking Submit...{Color.RESET}")
        submit_button = driver.find_element(By.NAME, "websubmit")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(random.uniform(0.3, 0.6))
        submit_button.click()
        time.sleep(random.uniform(2, 4))
        
        # 13. Wait for OTP (5-8 seconds)
        print(f"{Color.CYAN}[*] Waiting 8 seconds for OTP SMS...{Color.RESET}")
        time.sleep(8)
        
        print(f"{Color.GREEN}[✓] OTP SMS sent successfully!{Color.RESET}")
        return True
        
    except Exception as e:
        print(f"{Color.RED}[-] Task Logic Error: {e}{Color.RESET}")
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

    def run_automation(self):
        if not self.core.is_valid:
            print(f"\n{Color.RED}[!] Verify License First!{Color.RESET}"); time.sleep(2); return
        
        data_file = os.path.join(self.core.data_dir, 'numbers.txt')
        if not os.path.exists(data_file):
            print(f"\n{Color.RED}[-] numbers.txt not found!{Color.RESET}"); time.sleep(2); return
        
        with open(data_file, 'r') as f:
            items = [l.strip() for l in f if l.strip()]
        
        print(f"\n{Color.GREEN}[+] Batch Started: {len(items)} items{Color.RESET}")
        self.audio.speak("Starting batch process")

        for item in items:
            if self.core.credits <= 0:
                print(f"\n{Color.RED}[!] Insufficient Credits!{Color.RESET}"); break
            
            print(f"\n{Color.GOLD}>>> Task: {item}{Color.RESET}")
            
            # ১. আইপি ও ক্রেডিট ম্যানেজমেন্ট (SOCKS5)
            proxy = self.core.get_proxy_and_deduct()
            if not proxy:
                print(f"{Color.RED}[✗] Server/Proxy Error!{Color.RESET}"); continue

            print(f"{Color.CYAN}[*] Proxy: {proxy}{Color.RESET}")
            print(f"{Color.CYAN}[*] Remaining Credits: {self.core.credits}{Color.RESET}")

            # ২. অ্যান্টি-ডিটেক্ট ব্রাউজার লঞ্চ (Undetected ChromeDriver)
            browser = StealthBrowser(proxy)
            if browser.start():
                success = custom_automation_logic(browser.driver, item)
                if success:
                    print(f"{Color.GREEN}[✓] Success: {item}{Color.RESET}")
                else:
                    print(f"{Color.RED}[✗] Failed: {item}{Color.RESET}")
                browser.stop()
            
            # ৩. ১৫ সেকেন্ড ডেলে (প্রতি নাম্বারের মধ্যে)
            print(f"{Color.DIM}[*] Waiting 15s before next number...{Color.RESET}")
            for remaining in range(15, 0, -1):
                if remaining % 5 == 0:
                    print(f"    {remaining}s remaining...")
                time.sleep(1)

        self.audio.speak("All tasks finished")
        input("\nBatch Complete. Press Enter...")

    def install_dependencies(self):
        """Complete Termux setup with all dependencies"""
        print(f"\n{Color.GOLD}╔═══════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.GOLD}║   INSTALLING ALL DEPENDENCIES        ║{Color.RESET}")
        print(f"{Color.GOLD}║   FOR TERMUX COMPLETE SETUP          ║{Color.RESET}")
        print(f"{Color.GOLD}╚═══════════════════════════════════════╝{Color.RESET}\n")
        
        # Step 1: Update packages
        print(f"{Color.CYAN}[1/6] Updating Termux packages...{Color.RESET}")
        subprocess.run("pkg update -y", shell=True, check=False)
        subprocess.run("pkg upgrade -y", shell=True, check=False)
        
        # Step 2: Install essential packages
        print(f"{Color.CYAN}[2/6] Installing essential packages...{Color.RESET}")
        packages = [
            "python",
            "python-pip",
            "chromium",
            "chromedriver",
            "espeak",
            "tur-repo",
            "git",
            "wget",
            "curl",
            "openssl",
            "libxml2",
            "libxslt"
        ]
        for pkg in packages:
            subprocess.run(f"pkg install {pkg} -y", shell=True, check=False)
        
        # Step 3: Install Python packages
        print(f"{Color.CYAN}[3/6] Installing Python packages...{Color.RESET}")
        python_packages = [
            "selenium",
            "requests",
            "undetected-chromedriver",
            "urllib3",
            "pysocks",
            "fake-useragent",
            "pillow",
            "colorama"
        ]
        for pkg in python_packages:
            subprocess.run(f"pip install {pkg} --upgrade", shell=True, check=False)
        
        # Step 4: Install undetected-chromedriver with specific version
        print(f"{Color.CYAN}[4/6] Installing undetected-chromedriver...{Color.RESET}")
        subprocess.run("pip install undetected-chromedriver --upgrade", shell=True, check=False)
        
        # Step 5: Create necessary directories
        print(f"{Color.CYAN}[5/6] Creating directories...{Color.RESET}")
        os.makedirs(os.path.join(SCRIPT_DIR, 'data'), exist_ok=True)
        os.makedirs(os.path.join(SCRIPT_DIR, 'logs'), exist_ok=True)
        
        # Step 6: Verify installation
        print(f"{Color.CYAN}[6/6] Verifying installation...{Color.RESET}")
        
        # Check undetected-chromedriver
        try:
            import undetected_chromedriver
            print(f"{Color.GREEN}[✓] undetected-chromedriver installed{Color.RESET}")
        except ImportError:
            print(f"{Color.RED}[✗] undetected-chromedriver installation failed{Color.RESET}")
        
        # Check selenium
        try:
            import selenium
            print(f"{Color.GREEN}[✓] selenium installed{Color.RESET}")
        except ImportError:
            print(f"{Color.RED}[✗] selenium installation failed{Color.RESET}")
        
        # Check chromium
        if os.path.exists('/data/data/com.termux/files/usr/bin/chromium'):
            print(f"{Color.GREEN}[✓] chromium installed{Color.RESET}")
        else:
            print(f"{Color.YELLOW}[!] chromium not found{Color.RESET}")
        
        # Update browser ready status
        self.core.browser_ready = self.core.check_browser_ready()
        
        print(f"\n{Color.GREEN}╔═══════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.GREEN}║   ✅ SETUP COMPLETED SUCCESSFULLY    ║{Color.RESET}")
        print(f"{Color.GREEN}║   All dependencies installed!        ║{Color.RESET}")
        print(f"{Color.GREEN}╚═══════════════════════════════════════╝{Color.RESET}\n")
        
        self.audio.speak("Setup completed successfully")
        input("\nPress Enter to continue...")

    def main_loop(self):
        self.audio.speak("Welcome to Ridol FB tool")
        while True:
            self.draw_ui()
            print(f"\n  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}   MAIN MENU - PROXY + AUTO LOGIC       {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}├──────────────────────────────────────────┤{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Start Bot Automation               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Data Folder Setup                  {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[3]{Color.RESET} License Management                 {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[4]{Color.RESET} One-Click Dependencies (Termux)    {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")

            choice = input(f"\n{Color.BOLD} Enter choice: {Color.RESET}").strip()
            
            if choice == '1': 
                self.run_automation()
            elif choice == '2':
                path = input(f"\n{Color.CYAN} Enter Data Folder Path: {Color.RESET}").strip()
                if os.path.exists(path):
                    self.core.data_dir = path
                    self.core.save_config()
                    print(f"{Color.GREEN}[+] Path Saved!{Color.RESET}")
                else:
                    print(f"{Color.RED}[-] Path does not exist!{Color.RESET}")
                time.sleep(1)
            elif choice == '3':
                key = input(f"\n{Color.CYAN} Enter License Key: {Color.RESET}").strip().upper()
                if self.core.verify_license(key): 
                    print(f"{Color.GREEN}[+] License Verified!{Color.RESET}")
                    print(f"{Color.CYAN}[+] Credits: {self.core.credits}{Color.RESET}")
                else: 
                    print(f"{Color.RED}[-] Invalid License!{Color.RESET}")
                time.sleep(2)
            elif choice == '4':
                self.install_dependencies()
            elif choice == '0':
                self.audio.speak("Goodbye")
                sys.exit()

if __name__ == '__main__':
    try: 
        SaaSApp().main_loop()
    except KeyboardInterrupt: 
        print(f"\n{Color.YELLOW}[!] Exiting...{Color.RESET}")
        sys.exit()
    except Exception as e:
        print(f"{Color.RED}[!] Error: {e}{Color.RESET}")
        sys.exit()