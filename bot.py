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
import subprocess
import requests
import zipfile
import urllib.request
from datetime import datetime

# ==================== CONFIGURATION ====================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = 'https://ridol-fb-tool.onrender.com' 
APP_VERSION = 'v11.0'

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
        return random.randint(1, 28), random.randint(1, 12), random.randint(1992, 2005)
    
    @classmethod
    def get_random_gender(cls):
        return random.choice(['Male', 'Female'])
    
    @classmethod
    def get_random_password(cls):
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
        return ''.join(random.choices(chars, k=random.randint(8, 12)))
    
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

# ==================== CHROMEDRIVER MANAGER ====================
class ChromeDriverManager:
    @staticmethod
    def get_chromedriver_path():
        """Check for ChromeDriver in multiple locations"""
        # 1. Check project directory
        local_path = os.path.join(SCRIPT_DIR, 'chromedriver')
        if os.path.exists(local_path):
            return local_path
        
        # 2. Check project directory with .exe (Windows)
        local_path_exe = os.path.join(SCRIPT_DIR, 'chromedriver.exe')
        if os.path.exists(local_path_exe):
            return local_path_exe
        
        # 3. Check system paths
        system_paths = [
            '/data/data/com.termux/files/usr/bin/chromedriver',
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            '/opt/chromedriver/chromedriver'
        ]
        for path in system_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @staticmethod
    def download_chromedriver():
        """Download ChromeDriver automatically"""
        print(f"{Color.CYAN}[*] Downloading ChromeDriver...{Color.RESET}")
        
        # Detect architecture
        arch = os.uname().machine
        if arch == 'aarch64' or arch == 'arm64':
            driver_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/124.0.6367.91/linux-arm64/chromedriver-linux-arm64.zip"
        else:
            driver_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/124.0.6367.91/linux64/chromedriver-linux64.zip"
        
        try:
            # Download zip file
            zip_path = os.path.join(SCRIPT_DIR, 'chromedriver.zip')
            urllib.request.urlretrieve(driver_url, zip_path)
            
            # Extract zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(SCRIPT_DIR)
            
            # Find extracted chromedriver
            extracted_dirs = [d for d in os.listdir(SCRIPT_DIR) if d.startswith('chromedriver-linux')]
            for dir_name in extracted_dirs:
                src = os.path.join(SCRIPT_DIR, dir_name, 'chromedriver')
                dst = os.path.join(SCRIPT_DIR, 'chromedriver')
                if os.path.exists(src):
                    os.rename(src, dst)
                    # Make executable
                    os.chmod(dst, 0o755)
                    # Cleanup
                    import shutil
                    shutil.rmtree(os.path.join(SCRIPT_DIR, dir_name))
                    break
            
            # Remove zip file
            os.remove(zip_path)
            
            print(f"{Color.GREEN}[✓] ChromeDriver downloaded successfully!{Color.RESET}")
            return True
            
        except Exception as e:
            print(f"{Color.RED}[✗] ChromeDriver download failed: {e}{Color.RESET}")
            return False

# ==================== CORE MANAGER ====================
class CoreManager:
    def __init__(self):
        self.config = self.load_config()
        self.license_key = self.config.get('license_key', '')
        self.data_dir = self.config.get('data_dir', SCRIPT_DIR)
        self.credits = 0
        self.user_id = "None"
        self.is_valid = False
        self.browser_ready = self.check_browser_ready()
        self.undetected_available = self.check_undetected_chromedriver()
        self.browser_active = False

    def check_browser_ready(self):
        """Check if ChromeDriver exists"""
        return ChromeDriverManager.get_chromedriver_path() is not None

    def check_undetected_chromedriver(self):
        """Check if undetected-chromedriver is installed"""
        try:
            import undetected_chromedriver
            return True
        except ImportError:
            return False

    def install_undetected_chromedriver(self):
        """Install undetected-chromedriver package"""
        print(f"{Color.CYAN}[*] Installing undetected-chromedriver...{Color.RESET}")
        try:
            subprocess.run(
                "pip install undetected-chromedriver --upgrade",
                shell=True, 
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Verify installation
            self.undetected_available = self.check_undetected_chromedriver()
            if self.undetected_available:
                print(f"{Color.GREEN}[✓] undetected-chromedriver installed!{Color.RESET}")
                return True
            else:
                print(f"{Color.YELLOW}[!] undetected-chromedriver installation failed{Color.RESET}")
                return False
        except:
            return False

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'license_key': self.license_key,
                'data_dir': self.data_dir
            }, f, indent=2)

    def verify_license(self, key=None):
        target = key if key else self.license_key
        if not target:
            return False
        try:
            resp = requests.post(f"{SERVER_URL}/api/license/verify", 
                               json={'license_key': target}, timeout=10)
            data = resp.json()
            if data.get('valid'):
                self.is_valid = True
                self.credits = data.get('credits', 0)
                self.user_id = data.get('user_id', 'User')
                self.license_key = target
                self.save_config()
                return True
        except:
            pass
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
        except:
            pass
        return None

