#!/usr/bin/env python3
"""
Ridol SaaS Tool v14.0 - Facebook Signup OTP Sender
Residential Proxy with Chrome Extension
Author: Ridol Islam
"""

import os
import sys
import time
import json
import random
import subprocess
import zipfile
import requests
from datetime import datetime
from selenium.webdriver.chrome.service import Service

# ==================== CONFIGURATION ====================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = 'https://ridol-fb-tool.onrender.com' 
APP_VERSION = 'v14.0'

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

# ==================== FIND CHROMEDRIVER ====================
def get_chromedriver_path():
    possible_paths = [
        '/data/data/com.termux/files/usr/bin/chromedriver',
        '/data/data/com.termux/files/usr/lib/chromium/chromedriver',
        '/data/data/com.termux/files/usr/libexec/chromedriver',
        '/usr/bin/chromedriver',
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

CHROMEDRIVER_PATH = get_chromedriver_path()

# ==================== DATA GENERATOR ====================
class DataGenerator:
    """Generate random user data for Facebook registration"""
    
    FIRST_NAMES = {
        'US': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles'],
        'BD': ['Mohammad', 'Abdullah', 'Rafiq', 'Shahid', 'Kamal', 'Jamal', 'Rahim', 'Karim', 'Hasan', 'Ali'],
        'IN': ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Pranav', 'Dhruv', 'Aryan', 'Reyansh'],
        'GB': ['Oliver', 'George', 'Harry', 'Jack', 'Jacob', 'Charlie', 'Thomas', 'James', 'William', 'Muhammad'],
        'XX': ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Hayden', 'Harper']
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

# ==================== PROXY EXTENSION CREATOR ====================
def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, folder_path):
    """Chrome Proxy Authentication Extension তৈরি করা"""
    
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "22.0.0"
    }
    """
    
    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ["blocking"]
    );
    """ % (proxy_host, proxy_port, proxy_user, proxy_pass)
    
    extension_folder = os.path.join(folder_path, 'proxy_extension')
    os.makedirs(extension_folder, exist_ok=True)
    
    with open(os.path.join(extension_folder, 'manifest.json'), 'w') as f:
        f.write(manifest_json)
    with open(os.path.join(extension_folder, 'background.js'), 'w') as f:
        f.write(background_js)
    
    zip_path = os.path.join(folder_path, 'proxy_auth_plugin.zip')
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w') as zp:
        zp.write(os.path.join(extension_folder, 'manifest.json'), 'manifest.json')
        zp.write(os.path.join(extension_folder, 'background.js'), 'background.js')
    
    return extension_folder

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
            resp = requests.post(f"{SERVER_URL}/api/license/verify", json={'license_key': target}, timeout=15)
            data = resp.json()
            if data.get('valid'):
                self.is_valid = True
                self.credits = data.get('credits', 0)
                self.user_id = data.get('user_id', 'User')
                self.license_key = target
                self.save_config()
                print(f"{Color.GREEN}[+] License Active! Credits: {self.credits}{Color.RESET}")
                return True
        except Exception as e:
            print(f"{Color.RED}[-] License verify error: {e}{Color.RESET}")
        return False

    def get_proxy_and_deduct(self):
        """সার্ভার থেকে Residential Proxy নেওয়া"""
        try:
            print(f"{Color.DIM}[*] Requesting proxy from server...{Color.RESET}")
            resp = requests.post(f"{SERVER_URL}/api/proxy/get", json={
                'license_key': self.license_key,
                'country': 'Rand'
            }, timeout=20)
            
            print(f"{Color.DIM}[*] Server response status: {resp.status_code}{Color.RESET}")
            
            if resp.status_code != 200:
                print(f"{Color.RED}[-] Server error: {resp.status_code}{Color.RESET}")
                print(f"{Color.YELLOW}[!] Response: {resp.text[:200]}{Color.RESET}")
                return None
            
            data = resp.json()
            print(f"{Color.DIM}[*] Server response: {data}{Color.RESET}")
            
            if data.get('success'):
                self.credits = data.get('remaining_credits', 0)
                
                raw_user = data.get('user', '')
                if '@' in raw_user:
                    proxy_user = raw_user.split('@')[0]
                else:
                    proxy_user = raw_user
                
                proxy_data = {
                    'ip': data.get('ip'),
                    'port': str(data.get('port')),
                    'user': proxy_user,
                    'pass': data.get('pass', 'Ridol123')
                }
                
                if not proxy_data['ip']:
                    print(f"{Color.RED}[-] No IP in response{Color.RESET}")
                    return None
                
                print(f"{Color.GREEN}[+] Proxy: {proxy_data['user']}@{proxy_data['ip']}:{proxy_data['port']}{Color.RESET}")
                print(f"{Color.CYAN}[+] Credits left: {self.credits}{Color.RESET}")
                return proxy_data
            else:
                error = data.get('error', 'Unknown error')
                print(f"{Color.RED}[-] Server error: {error}{Color.RESET}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"{Color.RED}[-] Request timeout! Server might be down.{Color.RESET}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"{Color.RED}[-] Cannot connect to server!{Color.RESET}")
            print(f"{Color.YELLOW}[!] Server URL: {SERVER_URL}{Color.RESET}")
            return None
        except Exception as e:
            print(f"{Color.RED}[-] Proxy error: {e}{Color.RESET}")
            return None

