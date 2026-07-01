#!/usr/bin/env python3
"""
Ridol SaaS Tool v15.1 - Facebook Forgot Password OTP Sender
Updated OTP Logic - Multiple Selectors
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
import re
from datetime import datetime
from selenium.webdriver.chrome.service import Service

# ==================== INSTALL OPENPYXL ====================
try:
    import openpyxl
except ImportError:
    print("[*] Installing openpyxl...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'openpyxl'], capture_output=True)
    import openpyxl

# ==================== CONFIGURATION ====================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = 'https://ridol-fb-tool.onrender.com' 
APP_VERSION = 'v15.1'

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

# ==================== COUNTRY NAME TO CODE ====================
COUNTRY_NAME_TO_CODE = {
    'TOGO': 'TG',
    'USA': 'US',
    'UK': 'GB',
    'INDIA': 'IN',
    'BANGLADESH': 'BD',
    'PAKISTAN': 'PK',
    'INDONESIA': 'ID',
    'MALAYSIA': 'MY',
    'SINGAPORE': 'SG',
    'PHILIPPINES': 'PH',
    'THAILAND': 'TH',
    'VIETNAM': 'VN',
    'JAPAN': 'JP',
    'SOUTH KOREA': 'KR',
    'GERMANY': 'DE',
    'FRANCE': 'FR',
    'ITALY': 'IT',
    'RUSSIA': 'RU',
    'BRAZIL': 'BR',
}

def get_country_code_from_name(country_name):
    if not country_name:
        return 'XX'
    country_name = country_name.strip().upper()
    for name, code in COUNTRY_NAME_TO_CODE.items():
        if name in country_name or country_name in name:
            return code
    return 'XX'

def get_country_from_phone(phone_number):
    phone = phone_number.strip().replace('+', '').replace(' ', '').replace('-', '')
    country_codes = {
        '228': 'TG', '1': 'US', '44': 'GB', '91': 'IN', '92': 'PK',
        '880': 'BD', '62': 'ID', '60': 'MY', '65': 'SG', '63': 'PH',
        '66': 'TH', '84': 'VN', '81': 'JP', '82': 'KR', '49': 'DE',
        '33': 'FR', '39': 'IT', '7': 'RU', '55': 'BR'
    }
    for code in sorted(country_codes.keys(), key=len, reverse=True):
        if phone.startswith(code):
            return country_codes[code]
    return 'XX'

# ==================== EXCEL READER ====================
def read_numbers_from_excel(file_path):
    numbers = []
    try:
        if not os.path.exists(file_path):
            print(f"{Color.RED}[-] File not found at path: {file_path}{Color.RESET}")
            return []

        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        
        print(f"{Color.CYAN}[*] Sheet Name: {sheet.title}{Color.RESET}")
        
        current_country = None
        
        for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
            country_val = row[0] if len(row) > 0 else None
            number_val = row[1] if len(row) > 1 else None
            
            if country_val and isinstance(country_val, str):
                temp_country = re.sub(r'\d+', '', country_val).strip()
                if temp_country:
                    current_country = temp_country
            
            if number_val:
                number_str = str(number_val).strip()
                if 'E+' in number_str:
                    number_str = "{:.0f}".format(float(number_val))
                
                clean_number = re.sub(r'[^0-9]', '', number_str)
                
                if len(clean_number) >= 7:
                    if not number_str.startswith('+'):
                        full_number = '+' + clean_number
                    else:
                        full_number = number_str

                    c_code = get_country_from_phone(full_number)
                    if c_code == 'XX' and current_country:
                        c_code = get_country_code_from_name(current_country)

                    numbers.append({
                        'number': full_number,
                        'country': c_code,
                        'country_name': current_country or 'Unknown'
                    })
        
        wb.close()
        print(f"{Color.GREEN}[+] Total numbers found: {len(numbers)}{Color.RESET}")
        return numbers
    except Exception as e:
        print(f"{Color.RED}[-] Excel detailed error: {str(e)}{Color.RESET}")
        import traceback
        traceback.print_exc()
        return []

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

# ==================== FIND EXCEL FILES ====================
def find_excel_files():
    excel_files = []
    search_paths = [
        '/storage/emulated/0/Download/',
        '/storage/emulated/0/Documents/',
        '/storage/emulated/0/',
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.xlsx') or file.endswith('.xls'):
                            if 'number' in file.lower() or 'sheet' in file.lower() or 'my' in file.lower():
                                excel_files.append(os.path.join(root, file))
                    if len(excel_files) >= 5:
                        break
            except:
                pass
            if len(excel_files) >= 5:
                break
    
    return excel_files

# ==================== PROXY EXTENSION CREATOR ====================
def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, folder_path):
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
        self.excel_file = self.config.get('excel_file', '')
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
                'excel_file': self.excel_file
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

    def get_proxy_and_deduct(self, country='Rand'):
        try:
            print(f"{Color.DIM}[*] Requesting proxy for country: {country}{Color.RESET}")
            resp = requests.post(f"{SERVER_URL}/api/proxy/get", json={
                'license_key': self.license_key,
                'country': country
            }, timeout=20)
            
            if resp.status_code != 200:
                print(f"{Color.RED}[-] Server error: {resp.status_code}{Color.RESET}")
                return None
            
            data = resp.json()
            
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
            
            print(f"{Color.CYAN}[*] Initializing Chrome options...{Color.RESET}")
            
            options = Options()
            
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--blink-settings=imagesEnabled=false')
            options.add_argument('--disable-web-security')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
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
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            ]
            options.add_argument(f'user-agent={random.choice(ua_list)}')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            print(f"{Color.CYAN}[*] Starting Chrome driver...{Color.RESET}")
            service = Service(CHROMEDRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            
            print(f"{Color.GREEN}[+] Browser started successfully!{Color.RESET}")
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

# ==================== FORGOT PASSWORD OTP SENDER (UPDATED) ====================
def forgot_password_otp_sender(driver, phone_number):
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        
        print(f"{Color.CYAN}[*] Target: {phone_number}{Color.RESET}")
        
        # ১. ফরগট পাসওয়ার্ড পেজে যাওয়া
        driver.get("https://m.facebook.com/login/identify/")
        time.sleep(2)

        # ২. ইনপুট ফিল্ড খুঁজে নম্বর বসানো
        try:
            phone_xpath = "//input[contains(@name,'email') or contains(@type,'text') or contains(@type,'tel')]"
            input_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, phone_xpath)))
            input_box.clear()
            input_box.send_keys(phone_number)
            print(f"{Color.GREEN}[✓] Phone number entered{Color.RESET}")
        except:
            print(f"{Color.RED}[✗] Phone input box not found!{Color.RESET}")
            return False

        # ৩. প্রথম সার্চ/কন্টিনিউ বাটনে ক্লিক
        search_selectors = [
            "//button[@name='did_submit']",
            "//button[contains(., 'Search')]",
            "//button[contains(., 'Continue')]",
            "//button[@type='submit']",
            "//*[@data-sigil='touchable identify_search_button']"
        ]
        
        clicked = False
        for xpath in search_selectors:
            try:
                btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", btn)
                clicked = True
                print(f"{Color.GREEN}[✓] Search/Continue clicked successfully{Color.RESET}")
                break
            except: continue
        
        if not clicked:
            print(f"{Color.RED}[✗] First button could not be found!{Color.RESET}")
            return False
            
        time.sleep(3)

        # ৪. অ্যাকাউন্ট সিলেক্ট করা (যদি লিস্ট আসে)
        try:
            account_xpath = "//div[contains(@class, 'account')]//a | //ul/li//a | //div[@role='button' and contains(., 'Rid')]"
            accounts = driver.find_elements(By.XPATH, account_xpath)
            if accounts:
                driver.execute_script("arguments[0].click();", accounts[0])
                print(f"{Color.GREEN}[✓] Account selected from list{Color.RESET}")
                time.sleep(2)
        except: pass

        # ৫. SMS অপশনটি খুঁজে সিলেক্ট করা
        print(f"{Color.CYAN}[*] Step: Selecting SMS method...{Color.RESET}")
        sms_selectors = [
            "//div[contains(text(), 'SMS')]",
            "//span[contains(text(), 'SMS')]",
            "//label[contains(., 'SMS')]",
            "//input[@value='sms']",
            "//*[contains(text(), 'code via SMS')]"
        ]
        
        sms_found = False
        for xpath in sms_selectors:
            try:
                sms_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", sms_btn)
                sms_found = True
                print(f"{Color.GREEN}[✓] recovery method: SMS selected{Color.RESET}")
                break
            except: continue

        # ৬. চূড়ান্ত কন্টিনিউ বাটন ক্লিক (OTP ট্র্রিগার করার জন্য)
        final_selectors = [
            "//button[@name='reset_action']",
            "//button[@type='submit' and contains(., 'Continue')]",
            "//button[contains(text(), 'Continue')]",
            "//*[@data-sigil='touchable m_login_continue_button']"
        ]

        sent = False
        for xpath in final_selectors:
            try:
                final_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", final_btn)
                sent = True
                print(f"{Color.GREEN}[+] OTP successfully triggered for {phone_number}{Color.RESET}")
                break
            except: continue

        if sent:
            time.sleep(5)
            return True
        else:
            if "confirm" in driver.current_url or "checkpoint" in driver.current_url or "recovery" in driver.current_url:
                print(f"{Color.GREEN}[+] Success: Redirected to OTP page{Color.RESET}")
                return True
            print(f"{Color.RED}[✗] Final button not found!{Color.RESET}")
            return False
            
    except Exception as e:
        print(f"{Color.RED}[-] Automation Crash: {str(e)}{Color.RESET}")
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
        print(f"         {Color.PINK}Forgot Password OTP Sender (Excel){Color.RESET}")
        
        print(f"  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
        br_status = f"{Color.GREEN}Active{Color.RESET}" if self.core.browser_ready else f"{Color.RED}Missing{Color.RESET}"
        lic_status = f"{Color.GREEN}Active{Color.RESET}" if self.core.is_valid else f"{Color.RED}Inactive{Color.RESET}"
        
        try:
            srv_check = requests.get(SERVER_URL, timeout=5)
            srv_status = f"{Color.GREEN}Online{Color.RESET}" if srv_check.status_code == 200 else f"{Color.RED}Offline{Color.RESET}"
        except: srv_status = f"{Color.RED}Offline{Color.RESET}"

        print(f"  {Color.CYAN}│{Color.RESET}  Browser : {br_status}  | License : {lic_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  Credits : {Color.GOLD}{self.core.credits}{Color.RESET}  | Server  : {srv_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  Excel File : {Color.DIM}{self.core.excel_file or 'Not set'}{Color.RESET}{Color.CYAN}  │{Color.RESET}")
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
        
        if not self.core.excel_file:
            print(f"\n{Color.RED}[-] No Excel file path set!{Color.RESET}")
            print(f"{Color.YELLOW}[*] Please set Excel file path in Data Folder Setup{Color.RESET}")
            time.sleep(3)
            return
        
        if not os.path.exists(self.core.excel_file):
            print(f"\n{Color.RED}[-] Excel file not found: {self.core.excel_file}{Color.RESET}")
            print(f"{Color.YELLOW}[*] Please check the file path{Color.RESET}")
            time.sleep(3)
            return
        
        print(f"{Color.CYAN}[*] Reading numbers from Excel...{Color.RESET}")
        numbers_data = read_numbers_from_excel(self.core.excel_file)
        
        if not numbers_data:
            print(f"\n{Color.RED}[-] No numbers found in Excel!{Color.RESET}")
            time.sleep(2)
            return
        
        print(f"\n{Color.GREEN}[+] Found {len(numbers_data)} numbers in Excel{Color.RESET}")
        
        print(f"\n{Color.GREEN}[+] Starting OTP Sender...{Color.RESET}")
        print(f"{Color.CYAN}[+] Total: {len(numbers_data)} numbers{Color.RESET}")
        print(f"{Color.YELLOW}[!] Each number costs 1 credit{Color.RESET}")
        print("-" * 50)

        success_count = 0
        failed_count = 0
        no_proxy_count = 0
        
        for idx, data in enumerate(numbers_data, 1):
            if self.core.credits <= 0:
                print(f"\n{Color.RED}[!] Insufficient Credits!{Color.RESET}")
                break
            
            phone = data['number']
            country = data['country']
            country_name = data['country_name']
            
            print(f"\n{Color.GOLD}{'='*50}{Color.RESET}")
            print(f"{Color.GOLD}[{idx}/{len(numbers_data)}] Phone: {phone} | Country: {country} ({country_name}){Color.RESET}")
            print(f"{Color.GOLD}{'='*50}{Color.RESET}")
            
            proxy_data = self.core.get_proxy_and_deduct(country)
            if not proxy_data:
                print(f"{Color.RED}[✗] No proxy! Credits: {self.core.credits}{Color.RESET}")
                no_proxy_count += 1
                failed_count += 1
                continue

            browser = StealthBrowser(proxy_data)
            if browser.start():
                success = forgot_password_otp_sender(browser.driver, phone)
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
        print(f"Total: {len(numbers_data)}")
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
                print(f"\n{Color.CYAN}[*] Scanning for Excel files...{Color.RESET}")
                excel_files = find_excel_files()
                
                if excel_files:
                    print(f"\n{Color.GREEN}[+] Found {len(excel_files)} Excel files:{Color.RESET}")
                    for i, f in enumerate(excel_files, 1):
                        print(f"  {Color.CYAN}[{i}]{Color.RESET} {os.path.basename(f)}")
                        print(f"      {Color.DIM}{f}{Color.RESET}")
                    
                    print(f"\n{Color.YELLOW}[0]{Color.RESET} Enter custom path")
                    choice_file = input(f"\n{Color.BOLD} Select file (number): {Color.RESET}").strip()
                    
                    if choice_file == '0':
                        path = input(f"\n{Color.CYAN} Enter Excel file path: {Color.RESET}").strip()
                    else:
                        try:
                            idx = int(choice_file) - 1
                            if 0 <= idx < len(excel_files):
                                path = excel_files[idx]
                            else:
                                print(f"{Color.RED}Invalid selection!{Color.RESET}")
                                time.sleep(1)
                                continue
                        except:
                            print(f"{Color.RED}Invalid input!{Color.RESET}")
                            time.sleep(1)
                            continue
                    
                    if path:
                        path = path.strip('"').strip("'")
                        if os.path.exists(path):
                            self.core.excel_file = path
                            self.core.save_config()
                            print(f"{Color.GREEN}[+] Excel file path saved!{Color.RESET}")
                            print(f"{Color.CYAN}[+] File: {path}{Color.RESET}")
                        else:
                            print(f"{Color.RED}[-] File not found: {path}{Color.RESET}")
                else:
                    print(f"\n{Color.YELLOW}[!] No Excel files found in common locations{Color.RESET}")
                    path = input(f"\n{Color.CYAN} Enter Excel file path manually: {Color.RESET}").strip()
                    if path:
                        path = path.strip('"').strip("'")
                        if os.path.exists(path):
                            self.core.excel_file = path
                            self.core.save_config()
                            print(f"{Color.GREEN}[+] Excel file path saved!{Color.RESET}")
                        else:
                            print(f"{Color.RED}[-] File not found: {path}{Color.RESET}")
                
                time.sleep(2)
            elif choice == '3':
                key = input(f"\n{Color.CYAN} Enter License Key: {Color.RESET}").strip().upper()
                if self.core.verify_license(key): 
                    print(f"{Color.GREEN}Verified! Credits: {self.core.credits}{Color.RESET}")
                else: 
                    print(f"{Color.RED}Invalid!{Color.RESET}")
                time.sleep(2)
            elif choice == '4':
                print(f"\n{Color.CYAN}[*] Installing Dependencies...{Color.RESET}")
                subprocess.run("pkg update -y && pkg install -y tur-repo python chromium chromedriver && pip install --upgrade pip && pip install selenium requests openpyxl", shell=True)
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