# ==================== STEALTH BROWSER ====================
class StealthBrowser:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.driver = None

    def start(self):
        try:
            # Check if undetected-chromedriver is available
            if core.undetected_available:
                print(f"{Color.CYAN}[*] Using undetected-chromedriver{Color.RESET}")
                return self._start_undetected()
            else:
                print(f"{Color.CYAN}[*] Using standard selenium{Color.RESET}")
                return self._start_standard()
            
        except Exception as e:
            print(f"{Color.RED}[-] Browser Error: {e}{Color.RESET}")
            return False

    def _start_undetected(self):
        """Start with undetected-chromedriver"""
        try:
            import undetected_chromedriver as uc
            
            options = uc.ChromeOptions()
            
            # Anti-detection options
            ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ]
            options.add_argument(f'user-agent={random.choice(ua_list)}')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
            
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=ChromeDriverManager.get_chromedriver_path(),
                version_main=124
            )
            
            return True
            
        except Exception as e:
            print(f"{Color.RED}[-] undetected-chromedriver error: {e}{Color.RESET}")
            # Fallback to standard selenium
            return self._start_standard()

    def _start_standard(self):
        """Start with standard selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            
            chromedriver_path = ChromeDriverManager.get_chromedriver_path()
            if not chromedriver_path:
                print(f"{Color.RED}[-] ChromeDriver not found!{Color.RESET}")
                return False
            
            options = Options()
            
            # Find chromium binary
            chromium_paths = [
                '/data/data/com.termux/files/usr/bin/chromium',
                '/data/data/com.termux/files/usr/bin/chromium-browser',
                '/usr/bin/chromium'
            ]
            for p in chromium_paths:
                if os.path.exists(p):
                    options.binary_location = p
                    break
            
            ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ]
            options.add_argument(f'user-agent={random.choice(ua_list)}')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_setting_values.geolocation": 2,
                "profile.default_content_setting_values.cookies": 1
            }
            options.add_experimental_option("prefs", prefs)
            
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
            
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Stealth JavaScript
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                    window.chrome = { runtime: {} };
                """
            })
            
            return True
            
        except Exception as e:
            print(f"{Color.RED}[-] Standard browser error: {e}{Color.RESET}")
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
        except:
            pass

