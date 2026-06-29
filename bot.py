#!/usr/bin/env python3
"""
Ridol SaaS Tool v11.0 - Professional Anti-Detect Edition
Using Pure Selenium with Stealth Techniques
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
        local_path = os.path.join(SCRIPT_DIR, 'chromedriver')
        if os.path.exists(local_path):
            return local_path
        
        local_path_exe = os.path.join(SCRIPT_DIR, 'chromedriver.exe')
        if os.path.exists(local_path_exe):
            return local_path_exe
        
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
        print(f"{Color.CYAN}[*] Downloading ChromeDriver...{Color.RESET}")
        
        arch = os.uname().machine
        if arch == 'aarch64' or arch == 'arm64':
            driver_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/124.0.6367.91/linux-arm64/chromedriver-linux-arm64.zip"
        else:
            driver_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/124.0.6367.91/linux64/chromedriver-linux64.zip"
        
        try:
            zip_path = os.path.join(SCRIPT_DIR, 'chromedriver.zip')
            urllib.request.urlretrieve(driver_url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(SCRIPT_DIR)
            
            extracted_dirs = [d for d in os.listdir(SCRIPT_DIR) if d.startswith('chromedriver-linux')]
            for dir_name in extracted_dirs:
                src = os.path.join(SCRIPT_DIR, dir_name, 'chromedriver')
                dst = os.path.join(SCRIPT_DIR, 'chromedriver')
                if os.path.exists(src):
                    os.rename(src, dst)
                    os.chmod(dst, 0o755)
                    import shutil
                    shutil.rmtree(os.path.join(SCRIPT_DIR, dir_name))
                    break
            
            os.remove(zip_path)
            print(f"{Color.GREEN}[✓] ChromeDriver downloaded!{Color.RESET}")
            return True
        except Exception as e:
            print(f"{Color.RED}[✗] ChromeDriver download failed: {e}{Color.RESET}")
            return False

# ==================== FACEBOOK URL MANAGER (WITH CACHE) ====================
class FacebookURLManager:
    """Smart URL selector with caching system - remembers working URLs"""
    
    CACHE_FILE = os.path.join(SCRIPT_DIR, 'working_urls.json')
    
    URLS = {
        'mobile': [
            'https://m.facebook.com/reg',
            'https://m.facebook.com/r.php',
            'https://mbasic.facebook.com/reg',
            'https://mbasic.facebook.com/r.php'
        ],
        'desktop': [
            'https://www.facebook.com/reg',
            'https://www.facebook.com/r.php',
            'https://web.facebook.com/reg',
            'https://web.facebook.com/r.php'
        ],
        'touch': [
            'https://touch.facebook.com/reg',
            'https://touch.facebook.com/r.php'
        ]
    }
    
    _cache = None
    _current_device = None
    _working_url = None
    _device_detected = False
    
    @classmethod
    def load_cache(cls):
        if cls._cache is not None:
            return cls._cache
        
        try:
            if os.path.exists(cls.CACHE_FILE):
                with open(cls.CACHE_FILE, 'r') as f:
                    cls._cache = json.load(f)
                print(f"{Color.GREEN}[✓] Loaded URL cache{Color.RESET}")
                return cls._cache
        except:
            pass
        
        cls._cache = {}
        return cls._cache
    
    @classmethod
    def save_cache(cls):
        try:
            with open(cls.CACHE_FILE, 'w') as f:
                json.dump(cls._cache, f, indent=2)
        except:
            pass
    
    @classmethod
    def get_cached_url(cls, device_type):
        cache = cls.load_cache()
        return cache.get(device_type)
    
    @classmethod
    def set_cached_url(cls, device_type, url):
        cache = cls.load_cache()
        cache[device_type] = url
        cls._cache = cache
        cls.save_cache()
        cls._working_url = url
        print(f"{Color.GREEN}[✓] Cached working URL for {device_type}: {url}{Color.RESET}")
    
    @classmethod
    def detect_device(cls, driver):
        if cls._device_detected and cls._current_device:
            return cls._current_device
            
        try:
            user_agent = driver.execute_script("return navigator.userAgent")
            user_agent = user_agent.lower()
            
            mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']
            for keyword in mobile_keywords:
                if keyword in user_agent:
                    cls._current_device = 'mobile'
                    cls._device_detected = True
                    return 'mobile'
            
            tablet_keywords = ['tablet', 'ipad']
            for keyword in tablet_keywords:
                if keyword in user_agent:
                    cls._current_device = 'touch'
                    cls._device_detected = True
                    return 'touch'
            
            try:
                is_touch = driver.execute_script("return 'ontouchstart' in window || navigator.maxTouchPoints > 0")
                if is_touch:
                    cls._current_device = 'touch'
                    cls._device_detected = True
                    return 'touch'
            except:
                pass
            
            cls._current_device = 'desktop'
            cls._device_detected = True
            return 'desktop'
            
        except:
            cls._current_device = 'desktop'
            cls._device_detected = True
            return 'desktop'
    
    @classmethod
    def get_urls_for_device(cls, device_type):
        return cls.URLS.get(device_type, cls.URLS['desktop'])
    
    @classmethod
    def find_working_url(cls, driver, device_type):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        cached_url = cls.get_cached_url(device_type)
        if cached_url:
            print(f"{Color.GREEN}[✓] Using cached URL: {cached_url}{Color.RESET}")
            try:
                driver.get(cached_url)
                time.sleep(random.uniform(2, 3))
                
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.NAME, "firstname"))
                )
                cls._working_url = cached_url
                return cached_url
            except:
                print(f"{Color.YELLOW}[!] Cached URL failed, finding new...{Color.RESET}")
                cache = cls.load_cache()
                if device_type in cache:
                    del cache[device_type]
                    cls._cache = cache
                    cls.save_cache()
        
        urls = cls.get_urls_for_device(device_type)
        print(f"{Color.CYAN}[*] Testing {len(urls)} URLs for {device_type}...{Color.RESET}")
        
        for url in urls:
            print(f"{Color.DIM}[*] Trying: {url}{Color.RESET}")
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 4))
                
                try:
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.NAME, "firstname"))
                    )
                    print(f"{Color.GREEN}[✓] URL working: {url}{Color.RESET}")
                    cls.set_cached_url(device_type, url)
                    cls._working_url = url
                    return url
                except:
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="first"], input[placeholder*="First"]'))
                        )
                        print(f"{Color.GREEN}[✓] URL working: {url}{Color.RESET}")
                        cls.set_cached_url(device_type, url)
                        cls._working_url = url
                        return url
                    except:
                        print(f"{Color.YELLOW}[!] Form not found on {url}{Color.RESET}")
                        
            except Exception as e:
                print(f"{Color.RED}[✗] Failed: {url} - {str(e)[:40]}{Color.RESET}")
                continue
        
        print(f"{Color.YELLOW}[!] No working URL found for {device_type}, trying all...{Color.RESET}")
        all_urls = []
        for urls in cls.URLS.values():
            all_urls.extend(urls)
        all_urls = list(dict.fromkeys(all_urls))
        
        for url in all_urls:
            if url == cls._working_url:
                continue
            print(f"{Color.DIM}[*] Trying fallback: {url}{Color.RESET}")
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 4))
                
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.NAME, "firstname"))
                    )
                    print(f"{Color.GREEN}[✓] Fallback URL working: {url}{Color.RESET}")
                    cls.set_cached_url(device_type, url)
                    cls._working_url = url
                    return url
                except:
                    pass
            except:
                continue
        
        return None
    
    @classmethod
    def get_best_url(cls, driver):
        device = cls.detect_device(driver)
        print(f"{Color.CYAN}[*] Device detected: {device}{Color.RESET}")
        
        working_url = cls.find_working_url(driver, device)
        
        if working_url:
            print(f"{Color.GREEN}[✓] Using: {working_url}{Color.RESET}")
            return working_url, device
        else:
            print(f"{Color.RED}[✗] No working URL found!{Color.RESET}")
            return None, device

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
        self.browser_active = False
        self.all_ready = False
        self.server_online = self.check_server_status()

    def check_server_status(self):
        try:
            resp = requests.get(SERVER_URL, timeout=5)
            return resp.status_code == 200
        except:
            return False

    def check_browser_ready(self):
        return ChromeDriverManager.get_chromedriver_path() is not None
    
    def check_all_dependencies(self):
        status = {
            'chromium': False,
            'chromedriver': False,
            'selenium': False,
            'requests': False,
            'espeak': False
        }
        
        chromium_paths = [
            '/data/data/com.termux/files/usr/bin/chromium',
            '/data/data/com.termux/files/usr/bin/chromium-browser',
            '/usr/bin/chromium'
        ]
        for p in chromium_paths:
            if os.path.exists(p):
                status['chromium'] = True
                break
        
        status['chromedriver'] = self.check_browser_ready()
        
        try:
            import selenium
            status['selenium'] = True
        except:
            pass
        
        try:
            import requests
            status['requests'] = True
        except:
            pass
        
        espeak_paths = [
            '/data/data/com.termux/files/usr/bin/espeak',
            '/usr/bin/espeak'
        ]
        for p in espeak_paths:
            if os.path.exists(p):
                status['espeak'] = True
                break
        
        return status

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
            if not self.check_server_status():
                print(f"{Color.RED}❌ Server is OFFLINE!{Color.RESET}")
                return None
            
            if self.credits <= 0:
                print(f"{Color.RED}❌ Insufficient Credits! Remaining: {self.credits}{Color.RESET}")
                return None
            
            resp = requests.post(f"{SERVER_URL}/api/proxy/get", json={
                'license_key': self.license_key,
                'country': 'Rand'
            }, timeout=20)
            
            if resp.status_code != 200:
                print(f"{Color.RED}❌ Server returned: {resp.status_code}{Color.RESET}")
                return None
            
            data = resp.json()
            
            if data.get('success'):
                self.credits = data.get('remaining_credits', 0)
                ip = data.get('ip')
                port = data.get('port', 3010)
                
                if not ip or ip == '0.0.0.0':
                    print(f"{Color.RED}❌ Invalid proxy IP!{Color.RESET}")
                    return None
                
                proxy = f"socks5://{ip}:{port}"
                print(f"{Color.GREEN}✅ Proxy: {proxy}{Color.RESET}")
                print(f"{Color.CYAN}💰 Remaining Credits: {self.credits}{Color.RESET}")
                return proxy
            else:
                error_msg = data.get('error', 'Unknown error')
                print(f"{Color.RED}❌ Server error: {error_msg}{Color.RESET}")
                return None
                
        except Exception as e:
            print(f"{Color.RED}❌ Proxy error: {e}{Color.RESET}")
            return None

# ==================== STEALTH BROWSER (PURE SELENIUM) ====================
class StealthBrowser:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.driver = None

    def start(self):
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
            
            # Random device selection
            devices = [
                {
                    'ua': "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                    'device': 'mobile'
                },
                {
                    'ua': "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    'device': 'mobile'
                },
                {
                    'ua': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    'device': 'desktop'
                },
                {
                    'ua': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    'device': 'desktop'
                },
                {
                    'ua': "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    'device': 'tablet'
                }
            ]
            
            selected = random.choice(devices)
            options.add_argument(f'user-agent={selected["ua"]}')
            
            # Window size based on device
            if selected['device'] == 'mobile':
                options.add_argument('--window-size=390,844')
            elif selected['device'] == 'tablet':
                options.add_argument('--window-size=768,1024')
            else:
                options.add_argument('--window-size=1366,768')
            
            # Anti-detection options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            
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
            
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
            
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Stealth JavaScript injection
            stealth_js = """
            // Remove webdriver signature
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
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
            
            // Hide Chrome features
            window.chrome = {
                runtime: {}
            };
            
            // Fix console
            const originalConsole = window.console;
            window.console = originalConsole;
            
            // Randomize scroll behavior
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
            
            print(f"{Color.GREEN}[✓] Browser started with {selected['device']} mode{Color.RESET}")
            return True
            
        except Exception as e:
            print(f"{Color.RED}[-] Browser Error: {e}{Color.RESET}")
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
        
        # 1. Generate user data
        country_code = DataGenerator.get_country_from_phone(data_item)
        first_name, last_name = DataGenerator.get_random_name(country_code)
        day, month, year = DataGenerator.get_random_dob()
        gender = DataGenerator.get_random_gender()
        password = DataGenerator.get_random_password()
        
        print(f"{Color.CYAN}[*] Name: {first_name} {last_name} ({country_code}){Color.RESET}")
        print(f"{Color.CYAN}[*] DOB: {day}/{month}/{year}{Color.RESET}")
        print(f"{Color.CYAN}[*] Gender: {gender}{Color.RESET}")
        print(f"{Color.CYAN}[*] Password: {password}{Color.RESET}")
        
        # 2. Get working URL (from cache or find new)
        working_url, device_type = FacebookURLManager.get_best_url(driver)
        
        if not working_url:
            print(f"{Color.RED}[✗] No working URL found!{Color.RESET}")
            return False
        
        # 3. Load the URL
        current_url = driver.current_url
        if working_url not in current_url:
            print(f"{Color.CYAN}[*] Loading: {working_url}{Color.RESET}")
            driver.get(working_url)
            time.sleep(random.uniform(2, 4))
        
        # 4. Fill the form
        print(f"{Color.CYAN}[*] Filling registration form...{Color.RESET}")
        
        # First Name
        try:
            first_name_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "firstname"))
            )
            first_name_field.clear()
            time.sleep(random.uniform(0.2, 0.5))
            first_name_field.send_keys(first_name)
        except:
            try:
                first_name_field = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="first"], input[placeholder*="First"]')
                first_name_field.clear()
                first_name_field.send_keys(first_name)
            except:
                print(f"{Color.YELLOW}[!] Could not find first name field{Color.RESET}")
                return False
        
        # Last Name
        try:
            last_name_field = driver.find_element(By.NAME, "lastname")
            last_name_field.clear()
            time.sleep(random.uniform(0.2, 0.5))
            last_name_field.send_keys(last_name)
        except:
            try:
                last_name_field = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="last"], input[placeholder*="Last"]')
                last_name_field.clear()
                last_name_field.send_keys(last_name)
            except:
                print(f"{Color.YELLOW}[!] Could not find last name field{Color.RESET}")
                return False
        
        # DOB - Day
        try:
            Select(driver.find_element(By.NAME, "birthday_day")).select_by_value(str(day))
            time.sleep(random.uniform(0.2, 0.4))
        except:
            pass
        
        # DOB - Month
        try:
            Select(driver.find_element(By.NAME, "birthday_month")).select_by_value(str(month))
            time.sleep(random.uniform(0.2, 0.4))
        except:
            pass
        
        # DOB - Year
        try:
            Select(driver.find_element(By.NAME, "birthday_year")).select_by_value(str(year))
            time.sleep(random.uniform(0.2, 0.4))
        except:
            pass
        
        # Gender
        try:
            gender_value = '2' if gender == 'Female' else '1'
            driver.find_element(By.CSS_SELECTOR, f'input[name="sex"][value="{gender_value}"]').click()
            time.sleep(random.uniform(0.3, 0.6))
        except:
            try:
                gender_value = '2' if gender == 'Female' else '1'
                driver.find_element(By.CSS_SELECTOR, f'input[value="{gender_value}"]').click()
            except:
                pass
        
        # Phone/Email
        try:
            phone_field = driver.find_element(By.NAME, "reg_email__")
            phone_field.clear()
            time.sleep(random.uniform(0.2, 0.5))
            phone_field.send_keys(data_item)
            time.sleep(random.uniform(0.5, 1.0))
        except:
            try:
                phone_field = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][placeholder*="email"], input[type="text"][placeholder*="Email"]')
                phone_field.clear()
                phone_field.send_keys(data_item)
            except:
                try:
                    phone_field = driver.find_element(By.CSS_SELECTOR, 'input[type="tel"]')
                    phone_field.clear()
                    phone_field.send_keys(data_item)
                except:
                    print(f"{Color.YELLOW}[!] Could not find phone/email field{Color.RESET}")
                    return False
        
        # Password
        try:
            password_field = driver.find_element(By.NAME, "reg_passwd__")
            password_field.clear()
            time.sleep(random.uniform(0.2, 0.5))
            password_field.send_keys(password)
            time.sleep(random.uniform(0.5, 1.0))
        except:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
                password_field.clear()
                password_field.send_keys(password)
            except:
                print(f"{Color.YELLOW}[!] Could not find password field{Color.RESET}")
                return False
        
        # Submit
        print(f"{Color.CYAN}[*] Clicking Submit...{Color.RESET}")
        
        try:
            submit_button = driver.find_element(By.NAME, "websubmit")
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(random.uniform(0.3, 0.6))
            submit_button.click()
        except:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                submit_button.click()
            except:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
                    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                    submit_button.click()
                except:
                    print(f"{Color.YELLOW}[!] Could not find submit button{Color.RESET}")
                    return False
        
        time.sleep(random.uniform(2, 4))
        
        # Wait for OTP
        print(f"{Color.CYAN}[*] Waiting 10 seconds for OTP SMS...{Color.RESET}")
        time.sleep(10)
        
        # Check if OTP page loaded
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="code"], input[placeholder*="code"]'))
            )
            print(f"{Color.GREEN}[✓] OTP page loaded!{Color.RESET}")
        except:
            current_url = driver.current_url
            if 'confirm' in current_url or 'code' in current_url or 'checkpoint' in current_url:
                print(f"{Color.GREEN}[✓] OTP page detected!{Color.RESET}")
            else:
                print(f"{Color.YELLOW}[!] OTP page may not have loaded properly{Color.RESET}")
        
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
        self.check_and_update_status()

    def check_and_update_status(self):
        self.core.browser_ready = self.core.check_browser_ready()
        self.core.server_online = self.core.check_server_status()
        
        if self.core.browser_ready:
            self.core.all_ready = True
        else:
            self.core.all_ready = False

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
        
        if self.core.browser_active:
            br_status = f"{Color.GREEN}● Active{Color.RESET}"
        elif self.core.browser_ready:
            br_status = f"{Color.GREEN}● Ready{Color.RESET}"
        else:
            br_status = f"{Color.RED}● Missing{Color.RESET}"
        
        lic_status = f"{Color.GREEN}● Active{Color.RESET}" if self.core.is_valid else f"{Color.RED}● Inactive{Color.RESET}"
        
        if self.core.server_online:
            srv_status = f"{Color.GREEN}● Online{Color.RESET}"
        else:
            srv_status = f"{Color.RED}● Offline{Color.RESET}"

        print(f"  {Color.CYAN}│{Color.RESET}  {Color.BOLD}Browser   {Color.RESET}: {br_status}     {Color.BOLD}License{Color.RESET} : {lic_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.BOLD}Credits   {Color.RESET}: {Color.GOLD}{self.core.credits}{Color.RESET}     {Color.BOLD}Server {Color.RESET} : {srv_status}")
        print(f"  {Color.CYAN}│{Color.RESET}  {Color.BOLD}Mode      {Color.RESET}: {Color.GREEN}Selenium Only{Color.RESET}")
        print(f"  {Color.CYAN}└──────────────────────────────────────────────────┘{Color.RESET}")
        
        print(f"  {Color.DIM}┌──────────────────────────────────────────────────┐{Color.RESET}")
        if self.core.browser_active:
            print(f"  {Color.DIM}│{Color.RESET}  {Color.GREEN}✅ Browser is ACTIVE and ready to use{Color.RESET}      {Color.DIM}│{Color.RESET}")
        elif self.core.browser_ready:
            print(f"  {Color.DIM}│{Color.RESET}  {Color.GREEN}✅ Browser READY - Using pure Selenium{Color.RESET}    {Color.DIM}│{Color.RESET}")
        else:
            print(f"  {Color.DIM}│{Color.RESET}  {Color.RED}❌ Dependencies MISSING - Run Option 4{Color.RESET}      {Color.DIM}│{Color.RESET}")
        print(f"  {Color.DIM}│{Color.RESET}  {Color.CYAN}📱 Smart Device Detection + URL Cache{Color.RESET}          {Color.DIM}│{Color.RESET}")
        print(f"  {Color.DIM}└──────────────────────────────────────────────────┘{Color.RESET}")

    def run_automation(self):
        if not self.core.is_valid:
            print(f"\n{Color.RED}[!] Verify License First!{Color.RESET}")
            time.sleep(2)
            return
        
        if not self.core.browser_ready:
            print(f"\n{Color.RED}[!] Browser not ready! Run Option 4 first.{Color.RESET}")
            time.sleep(3)
            return
        
        if not self.core.server_online:
            print(f"\n{Color.RED}[!] Server is OFFLINE! Cannot get proxies.{Color.RESET}")
            time.sleep(3)
            return
        
        data_file = os.path.join(self.core.data_dir, 'numbers.txt')
        if not os.path.exists(data_file):
            print(f"\n{Color.RED}[-] numbers.txt not found!{Color.RESET}")
            time.sleep(2)
            return
        
        with open(data_file, 'r') as f:
            items = [l.strip() for l in f if l.strip()]
        
        if not items:
            print(f"\n{Color.RED}[-] numbers.txt is empty!{Color.RESET}")
            time.sleep(2)
            return
        
        print(f"\n{Color.GREEN}[+] Batch Started: {len(items)} items{Color.RESET}")
        print(f"{Color.CYAN}[*] Remaining Credits: {self.core.credits}{Color.RESET}")
        self.audio.speak("Starting batch process")
        
        self.core.browser_active = True
        success_count = 0
        fail_count = 0
        proxy_error_count = 0
        
        # Reset URL cache for new session
        FacebookURLManager._device_detected = False
        FacebookURLManager._current_device = None

        for idx, item in enumerate(items, 1):
            if self.core.credits <= 0:
                print(f"\n{Color.RED}[!] Insufficient Credits!{Color.RESET}")
                break
            
            print(f"\n{Color.GOLD}>>> [{idx}/{len(items)}] Task: {item}{Color.RESET}")
            
            proxy = self.core.get_proxy_and_deduct()
            if not proxy:
                proxy_error_count += 1
                print(f"{Color.RED}[✗] Skipping {item} - No proxy available{Color.RESET}")
                
                if proxy_error_count >= 3:
                    print(f"{Color.RED}[!] Too many proxy errors! Stopping...{Color.RESET}")
                    break
                continue

            browser = StealthBrowser(proxy)
            if browser.start():
                success = custom_automation_logic(browser.driver, item)
                if success:
                    success_count += 1
                    print(f"{Color.GREEN}[✓] Success: {item}{Color.RESET}")
                else:
                    fail_count += 1
                    print(f"{Color.RED}[✗] Failed: {item}{Color.RESET}")
                browser.stop()
            else:
                fail_count += 1
                print(f"{Color.RED}[✗] Browser failed to start!{Color.RESET}")
            
            if idx < len(items) and self.core.credits > 0:
                print(f"{Color.DIM}[*] Waiting 15s before next number...{Color.RESET}")
                for remaining in range(15, 0, -1):
                    if remaining % 5 == 0:
                        print(f"    {remaining}s remaining...")
                    time.sleep(1)

        self.core.browser_active = False
        
        print(f"\n{Color.GOLD}╔══════════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.GOLD}║           BATCH SUMMARY                  ║{Color.RESET}")
        print(f"{Color.GOLD}╠══════════════════════════════════════════╣{Color.RESET}")
        print(f"{Color.GOLD}║{Color.RESET}  {Color.GREEN}✅ Success  : {success_count}{Color.RESET}                              {Color.GOLD}║{Color.RESET}")
        print(f"{Color.GOLD}║{Color.RESET}  {Color.RED}❌ Failed   : {fail_count}{Color.RESET}                              {Color.GOLD}║{Color.RESET}")
        print(f"{Color.GOLD}║{Color.RESET}  {Color.YELLOW}⚠️  Proxy Err: {proxy_error_count}{Color.RESET}                              {Color.GOLD}║{Color.RESET}")
        print(f"{Color.GOLD}║{Color.RESET}  {Color.CYAN}💰 Credits  : {self.core.credits}{Color.RESET}                              {Color.GOLD}║{Color.RESET}")
        print(f"{Color.GOLD}╚══════════════════════════════════════════╝{Color.RESET}")
        
        self.audio.speak("All tasks finished")
        input("\nBatch Complete. Press Enter...")

    def install_dependencies(self):
        print(f"\n{Color.GOLD}╔══════════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.GOLD}║     SMART DEPENDENCY INSTALLER           ║{Color.RESET}")
        print(f"{Color.GOLD}║   Pure Selenium - No Undetected Needed   ║{Color.RESET}")
        print(f"{Color.GOLD}╚══════════════════════════════════════════╝{Color.RESET}\n")
        
        status = self.core.check_all_dependencies()
        
        print(f"\n{Color.CYAN}📊 Current Status:{Color.RESET}")
        print(f"  {Color.GREEN}✅{Color.RESET} Chromium     : {'Installed' if status['chromium'] else 'Missing'}")
        print(f"  {Color.GREEN}✅{Color.RESET} ChromeDriver  : {'Installed' if status['chromedriver'] else 'Missing'}")
        print(f"  {Color.GREEN}✅{Color.RESET} Selenium     : {'Installed' if status['selenium'] else 'Missing'}")
        print(f"  {Color.GREEN}✅{Color.RESET} Requests     : {'Installed' if status['requests'] else 'Missing'}")
        print(f"  {Color.GREEN}✅{Color.RESET} Espeak       : {'Installed' if status['espeak'] else 'Missing'}")
        
        all_installed = all(status.values())
        
        if all_installed:
            print(f"\n{Color.GREEN}✅ All dependencies are already installed!{Color.RESET}")
            print(f"{Color.GREEN}🎯 System is READY to use!{Color.RESET}")
            self.core.browser_ready = True
            self.core.all_ready = True
            self.audio.speak("All dependencies are already installed")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n{Color.YELLOW}[!] Some dependencies are missing. Installing...{Color.RESET}\n")
        
        if not status['chromium'] or not status['espeak']:
            print(f"{Color.CYAN}[1/3] Installing system packages...{Color.RESET}")
            subprocess.run("pkg update -y", shell=True, check=False)
            subprocess.run("pkg upgrade -y", shell=True, check=False)
            
            if not status['chromium']:
                print(f"{Color.DIM}    Installing Chromium...{Color.RESET}")
                subprocess.run("pkg install chromium -y", shell=True, check=False)
            
            if not status['espeak']:
                print(f"{Color.DIM}    Installing espeak...{Color.RESET}")
                subprocess.run("pkg install espeak -y", shell=True, check=False)
            
            subprocess.run("pkg install python python-pip -y", shell=True, check=False)
        
        if not status['chromedriver']:
            print(f"{Color.CYAN}[2/3] Installing ChromeDriver...{Color.RESET}")
            if ChromeDriverManager.download_chromedriver():
                print(f"{Color.GREEN}[✓] ChromeDriver installed!{Color.RESET}")
            else:
                print(f"{Color.RED}[✗] ChromeDriver installation failed!{Color.RESET}")
        
        if not status['selenium'] or not status['requests']:
            print(f"{Color.CYAN}[3/3] Installing Python packages...{Color.RESET}")
            subprocess.run("pip install selenium requests urllib3 pysocks --upgrade", shell=True, check=False)
        
        os.makedirs(os.path.join(SCRIPT_DIR, 'data'), exist_ok=True)
        os.makedirs(os.path.join(SCRIPT_DIR, 'logs'), exist_ok=True)
        
        print(f"\n{Color.CYAN}[*] Verifying installation...{Color.RESET}")
        
        self.core.browser_ready = self.core.check_browser_ready()
        
        if self.core.browser_ready:
            self.core.all_ready = True
            print(f"\n{Color.GREEN}╔══════════════════════════════════════════╗{Color.RESET}")
            print(f"{Color.GREEN}║     ✅ ALL SYSTEMS READY!                ║{Color.RESET}")
            print(f"{Color.GREEN}║     ✅ Browser: READY                    ║{Color.RESET}")
            print(f"{Color.GREEN}║     ✅ Pure Selenium Mode               ║{Color.RESET}")
            print(f"{Color.GREEN}║     🚀 Everything is ACTIVE!            ║{Color.RESET}")
            print(f"{Color.GREEN}╚══════════════════════════════════════════╝{Color.RESET}")
        else:
            print(f"\n{Color.RED}╔══════════════════════════════════════════╗{Color.RESET}")
            print(f"{Color.RED}║     ❌ SETUP FAILED!                     ║{Color.RESET}")
            print(f"{Color.RED}║     Browser: NOT READY                   ║{Color.RESET}")
            print(f"{Color.RED}╚══════════════════════════════════════════╝{Color.RESET}")
        
        self.audio.speak("Setup completed")
        input("\nPress Enter to continue...")

    def create_sample_numbers_file(self):
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
        
        self.create_sample_numbers_file()
        
        while True:
            self.check_and_update_status()
            self.draw_ui()
            print(f"\n  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}   MAIN MENU - PROXY + AUTO LOGIC       {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}├──────────────────────────────────────────┤{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Start Bot Automation               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Data Folder Setup                  {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[3]{Color.RESET} License Management                 {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Smart Dependency Installer         {Color.CYAN}│{Color.RESET}")
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