# ==================== STEALTH BROWSER ====================
class StealthBrowser:
    def __init__(self, proxy_data=None):
        self.proxy_data = proxy_data
        self.driver = None

    def start(self):
        if not CHROMEDRIVER_PATH:
            print(f"{Color.RED}[-] Chromedriver not found!{Color.RESET}")
            return False
            
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--blink-settings=imagesEnabled=false')
            options.add_argument('--disable-web-security')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            
            if self.proxy_data:
                print(f"{Color.CYAN}[*] Creating proxy extension...{Color.RESET}")
                extension_path = create_proxy_auth_extension(
                    self.proxy_data['ip'],
                    self.proxy_data['port'],
                    self.proxy_data['user'],
                    self.proxy_data['pass'],
                    SCRIPT_DIR
                )
                options.add_argument(f'--load-extension={extension_path}')
                print(f"{Color.GREEN}[+] Proxy extension loaded{Color.RESET}")
            
            ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
            ]
            options.add_argument(f'user-agent={random.choice(ua_list)}')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(CHROMEDRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            
            print(f"{Color.GREEN}[+] Browser started{Color.RESET}")
            return True
                
        except Exception as e:
            print(f"{Color.RED}[-] Browser error: {e}{Color.RESET}")
            return False

    def stop(self):
        if self.driver:
            try:
                self.driver.quit()
                print(f"{Color.DIM}[*] Browser closed{Color.RESET}")
            except:
                pass

# ==================== FACEBOOK SIGNUP OTP SENDER ====================
def facebook_signup_otp_sender(driver, phone_number):
    """
    Facebook Signup - OTP Sender
    ফর্ম ফিল করে OTP Send করবে, Submit করবে না
    """
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        
        # 1. দেশ ডিটেক্ট
        country_code = DataGenerator.get_country_from_phone(phone_number)
        print(f"{Color.CYAN}[*] Country detected: {country_code}{Color.RESET}")
        
        # 2. র্যান্ডম ডাটা জেনারেট
        first_name, last_name = DataGenerator.get_random_name(country_code)
        day, month, year = DataGenerator.get_random_dob()
        gender = DataGenerator.get_random_gender()
        password = DataGenerator.get_random_password()
        
        print(f"{Color.CYAN}[*] Name: {first_name} {last_name}{Color.RESET}")
        print(f"{Color.CYAN}[*] DOB: {day}/{month}/{year}{Color.RESET}")
        print(f"{Color.CYAN}[*] Gender: {gender}{Color.RESET}")
        print(f"{Color.CYAN}[*] Phone: {phone_number}{Color.RESET}")
        print(f"{Color.CYAN}[*] Password: {password}{Color.RESET}")
        
        # 3. Facebook Signup Page
        print(f"{Color.CYAN}[*] Opening Facebook Signup...{Color.RESET}")
        driver.get("https://www.facebook.com/reg/")
        time.sleep(3)
        
        # 4. Fill First Name
        try:
            first_name_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "firstname"))
            )
            first_name_field.send_keys(first_name)
            time.sleep(0.5)
            print(f"{Color.CYAN}[*] First name filled{Color.RESET}")
        except:
            print(f"{Color.YELLOW}[!] First name field not found{Color.RESET}")
        
        # 5. Fill Last Name
        try:
            last_name_field = driver.find_element(By.NAME, "lastname")
            last_name_field.send_keys(last_name)
            time.sleep(0.5)
            print(f"{Color.CYAN}[*] Last name filled{Color.RESET}")
        except:
            print(f"{Color.YELLOW}[!] Last name field not found{Color.RESET}")
        
        # 6. Select Day
        try:
            day_select = Select(driver.find_element(By.NAME, "birthday_day"))
            day_select.select_by_value(str(day))
            time.sleep(0.3)
        except:
            pass
        
        # 7. Select Month
        try:
            month_select = Select(driver.find_element(By.NAME, "birthday_month"))
            month_select.select_by_value(str(month))
            time.sleep(0.3)
        except:
            pass
        
        # 8. Select Year
        try:
            year_select = Select(driver.find_element(By.NAME, "birthday_year"))
            year_select.select_by_value(str(year))
            time.sleep(0.3)
        except:
            pass
        
        # 9. Select Gender
        try:
            gender_value = '2' if gender == 'Female' else '1'
            gender_radio = driver.find_element(By.CSS_SELECTOR, f'input[name="sex"][value="{gender_value}"]')
            gender_radio.click()
            time.sleep(0.5)
            print(f"{Color.CYAN}[*] Gender selected{Color.RESET}")
        except:
            print(f"{Color.YELLOW}[!] Gender field not found{Color.RESET}")
        
        # 10. Fill Phone Number
        try:
            phone_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "reg_email__"))
            )
            phone_field.send_keys(phone_number)
            time.sleep(0.5)
            print(f"{Color.CYAN}[*] Phone number filled{Color.RESET}")
        except:
            print(f"{Color.YELLOW}[!] Phone field not found{Color.RESET}")
            return False
        
        # 11. Fill Password
        try:
            password_field = driver.find_element(By.NAME, "reg_passwd__")
            password_field.send_keys(password)
            time.sleep(0.5)
            print(f"{Color.CYAN}[*] Password filled{Color.RESET}")
        except:
            print(f"{Color.YELLOW}[!] Password field not found{Color.RESET}")
        
        # 12. Click Sign Up
        try:
            signup_btn = driver.find_element(By.NAME, "websubmit")
            signup_btn.click()
            time.sleep(3)
            print(f"{Color.GREEN}[+] Signup submitted! OTP sent to: {phone_number}{Color.RESET}")
            return True
        except:
            print(f"{Color.RED}[-] Failed to click Sign Up{Color.RESET}")
            return False
            
    except Exception as e:
        print(f"{Color.RED}[-] Error: {e}{Color.RESET}")
        return False