# ==================== AUTOMATION LOGIC ====================
def custom_automation_logic(driver, data_item):
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select, WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        country_code = DataGenerator.get_country_from_phone(data_item)
        first_name, last_name = DataGenerator.get_random_name(country_code)
        day, month, year = DataGenerator.get_random_dob()
        gender = DataGenerator.get_random_gender()
        password = DataGenerator.get_random_password()
        
        print(f"{Color.CYAN}[*] Name: {first_name} {last_name} ({country_code}){Color.RESET}")
        print(f"{Color.CYAN}[*] DOB: {day}/{month}/{year}{Color.RESET}")
        print(f"{Color.CYAN}[*] Gender: {gender}{Color.RESET}")
        print(f"{Color.CYAN}[*] Password: {password}{Color.RESET}")
        
        driver.get("https://m.facebook.com/reg")
        time.sleep(random.uniform(2, 4))
        
        first_name_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "firstname"))
        )
        first_name_field.send_keys(first_name)
        time.sleep(random.uniform(0.2, 0.5))
        
        driver.find_element(By.NAME, "lastname").send_keys(last_name)
        time.sleep(random.uniform(0.2, 0.5))
        
        Select(driver.find_element(By.NAME, "birthday_day")).select_by_value(str(day))
        time.sleep(random.uniform(0.2, 0.4))
        Select(driver.find_element(By.NAME, "birthday_month")).select_by_value(str(month))
        time.sleep(random.uniform(0.2, 0.4))
        Select(driver.find_element(By.NAME, "birthday_year")).select_by_value(str(year))
        time.sleep(random.uniform(0.2, 0.4))
        
        gender_value = '2' if gender == 'Female' else '1'
        driver.find_element(By.CSS_SELECTOR, f'input[name="sex"][value="{gender_value}"]').click()
        time.sleep(random.uniform(0.3, 0.6))
        
        driver.find_element(By.NAME, "reg_email__").send_keys(data_item)
        time.sleep(random.uniform(0.5, 1.0))
        driver.find_element(By.NAME, "reg_passwd__").send_keys(password)
        time.sleep(random.uniform(0.5, 1.0))
        
        print(f"{Color.CYAN}[*] Clicking Submit...{Color.RESET}")
        submit_button = driver.find_element(By.NAME, "websubmit")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(random.uniform(0.3, 0.6))
        submit_button.click()
        time.sleep(random.uniform(2, 4))
        
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
        global core
        self.core = CoreManager()
        core = self.core
        self.audio = AudioEngine()
        self.core.verify_license()

    def draw_ui(self):
        os.system('clear')
        print(f"""{Color.GOLD}
   ██████╗ ██╗██████╗  ██████╗ ██╗     
   ██╔══██╗██║██╔══██╗██╔═══██╗██║     
   ██████╔╝██║██║  ██║██║   ██║██║     
   ██╔══██╗██║██║  ██║██║   ██║██║     
   ██║  ██║██║██████╔╝╚██████╔╝███████╗
   ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝{Color.RESET}""")
        print(f"            {Color.WHITE}{Color.BOLD}RIDOL FB TOOL {APP_VERSION}{Color.RESET}")
        
        print(f"  {Color.CYAN}┌──────────────────────────────────────────────────┐{Color.RESET}")
        
        # Browser Status - More Detailed
        if self.core.browser_active:
            br_status = f"{Color.GREEN}● Active{Color.RESET}"
        elif self.core.browser_ready:
            br_status = f"{Color.GREEN}● Ready{Color.RESET}"
        else:
            br_status = f"{Color.RED}● Missing{Color.RESET}"
        
        lic_status = f"{Color.GREEN}● Active{Color.RESET}" if self.core.is_valid else f"{Color.RED}● Inactive{Color.RESET}"
        
        # Undetected Status
        if self.core.undetected_available:
            ud_status = f"{Color.GREEN}● Installed{Color.RESET}"
        else:
            ud_status = f"{Color.YELLOW}● Not Installed{Color.RESET}"
        
        try:
            srv_check = requests.get(SERVER_URL, timeout=3)
            srv_status = f"{Color.GREEN}● Online{Color.RESET}" if srv_check.status_code == 200 else f"{Color.RED}● Offline{Color.RESET}"
        except:
            srv_status = f"{Color.RED}● Offline{Color.RESET}"

        print(f"  {Color.CYAN}│{Color.RESET}  {Color.BOLD}Browser   {Color.RESET}: {br_status}     {Color.BOLD}License{Color.RESET} : {lic_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.BOLD}Credits   {Color.RESET}: {Color.GOLD}{self.core.credits}{Color.RESET}     {Color.BOLD}Server {Color.RESET} : {srv_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.BOLD}Undetected{Color.RESET}: {ud_status}")
        print(f"  {Color.CYAN}└──────────────────────────────────────────────────┘{Color.RESET}")
        
        # Browser Status Explanation
        print(f"  {Color.DIM}┌──────────────────────────────────────────────────┐{Color.RESET}")
        if self.core.browser_active:
            print(f"  {Color.DIM}│{Color.RESET}  {Color.GREEN}✅ Browser is ACTIVE and ready to use{Color.RESET}      {Color.DIM}│{Color.RESET}")
        elif self.core.browser_ready:
            print(f"  {Color.DIM}│{Color.RESET}  {Color.YELLOW}⏳ Browser is READY (waiting to start){Color.RESET}   {Color.DIM}│{Color.RESET}")
        else:
            print(f"  {Color.DIM}│{Color.RESET}  {Color.RED}❌ Browser NOT READY - Run Option 4{Color.RESET}       {Color.DIM}│{Color.RESET}")
        
        if self.core.undetected_available:
            print(f"  {Color.DIM}│{Color.RESET}  {Color.GREEN}🔒 Undetected Mode: ON{Color.RESET}                      {Color.DIM}│{Color.RESET}")
        else:
            print(f"  {Color.DIM}│{Color.RESET}  {Color.YELLOW}🔓 Undetected Mode: OFF (using standard){Color.RESET} {Color.DIM}│{Color.RESET}")
        print(f"  {Color.DIM}└──────────────────────────────────────────────────┘{Color.RESET}")

    def run_automation(self):
        if not self.core.is_valid:
            print(f"\n{Color.RED}[!] Verify License First!{Color.RESET}")
            time.sleep(2)
            return
        
        if not self.core.browser_ready:
            print(f"\n{Color.RED}[!] Browser not ready! Run Option 4 first.{Color.RESET}")
            print(f"{Color.YELLOW}[!] ChromeDriver not found in project folder or system{Color.RESET}")
            time.sleep(3)
            return
        
        data_file = os.path.join(self.core.data_dir, 'numbers.txt')
        if not os.path.exists(data_file):
            print(f"\n{Color.RED}[-] numbers.txt not found!{Color.RESET}")
            print(f"{Color.YELLOW}[!] Create numbers.txt in: {self.core.data_dir}{Color.RESET}")
            time.sleep(2)
            return
        
        with open(data_file, 'r') as f:
            items = [l.strip() for l in f if l.strip()]
        
        if not items:
            print(f"\n{Color.RED}[-] numbers.txt is empty!{Color.RESET}")
            time.sleep(2)
            return
        
        print(f"\n{Color.GREEN}[+] Batch Started: {len(items)} items{Color.RESET}")
        self.audio.speak("Starting batch process")
        
        # Set browser active
        self.core.browser_active = True

        for idx, item in enumerate(items, 1):
            if self.core.credits <= 0:
                print(f"\n{Color.RED}[!] Insufficient Credits!{Color.RESET}")
                break
            
            print(f"\n{Color.GOLD}>>> [{idx}/{len(items)}] Task: {item}{Color.RESET}")
            
            proxy = self.core.get_proxy_and_deduct()
            if not proxy:
                print(f"{Color.RED}[✗] Server/Proxy Error!{Color.RESET}")
                continue

            print(f"{Color.CYAN}[*] Proxy: {proxy}{Color.RESET}")
            print(f"{Color.CYAN}[*] Remaining Credits: {self.core.credits}{Color.RESET}")

            browser = StealthBrowser(proxy)
            if browser.start():
                success = custom_automation_logic(browser.driver, item)
                if success:
                    print(f"{Color.GREEN}[✓] Success: {item}{Color.RESET}")
                else:
                    print(f"{Color.RED}[✗] Failed: {item}{Color.RESET}")
                browser.stop()
            else:
                print(f"{Color.RED}[✗] Browser failed to start!{Color.RESET}")
            
            if idx < len(items):
                print(f"{Color.DIM}[*] Waiting 15s before next number...{Color.RESET}")
                for remaining in range(15, 0, -1):
                    if remaining % 5 == 0:
                        print(f"    {remaining}s remaining...")
                    time.sleep(1)

        self.core.browser_active = False
        self.audio.speak("All tasks finished")
        input("\nBatch Complete. Press Enter...")

    def install_dependencies(self):
        """Complete Termux setup with ChromeDriver and undetected-chromedriver"""
        print(f"\n{Color.GOLD}╔══════════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.GOLD}║     INSTALLING ALL DEPENDENCIES          ║{Color.RESET}")
        print(f"{Color.GOLD}║   ChromeDriver + undetected-chromedriver ║{Color.RESET}")
        print(f"{Color.GOLD}╚══════════════════════════════════════════╝{Color.RESET}\n")
        
        # Step 1: Update packages
        print(f"{Color.CYAN}[1/7] Updating Termux packages...{Color.RESET}")
        subprocess.run("pkg update -y", shell=True, check=False)
        subprocess.run("pkg upgrade -y", shell=True, check=False)
        
        # Step 2: Install Chromium
        print(f"{Color.CYAN}[2/7] Installing Chromium...{Color.RESET}")
        subprocess.run("pkg install chromium -y", shell=True, check=False)
        
        # Step 3: Install Python and pip
        print(f"{Color.CYAN}[3/7] Installing Python...{Color.RESET}")
        subprocess.run("pkg install python python-pip -y", shell=True, check=False)
        
        # Step 4: Install espeak
        print(f"{Color.CYAN}[4/7] Installing espeak...{Color.RESET}")
        subprocess.run("pkg install espeak -y", shell=True, check=False)
        
        # Step 5: Check and Download ChromeDriver
        print(f"{Color.CYAN}[5/7] Checking ChromeDriver...{Color.RESET}")
        chromedriver_path = ChromeDriverManager.get_chromedriver_path()
        if chromedriver_path:
            print(f"{Color.GREEN}[✓] ChromeDriver found: {chromedriver_path}{Color.RESET}")
        else:
            print(f"{Color.YELLOW}[!] ChromeDriver not found. Downloading...{Color.RESET}")
            if ChromeDriverManager.download_chromedriver():
                print(f"{Color.GREEN}[✓] ChromeDriver downloaded successfully!{Color.RESET}")
            else:
                print(f"{Color.RED}[✗] ChromeDriver download failed!{Color.RESET}")
        
        # Step 6: Install undetected-chromedriver
        print(f"{Color.CYAN}[6/7] Installing undetected-chromedriver...{Color.RESET}")
        self.core.install_undetected_chromedriver()
        
        # Step 7: Install other Python packages
        print(f"{Color.CYAN}[7/7] Installing other Python packages...{Color.RESET}")
        subprocess.run("pip install selenium requests urllib3 pysocks --upgrade", shell=True, check=False)
        
        # Create directories
        os.makedirs(os.path.join(SCRIPT_DIR, 'data'), exist_ok=True)
        os.makedirs(os.path.join(SCRIPT_DIR, 'logs'), exist_ok=True)
        
        # Verify installation
        print(f"\n{Color.CYAN}[*] Verifying installation...{Color.RESET}")
        
        self.core.browser_ready = self.core.check_browser_ready()
        self.core.undetected_available = self.core.check_undetected_chromedriver()
        
        print(f"\n{Color.GREEN}╔══════════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.GREEN}║     ✅ SETUP COMPLETED SUCCESSFULLY      ║{Color.RESET}")
        
        if self.core.browser_ready:
            print(f"{Color.GREEN}║     ✅ Browser: READY                   ║{Color.RESET}")
        else:
            print(f"{Color.RED}║     ❌ Browser: NOT READY               ║{Color.RESET}")
        
        if self.core.undetected_available:
            print(f"{Color.GREEN}║     ✅ Undetected Mode: ON             ║{Color.RESET}")
        else:
            print(f"{Color.YELLOW}║     ⚠️  Undetected Mode: OFF           ║{Color.RESET}")
        
        print(f"{Color.GREEN}╚══════════════════════════════════════════╝{Color.RESET}\n")
        
        self.audio.speak("Setup completed successfully")
        input("\nPress Enter to continue...")

    def create_sample_numbers_file(self):
        """Create a sample numbers.txt file"""
        sample_path = os.path.join(SCRIPT_DIR, 'numbers.txt')
        if not os.path.exists(sample_path):
            with open(sample_path, 'w') as f:
                f.write("+8801234567890\n")
                f.write("+8801987654321\n")
                f.write("+8801555123456\n")
            print(f"{Color.GREEN}[+] Created sample numbers.txt{Color.RESET}")
        else:
            print(f"{Color.YELLOW}[!] numbers.txt already exists{Color.RESET}")

    def main_loop(self):
        self.audio.speak("Welcome to Ridol FB tool")
        
        # Create sample numbers.txt if not exists
        self.create_sample_numbers_file()
        
        while True:
            self.draw_ui()
            print(f"\n  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}   MAIN MENU - PROXY + AUTO LOGIC       {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}├──────────────────────────────────────────┤{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Start Bot Automation               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Data Folder Setup                  {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[3]{Color.RESET} License Management                 {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[4]{Color.RESET} One-Click Dependencies (Termux)    {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Create Sample numbers.txt           {Color.CYAN}│{Color.RESET}")
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
            elif choice == '5':
                self.create_sample_numbers_file()
                time.sleep(1)
            elif choice == '0':
                self.audio.speak("Goodbye")
                print(f"\n{Color.GREEN}Thanks for using Ridol FB Tool!{Color.RESET}")
                sys.exit()

core = None

if __name__ == '__main__':
    try:
        SaaSApp().main_loop()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}[!] Exiting...{Color.RESET}")
        sys.exit()
    except Exception as e:
        print(f"{Color.RED}[!] Error: {e}{Color.RESET}")
        sys.exit()