# ==================== UI & APP CONTROLLER ====================
class SaaSApp:
    def __init__(self):
        self.core = CoreManager()
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
        print(f"         {Color.PINK}Facebook Signup OTP Sender{Color.RESET}")
        
        print(f"  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
        br_status = f"{Color.GREEN}Active{Color.RESET}" if self.core.browser_ready else f"{Color.RED}Missing{Color.RESET}"
        lic_status = f"{Color.GREEN}Active{Color.RESET}" if self.core.is_valid else f"{Color.RED}Inactive{Color.RESET}"
        
        try:
            srv_check = requests.get(SERVER_URL, timeout=5)
            srv_status = f"{Color.GREEN}Online{Color.RESET}" if srv_check.status_code == 200 else f"{Color.RED}Offline{Color.RESET}"
        except: srv_status = f"{Color.RED}Offline{Color.RESET}"

        print(f"  {Color.CYAN}│{Color.RESET}  Browser : {br_status}  | License : {lic_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  Credits : {Color.GOLD}{self.core.credits}{Color.RESET}  | Server  : {srv_status}")
        print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")
        
        if CHROMEDRIVER_PATH:
            print(f"  {Color.DIM}Chromedriver: {CHROMEDRIVER_PATH}{Color.RESET}")

    def run_otp_sender(self):
        if not self.core.is_valid:
            print(f"\n{Color.RED}[!] Verify License First!{Color.RESET}")
            time.sleep(2)
            return
        
        if not CHROMEDRIVER_PATH:
            print(f"\n{Color.RED}[!] Chromedriver not found!{Color.RESET}")
            print(f"{Color.YELLOW}[*] Run: pkg install chromedriver{Color.RESET}")
            time.sleep(3)
            return
        
        data_file = os.path.join(self.core.data_dir, 'numbers.txt')
        if not os.path.exists(data_file):
            print(f"\n{Color.RED}[-] numbers.txt not found!{Color.RESET}")
            time.sleep(2)
            return
        
        with open(data_file, 'r') as f:
            numbers = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        
        if not numbers:
            print(f"\n{Color.RED}[-] No numbers found!{Color.RESET}")
            time.sleep(2)
            return
        
        print(f"\n{Color.GREEN}[+] Starting OTP Sender...{Color.RESET}")
        print(f"{Color.CYAN}[+] Total: {len(numbers)} numbers{Color.RESET}")
        print(f"{Color.YELLOW}[!] Each number costs 1 credit{Color.RESET}")
        print(f"{Color.YELLOW}[!] Proxy: Residential (Chrome Extension){Color.RESET}")
        print("-" * 50)

        success_count = 0
        failed_count = 0
        no_proxy_count = 0
        
        for idx, phone in enumerate(numbers, 1):
            if self.core.credits <= 0:
                print(f"\n{Color.RED}[!] Insufficient Credits!{Color.RESET}")
                break
            
            print(f"\n{Color.GOLD}[{idx}/{len(numbers)}] Processing: {phone}{Color.RESET}")
            
            proxy_data = self.core.get_proxy_and_deduct()
            if not proxy_data:
                print(f"{Color.RED}[✗] No proxy! Credits: {self.core.credits}{Color.RESET}")
                no_proxy_count += 1
                failed_count += 1
                continue

            browser = StealthBrowser(proxy_data)
            if browser.start():
                success = facebook_signup_otp_sender(browser.driver, phone)
                if success:
                    success_count += 1
                    print(f"{Color.GREEN}[✓] OTP sent to: {phone}{Color.RESET}")
                else:
                    failed_count += 1
                    print(f"{Color.RED}[✗] Failed: {phone}{Color.RESET}")
                browser.stop()
            else:
                failed_count += 1
                print(f"{Color.RED}[✗] Browser failed!{Color.RESET}")

        print("\n" + "="*50)
        print(f"{Color.GREEN}COMPLETE{Color.RESET}")
        print("="*50)
        print(f"Total: {len(numbers)}")
        print(f"Success: {Color.GREEN}{success_count}{Color.RESET}")
        print(f"Failed: {Color.RED}{failed_count}{Color.RESET}")
        print(f"No Proxy: {Color.YELLOW}{no_proxy_count}{Color.RESET}")
        print(f"Credits Left: {Color.GOLD}{self.core.credits}{Color.RESET}")
        print("="*50)
        
        input("\nPress Enter to continue...")

    def main_loop(self):
        while True:
            self.draw_ui()
            print(f"\n  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}   MAIN MENU - OTP SENDER                {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}├──────────────────────────────────────────┤{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Start OTP Sender                   {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Data Folder Setup                  {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[3]{Color.RESET} License Management                 {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Install Dependencies               {Color.CYAN}│{Color.RESET}")
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
                print(f"\n{Color.CYAN}[*] Installing Dependencies...{Color.RESET}")
                subprocess.run("pkg update -y && pkg install -y tur-repo python chromium chromedriver && pip install --upgrade pip && pip install selenium requests", shell=True)
                global CHROMEDRIVER_PATH
                CHROMEDRIVER_PATH = get_chromedriver_path()
                if CHROMEDRIVER_PATH:
                    print(f"{Color.GREEN}[+] Found: {CHROMEDRIVER_PATH}{Color.RESET}")
                else:
                    print(f"{Color.RED}[-] Not found! Try: pkg install chromedriver{Color.RESET}")
                input("\nDone. Press Enter...")
            elif choice == '0':
                print(f"\n{Color.GREEN}Goodbye!{Color.RESET}")
                sys.exit()

if __name__ == '__main__':
    try: SaaSApp().main_loop()
    except KeyboardInterrupt: 
        print(f"\n{Color.YELLOW}[!] Interrupted{Color.RESET}")
        sys.exit()