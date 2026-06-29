#!/usr/bin/env python3
"""
Ridol FB Tool v8.6 - OTP Sender Automation (with Password)
Author: Ridol Islam
License: MIT
"""

import os
import sys
import time
import json
import random
import threading
import subprocess
from datetime import datetime
import re

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], capture_output=True)
    import requests

# ==================== CONFIGURATION ====================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(SCRIPT_DIR, 'sounds')
CUSTOM_SOUND_DIR = os.path.join(SCRIPT_DIR, 'custom_sounds')

# ==================== SERVER CONFIG ====================
LICENSE_SERVER = 'https://ridol-fb-tool.onrender.com'
APP_NAME = 'Ridol FB Tool'
APP_VERSION = 'v8.6'

# ==================== GOOGLE DRIVE CONFIG ====================
GOOGLE_DRIVE_FILE_ID = "1jBDWRKJ0ry9lZUMc8IaVI8zDKvtVzVma"
GOOGLE_DRIVE_DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"
GITHUB_SOUND_URL = "https://raw.githubusercontent.com/ridolislam/Ridol_FB_Tool/main/sounds"

os.makedirs(SOUND_DIR, exist_ok=True)
os.makedirs(CUSTOM_SOUND_DIR, exist_ok=True)

# ==================== CONFIG ====================
FB_CONFIG = {
    'OTP_WAIT_TIMEOUT': 8,
    'BATCH_DELAY': 10,
    'ROTATE_IP': True,
    'ROTATE_DEVICE': True,
}

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
    CLEAR = '\033[2J\033[H'
    
    GOLD = '\033[38;5;214m'
    PINK = '\033[38;5;206m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;141m'
    NEON_GREEN = '\033[38;5;46m'
    NEON_BLUE = '\033[38;5;45m'

# ==================== SERVER API FUNCTIONS ====================

def server_request(endpoint, method='GET', data=None):
    """Make request to server API"""
    url = f"{LICENSE_SERVER}/api/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            return None
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.text else {'success': True}
        return None
    except Exception as e:
        print(f"{Color.RED}[-] Server Error: {e}{Color.RESET}")
        return None

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
        'ID': ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fitri', 'Gilang', 'Hana', 'Indra', 'Joko',
               'Kartika', 'Lestari', 'Maya', 'Nanda', 'Oka', 'Purnama', 'Ratna', 'Sari', 'Tono', 'Utami'],
        'PK': ['Muhammad', 'Ali', 'Ahmed', 'Hassan', 'Usman', 'Omar', 'Zain', 'Hamza', 'Bilal', 'Raza',
               'Ayesha', 'Fatima', 'Zara', 'Hira', 'Noor', 'Sana', 'Kiran', 'Mehak', 'Saima', 'Rabia'],
        'PH': ['Jose', 'Juan', 'Carlos', 'Ramon', 'Pedro', 'Andres', 'Emilio', 'Josefino', 'Ronaldo', 'Ferdinand',
               'Maria', 'Josefa', 'Teresita', 'Rosa', 'Luz', 'Cristina', 'Angelica', 'Marisol', 'Lorna', 'Fe'],
        'MY': ['Ahmad', 'Mohd', 'Abdullah', 'Ali', 'Hassan', 'Zainal', 'Kamarul', 'Azman', 'Razali', 'Idris',
               'Siti', 'Nur', 'Aishah', 'Fatimah', 'Zaharah', 'Rohani', 'Nor', 'Azizah', 'Hamidah', 'Salbiah'],
        'XX': ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Hayden', 'Harper',
               'Emerson', 'Reese', 'Charlie', 'Blake', 'Sage', 'Rowan', 'Logan', 'Peyton', 'Ari', 'Ellis']
    }
    
    LAST_NAMES = {
        'US': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'],
        'BD': ['Rahman', 'Ahmed', 'Islam', 'Hossain', 'Ali', 'Khan', 'Haque', 'Sarkar', 'Mia', 'Pramanik'],
        'IN': ['Sharma', 'Verma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Gandhi', 'Prasad', 'Sinha'],
        'GB': ['Smith', 'Jones', 'Williams', 'Taylor', 'Brown', 'Davies', 'Evans', 'Thomas', 'Johnson', 'Roberts'],
        'ID': ['Siregar', 'Nasution', 'Harahap', 'Lubis', 'Batubara', 'Sinaga', 'Saragih', 'Ginting', 'Manurung', 'Simanjuntak'],
        'PK': ['Khan', 'Malik', 'Akhtar', 'Shah', 'Chaudhry', 'Butt', 'Qureshi', 'Sheikh', 'Abbasi', 'Javed'],
        'PH': ['Santos', 'Reyes', 'Cruz', 'Garcia', 'Martinez', 'Lopez', 'Gonzales', 'Flores', 'Perez', 'Ramos'],
        'MY': ['Abdullah', 'Ali', 'Hassan', 'Ahmad', 'Mohd', 'Ismail', 'Othman', 'Rahman', 'Hussein', 'Yusof'],
        'XX': ['Chen', 'Singh', 'Garcia', 'Wang', 'Perez', 'Nguyen', 'Patel', 'Smith', 'Jones', 'Williams']
    }
    
    @classmethod
    def get_random_name(cls, country_code):
        """Get random first and last name for a country"""
        first_list = cls.FIRST_NAMES.get(country_code, cls.FIRST_NAMES['XX'])
        last_list = cls.LAST_NAMES.get(country_code, cls.LAST_NAMES['XX'])
        return random.choice(first_list), random.choice(last_list)
    
    @classmethod
    def get_random_dob(cls):
        """Generate random date of birth (1992-2005)"""
        day = random.randint(1, 28)
        month = random.randint(1, 12)
        year = random.randint(1992, 2005)
        return day, month, year
    
    @classmethod
    def get_random_gender(cls):
        """Return random gender"""
        return random.choice(['Male', 'Female'])
    
    @classmethod
    def get_random_password(cls):
        """Generate random password (8-12 characters)"""
        length = random.randint(8, 12)
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
        return ''.join(random.choices(chars, k=length))
    
    @classmethod
    def get_full_name(cls, country_code):
        first, last = cls.get_random_name(country_code)
        return f"{first} {last}"

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self):
        self.current_proxy = None
        self.current_country = None
        self.total_credits = 0
        self.user_id = None
        self.license_active = False
        self.proxy_history = []
    
    def _get_country_from_phone(self, phone_number):
        """Get country code from phone number"""
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
    
    def get_proxy_from_server(self, license_key, phone_number):
        """Get SOCKS5 proxy from server (deducts 1 credit)"""
        country_code = self._get_country_from_phone(phone_number)
        print(f"{Color.CYAN}[*] Requesting proxy for country: {country_code}{Color.RESET}")
        
        try:
            response = requests.post(
                f"{LICENSE_SERVER}/api/proxy/get",
                json={
                    "license_key": license_key,
                    "country": country_code
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    ip = data.get('ip')
                    port = data.get('port', 3010)
                    self.total_credits = data.get('remaining_credits', 0)
                    self.current_country = country_code
                    
                    proxy = f"socks5://{ip}:{port}"
                    self.current_proxy = proxy
                    self.proxy_history.append({
                        'phone': phone_number,
                        'proxy': proxy,
                        'country': country_code,
                        'credits_left': self.total_credits
                    })
                    print(f"{Color.GREEN}[+] Got proxy: {ip}:{port}{Color.RESET}")
                    print(f"{Color.CYAN}[+] Credits left: {self.total_credits}{Color.RESET}")
                    return proxy, country_code, self.total_credits
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"{Color.RED}[-] Server error: {error}{Color.RESET}")
                    if "Insufficient credits" in error or "No credits" in error:
                        print(f"{Color.RED}[!] Not enough credits! Please add credits.{Color.RESET}")
                    return None, country_code, 0
            else:
                print(f"{Color.RED}[-] Server returned: {response.status_code}{Color.RESET}")
        except Exception as e:
            print(f"{Color.RED}[-] Proxy error: {e}{Color.RESET}")
        
        return None, country_code, 0
    
    def get_proxy_stats(self):
        return {
            'current': self.current_proxy,
            'country': self.current_country,
            'credits': self.total_credits,
            'history_count': len(self.proxy_history)
        }

# ==================== SOUND FUNCTIONS ====================

def download_sound_from_github(filename):
    url = f"{GITHUB_SOUND_URL}/{filename}"
    filepath = os.path.join(SOUND_DIR, filename)
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code != 200:
            return None
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filepath
    except:
        return None

def download_all_sounds():
    sounds = ['startup.wav', 'click.wav', 'success.wav', 'fail.wav', 'done.wav']
    for sound in sounds:
        filepath = os.path.join(SOUND_DIR, sound)
        if not os.path.exists(filepath):
            download_sound_from_github(sound)

def download_custom_background():
    custom_mp3 = os.path.join(CUSTOM_SOUND_DIR, 'background.mp3')
    if os.path.exists(custom_mp3) and os.path.getsize(custom_mp3) > 0:
        return True
    return False

# ==================== TITLE ====================
class TitleAnimation:
    @staticmethod
    def compact_banner():
        os.system('clear')
        banner = f"""
{Color.CYAN}╔════════════════════════════════════════════════════════════╗{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.GOLD}██████╗ ██╗██████╗  ██████╗ ██╗     ███████╗{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.GOLD}██╔══██╗██║██╔══██╗██╔═══██╗██║     ██╔════╝{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.GOLD}██████╔╝██║██║  ██║██║   ██║██║     █████╗  {Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.GOLD}██╔══██╗██║██║  ██║██║   ██║██║     ██╔══╝  {Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.GOLD}██║  ██║██║██████╔╝╚██████╔╝███████╗███████╗{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.GOLD}╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝╚══════╝{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}           {Color.WHITE}{Color.BOLD}RIDOL FB TOOL {APP_VERSION}{Color.RESET}                    {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}      {Color.DIM}OTP Sender Automation{Color.RESET}                     {Color.CYAN}║{Color.RESET}
{Color.CYAN}╚════════════════════════════════════════════════════════════╝{Color.RESET}
"""
        print(banner)

# ==================== AUDIO ENGINE ====================
class AudioEngine:
    def __init__(self):
        self.sound_dir = SOUND_DIR
        self.voice_available = self._check_voice()
        self.sound_available = self._check_sound()
        os.makedirs(self.sound_dir, exist_ok=True)
        download_all_sounds()
    
    def _check_voice(self):
        try:
            subprocess.run(['espeak', '--help'], capture_output=True, timeout=1)
            return True
        except:
            return False
    
    def _check_sound(self):
        try:
            subprocess.run(['mpv', '--version'], capture_output=True, timeout=1)
            return True
        except:
            try:
                subprocess.run(['play', '--help', '-q'], capture_output=True, timeout=1)
                return True
            except:
                return False
    
    def play_sound(self, filename):
        if not self.sound_available:
            return
        filepath = os.path.join(self.sound_dir, filename)
        if not os.path.exists(filepath):
            download_sound_from_github(filename)
            if not os.path.exists(filepath):
                return
        try:
            subprocess.Popen(['play', '-q', filepath, 'gain', '-3'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    
    def play_startup(self): self.play_sound('startup.wav')
    def play_click(self): self.play_sound('click.wav')
    def play_success(self): self.play_sound('success.wav')
    def play_fail(self): self.play_sound('fail.wav')
    def play_done(self): self.play_sound('done.wav')
    
    def speak(self, text):
        if not self.voice_available:
            return
        try:
            subprocess.run(['espeak', text, '-v', 'en+m3', '-s', '150'],
                         capture_output=True, timeout=3)
        except:
            pass
    
    def speak_welcome(self): self.speak('Ridol FB Tool')
    def speak_success(self): self.speak('OTP sent')
    def speak_fail(self): self.speak('Failed')
    def speak_bot_starting(self): self.speak('Starting bot')
    def speak_bot_complete(self): self.speak('All tasks complete')
    def speak_goodbye(self): self.speak('Goodbye')

# ==================== BROWSER PILOT MANAGER ====================
class BrowserPilotManager:
    def __init__(self):
        self.browser_available = self._check_browser_pilot()
        self.browser = None
        self.browser_started = False
    
    def _check_browser_pilot(self):
        try:
            import termux_browser_pilot
            return True
        except ImportError:
            return False
    
    def _install_browser_pilot(self):
        print(f"{Color.CYAN}[*] Installing termux-browser-pilot...{Color.RESET}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'termux-browser-pilot'], 
                         capture_output=True, timeout=60)
            print(f"{Color.GREEN}[+] Installed successfully{Color.RESET}")
            return True
        except:
            return False
    
    def get_random_user_agent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
        ]
        return random.choice(user_agents)
    
    def start_browser(self, headless=False, proxy=None):
        if not self.browser_available:
            if not self._install_browser_pilot():
                return False
            try:
                import termux_browser_pilot
                self.browser_available = True
            except:
                return False
        try:
            from termux_browser_pilot import Browser
            
            user_agent = self.get_random_user_agent()
            
            if proxy:
                os.environ['http_proxy'] = proxy
                os.environ['https_proxy'] = proxy
                print(f"{Color.CYAN}[*] Using proxy: {proxy}{Color.RESET}")
            else:
                os.environ.pop('http_proxy', None)
                os.environ.pop('https_proxy', None)
            
            self.browser = Browser(
                headless=headless,
                user_agent=user_agent,
                window_size=(1366, 768)
            )
            self.browser_started = True
            print(f"{Color.GREEN}[+] Browser started{Color.RESET}")
            return True
        except Exception as e:
            print(f"{Color.RED}[-] Failed to start browser: {e}{Color.RESET}")
            return False
    
    def goto(self, url):
        if not self.browser_started:
            return False
        try:
            self.browser.goto(url)
            return True
        except:
            return False
    
    def type_text(self, selector, text):
        if not self.browser_started:
            return False
        try:
            self.browser.type(selector, text)
            return True
        except:
            return False
    
    def click(self, selector):
        if not self.browser_started:
            return False
        try:
            self.browser.click(selector)
            return True
        except:
            return False
    
    def select_dropdown(self, selector, value):
        """Select dropdown option by value"""
        if not self.browser_started:
            return False
        try:
            self.browser.select(selector, value)
            return True
        except:
            return False
    
    def close_browser(self):
        self.browser_started = False
        try:
            self.browser.close()
        except:
            pass

# ==================== LICENSE MANAGER ====================
class LicenseManager:
    def __init__(self):
        self.config = load_json(CONFIG_FILE)
        self._verified = False
        self._license_data = None
        self.credits = 0
        self.user_id = None
    
    def save(self): save_json(CONFIG_FILE, self.config)
    def get_license_key(self): return self.config.get('license_key', '')
    def set_license_key(self, key): 
        self.config['license_key'] = key
        self.save()
        self._verified = False
        self._license_data = None
    
    def get_device_serial(self): return self.config.get('device_serial', '')
    def set_device_serial(self, s): self.config['device_serial'] = s; self.save()
    
    def is_verified(self):
        return self._verified
    
    def get_credits(self):
        return self.credits
    
    def get_user_id(self):
        return self.user_id
    
    def verify(self, key):
        """Verify license with server"""
        if self._verified and self._license_data:
            return True, self._license_data
        
        print(f'  {Color.YELLOW}[*] Verifying license...{Color.RESET}')
        result = server_request("license/verify", 'POST', {
            'license_key': key,
            'device_serial': self.get_device_serial()
        })
        
        if result and result.get('valid'):
            self.credits = result.get('credits', 0)
            self.user_id = result.get('user_id', 'Unknown')
            self._verified = True
            self._license_data = result
            print(f'  {Color.GREEN}[+] License Active! Credits: {self.credits} | User: {self.user_id}{Color.RESET}')
            return True, result
        else:
            self._verified = False
            self._license_data = None
            msg = result.get('message', 'Invalid license') if result else 'Server error'
            print(f'  {Color.RED}[-] {msg}{Color.RESET}')
            return False, None

# ==================== UTILITY FUNCTIONS ====================
def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def load_file_lines(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [l.strip() for l in f if l.strip() and not l.startswith('#')]
    except:
        return []

def clear_screen():
    os.system('clear')

def press_enter():
    input(f'\n{Color.DIM}Press Enter to continue...{Color.RESET}')

# ==================== FACEBOOK OTP SENDER ENGINE ====================
class FacebookOTPSender:
    def __init__(self):
        self.is_running = False
        self.stats = {'processed': 0, 'success': 0, 'failed': 0}
        self.browser_manager = BrowserPilotManager()
        self.proxy_manager = ProxyManager()
        self.data_generator = DataGenerator()
        self.audio = None
        self.license_key = None
    
    def _get_proxy(self, phone_number):
        """Get SOCKS5 proxy from server (deducts 1 credit)"""
        return self.proxy_manager.get_proxy_from_server(self.license_key, phone_number)
    
    def _fill_registration_form(self, phone_number, country_code):
        """Fill Facebook registration form with random data"""
        try:
            first_name, last_name = self.data_generator.get_random_name(country_code)
            day, month, year = self.data_generator.get_random_dob()
            gender = self.data_generator.get_random_gender()
            password = self.data_generator.get_random_password()
            
            print(f"{Color.CYAN}  [*] Name: {first_name} {last_name} ({country_code}){Color.RESET}")
            print(f"{Color.CYAN}  [*] DOB: {day}/{month}/{year}{Color.RESET}")
            print(f"{Color.CYAN}  [*] Gender: {gender}{Color.RESET}")
            print(f"{Color.CYAN}  [*] Phone: {phone_number}{Color.RESET}")
            print(f"{Color.CYAN}  [*] Password: {password}{Color.RESET}")
            
            # Fill First Name
            self.browser_manager.type_text('input[name="firstname"]', first_name)
            time.sleep(0.3)
            
            # Fill Last Name
            self.browser_manager.type_text('input[name="lastname"]', last_name)
            time.sleep(0.3)
            
            # Select Day
            self.browser_manager.select_dropdown('select[name="birthday_day"]', str(day))
            time.sleep(0.2)
            
            # Select Month
            self.browser_manager.select_dropdown('select[name="birthday_month"]', str(month))
            time.sleep(0.2)
            
            # Select Year
            self.browser_manager.select_dropdown('select[name="birthday_year"]', str(year))
            time.sleep(0.2)
            
            # Select Gender
            gender_value = '2' if gender == 'Female' else '1'
            self.browser_manager.click(f'input[name="sex"][value="{gender_value}"]')
            time.sleep(0.3)
            
            # Fill Phone Number
            self.browser_manager.type_text('input[name="reg_email__"]', phone_number)
            time.sleep(0.5)
            
            # Fill Password
            self.browser_manager.type_text('input[name="reg_passwd__"]', password)
            time.sleep(0.5)
            
            # Click Submit
            print(f"{Color.CYAN}  [*] Clicking Submit...{Color.RESET}")
            self.browser_manager.click('button[name="websubmit"]')
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"{Color.RED}  [-] Form fill error: {e}{Color.RESET}")
            return False
    
    def _process_number(self, phone_number):
        """Process a single phone number"""
        print(f"\n{Color.CYAN}[+] Processing: {phone_number}{Color.RESET}")
        
        proxy, country_code, credits = self._get_proxy(phone_number)
        
        if not proxy:
            print(f"{Color.RED}[-] No proxy available! Credits: {credits}{Color.RESET}")
            self.stats['failed'] += 1
            if self.audio:
                self.audio.play_fail()
            return False
        
        if not self.browser_manager.start_browser(headless=False, proxy=proxy):
            print(f"{Color.RED}  [-] Failed to start browser{Color.RESET}")
            self.stats['failed'] += 1
            if self.audio:
                self.audio.play_fail()
            return False
        
        try:
            print(f"{Color.CYAN}  [*] Navigating to https://m.facebook.com/reg{Color.RESET}")
            self.browser_manager.goto("https://m.facebook.com/reg")
            time.sleep(2)
            
            if not self._fill_registration_form(phone_number, country_code):
                print(f"{Color.RED}  [-] Failed to fill form{Color.RESET}")
                self.stats['failed'] += 1
                return False
            
            print(f"{Color.CYAN}  [*] Waiting {FB_CONFIG['OTP_WAIT_TIMEOUT']}s for OTP SMS...{Color.RESET}")
            time.sleep(FB_CONFIG['OTP_WAIT_TIMEOUT'])
            
            print(f"{Color.GREEN}  [+] OTP SMS sent successfully!{Color.RESET}")
            self.stats['success'] += 1
            if self.audio:
                self.audio.play_success()
                self.audio.speak_success()
            
            return True
            
        except Exception as e:
            print(f"{Color.RED}  [-] Error: {e}{Color.RESET}")
            self.stats['failed'] += 1
            return False
        finally:
            self.browser_manager.close_browser()
            print(f"{Color.DIM}  [*] Browser closed{Color.RESET}")
    
    def start_batch(self, numbers):
        """Start batch processing"""
        if not numbers:
            print(f"{Color.RED}[-] No numbers found{Color.RESET}")
            return
        
        print(f"\n{Color.GREEN}[+] Starting OTP Sender Automation{Color.RESET}")
        print(f"{Color.CYAN}[+] Total: {len(numbers)} numbers{Color.RESET}")
        print(f"{Color.CYAN}[+] Delay: {FB_CONFIG['BATCH_DELAY']}s between numbers{Color.RESET}")
        print(f"{Color.YELLOW}[!] Each number costs 1 credit{Color.RESET}")
        print("-" * 50)
        
        self.is_running = True
        
        for idx, phone in enumerate(numbers, 1):
            if not self.is_running:
                break
            
            print(f"\n{Color.GOLD}[{idx}/{len(numbers)}]{Color.RESET}")
            self._process_number(phone)
            self.stats['processed'] += 1
            
            if idx < len(numbers) and self.is_running:
                print(f"{Color.DIM}[*] Waiting {FB_CONFIG['BATCH_DELAY']}s...{Color.RESET}")
                for remaining in range(FB_CONFIG['BATCH_DELAY'], 0, -1):
                    if not self.is_running:
                        break
                    if remaining % 5 == 0:
                        print(f"    {remaining}s remaining...")
                    time.sleep(1)
        
        print("\n" + "="*50)
        print(f"{Color.GREEN}BATCH PROCESSING COMPLETE{Color.RESET}")
        print("="*50)
        print(f"Total Processed: {self.stats['processed']}")
        print(f"Success: {Color.GREEN}{self.stats['success']}{Color.RESET}")
        print(f"Failed: {Color.RED}{self.stats['failed']}{Color.RESET}")
        print(f"Credits Used: {Color.CYAN}{self.stats['processed']}{Color.RESET}")
        print("="*50)
        
        if self.audio:
            self.audio.play_done()
            self.audio.speak_bot_complete()
        
        self.is_running = False
    
    def stop(self):
        self.is_running = False
        self.browser_manager.close_browser()
        if self.audio:
            self.audio.speak_fail()

# ==================== MAIN MENU ====================
class MainMenu:
    def __init__(self):
        self.browser_manager = BrowserPilotManager()
        self.proxy_manager = ProxyManager()
        self.license = LicenseManager()
        self.audio = AudioEngine()
        self.bot = None
        self.config = load_json(CONFIG_FILE)
        self.data_dir = self.config.get('data_dir', '/storage/emulated/0/Download/Ridol FB Tool')
        self.bot_running = False
    
    def get_server_status(self):
        try:
            response = requests.get(f"{LICENSE_SERVER}/", timeout=5)
            if response.status_code == 200:
                return "Online", Color.GREEN
            return "Offline", Color.RED
        except:
            return "Offline", Color.RED
    
    def show_header(self):
        clear_screen()
        TitleAnimation.compact_banner()
        
        server_status, server_color = self.get_server_status()
        license_status = "Active ✓" if self.license.is_verified() else "Inactive"
        license_color = Color.GREEN if self.license.is_verified() else Color.RED
        credits = self.license.get_credits() if self.license.is_verified() else 0
        user_id = self.license.get_user_id() or "N/A"
        
        print(f' {Color.CYAN}╔════════════════════════════════════════════════════════════╗{Color.RESET}')
        print(f' {Color.CYAN}║{Color.RESET}  {Color.WHITE}License:{Color.RESET} {license_color}{license_status}{Color.RESET}  {Color.WHITE}Credits:{Color.RESET} {Color.GOLD}{credits}{Color.RESET}  {Color.WHITE}User:{Color.RESET} {Color.CYAN}{user_id}{Color.RESET}  {Color.WHITE}Server:{Color.RESET} {server_color}{server_status}{Color.RESET}  {Color.CYAN}║{Color.RESET}')
        print(f' {Color.CYAN}╚════════════════════════════════════════════════════════════╝{Color.RESET}')
        print()
    
    def welcome_screen(self):
        clear_screen()
        TitleAnimation.compact_banner()
        self.audio.play_startup()
        threading.Thread(target=self.audio.speak_welcome, daemon=True).start()
        time.sleep(0.5)
        clear_screen()
        TitleAnimation.compact_banner()
        time.sleep(0.3)
    
    def check_stop_input(self):
        while self.bot_running:
            try:
                if sys.stdin.isatty():
                    inp = sys.stdin.read(1)
                    if inp == '0':
                        print(f"\n\n{Color.YELLOW}[!] Stopping...{Color.RESET}")
                        self.bot_running = False
                        if self.bot:
                            self.bot.stop()
                        break
            except:
                pass
            time.sleep(0.5)
    
    def menu_main(self):
        self.welcome_screen()
        while True:
            self.show_header()
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}MAIN MENU{Color.RESET}{Color.CYAN}                                      ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Setup                         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Start Bot                      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Status                         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Proxy History                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[5]{Color.RESET} License Management             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[6]{Color.RESET} Audio Settings                 {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[7]{Color.RESET} Help                           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1': self.menu_setup()
            elif choice == '2': self.menu_start_bot()
            elif choice == '3': self.menu_status()
            elif choice == '4': self.menu_proxy_history()
            elif choice == '5': self.menu_license()
            elif choice == '6': self.menu_audio()
            elif choice == '7': self.menu_help()
            elif choice == '0': self.menu_exit(); break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_setup(self):
        while True:
            self.show_header()
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}SETUP{Color.RESET}{Color.CYAN}                                       ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Install Browser Pilot            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Set License Key                 {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Set Data Folder                 {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Create Required Files           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                self.browser_manager._install_browser_pilot()
                press_enter()
            elif choice == '2':
                key = input(f'  {Color.CYAN}Enter license key: {Color.RESET}').strip()
                if key:
                    self.license.set_license_key(key)
                    self.license.verify(key)
                press_enter()
            elif choice == '3':
                path = input(f'  {Color.CYAN}Enter data folder path: {Color.RESET}').strip()
                if path:
                    self.data_dir = path
                    self.config['data_dir'] = path
                    save_json(CONFIG_FILE, self.config)
                press_enter()
            elif choice == '4':
                os.makedirs(self.data_dir, exist_ok=True)
                for fname in ['numbers.txt']:
                    fpath = os.path.join(self.data_dir, fname)
                    if not os.path.exists(fpath):
                        with open(fpath, 'w') as f:
                            f.write(f'# {fname} - Add phone numbers here\n')
                print(f'  {Color.GREEN}[+] Files created{Color.RESET}')
                press_enter()
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_start_bot(self):
        self.show_header()
        folder_path = self.data_dir
        folder_exists = os.path.exists(folder_path)
        
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}START BOT{Color.RESET}{Color.CYAN}                                     ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Numbers: {len(load_file_lines(os.path.join(self.data_dir, "numbers.txt")))}                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.DIM}{"Active" if self.license.is_verified() else "Not set"}{Color.RESET}{Color.CYAN}         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Credits: {Color.DIM}{self.license.get_credits() if self.license.is_verified() else 0}{Color.RESET}{Color.CYAN}                    ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Folder: {Color.DIM}{"✓ Exists" if folder_exists else "✗ Not found"}{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        
        if not folder_exists:
            print(f'\n{Color.RED}[-] Data folder not found!{Color.RESET}')
            press_enter()
            return
        if not self.license.is_verified():
            print(f'\n{Color.RED}[-] License not verified!{Color.RESET}')
            press_enter()
            return
        if self.license.get_credits() <= 0:
            print(f'\n{Color.RED}[-] No credits remaining!{Color.RESET}')
            press_enter()
            return
        if not self.browser_manager.browser_available:
            print(f'\n{Color.RED}[-] Browser Pilot not installed!{Color.RESET}')
            press_enter()
            return
        
        print(f'\n{Color.YELLOW}[!] Press 0 to stop{Color.RESET}')
        
        self.bot_running = True
        stop_thread = threading.Thread(target=self.check_stop_input, daemon=True)
        stop_thread.start()
        
        numbers = load_file_lines(os.path.join(self.data_dir, 'numbers.txt'))
        
        self.bot = FacebookOTPSender()
        self.bot.audio = self.audio
        self.bot.license_key = self.license.get_license_key()
        self.bot.start_batch(numbers)
        
        self.bot_running = False
        time.sleep(1)
        print(f'\n{Color.GREEN}[+] Returned to menu{Color.RESET}')
        press_enter()
    
    def menu_status(self):
        self.show_header()
        proxy_stats = self.proxy_manager.get_proxy_stats()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}STATUS{Color.RESET}{Color.CYAN}                                      ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Browser: {Color.WHITE}{"Installed" if self.browser_manager.browser_available else "Not installed"}{Color.RESET}{Color.CYAN}  ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.WHITE}{"Active" if self.license.is_verified() else "Inactive"}{Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Credits: {Color.WHITE}{self.license.get_credits() if self.license.is_verified() else 0}{Color.RESET}{Color.CYAN}                    ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  User ID: {Color.WHITE}{self.license.get_user_id() or "N/A"}{Color.RESET}{Color.CYAN}                 ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Server: {Color.WHITE}{self.get_server_status()[0]}{Color.RESET}{Color.CYAN}                            ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Data Dir: {Color.WHITE}{self.data_dir}{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Proxy History: {Color.WHITE}{proxy_stats['history_count']}{Color.RESET}{Color.CYAN}                    ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        press_enter()
    
    def menu_proxy_history(self):
        self.show_header()
        history = self.proxy_manager.proxy_history[-10:] if self.proxy_manager.proxy_history else []
        
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}PROXY HISTORY{Color.RESET}{Color.CYAN}                               ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}''')
        
        if history:
            for item in history:
                print(f' {Color.CYAN}║{Color.RESET}  {Color.DIM}{item["phone"]}{Color.RESET} → {Color.GREEN}{item["country"]}{Color.RESET} | Credits: {Color.GOLD}{item["credits_left"]}{Color.RESET}  {Color.CYAN}║{Color.RESET}')
        else:
            print(f' {Color.CYAN}║{Color.RESET}  {Color.DIM}No proxy history yet{Color.RESET}                       {Color.CYAN}║{Color.RESET}')
        
        print(f''' {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        press_enter()
    
    def menu_license(self):
        while True:
            self.show_header()
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}LICENSE MANAGEMENT{Color.RESET}{Color.CYAN}                           ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} View Current License             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Enter New License Key            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Verify License (Server)          {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Register Device (Server)         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[5]{Color.RESET} Check Server Status              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                key = self.license.get_license_key()
                serial = self.license.get_device_serial()
                print(f'\n  {Color.CYAN}License Key: {key if key else "None"}{Color.RESET}')
                print(f'  {Color.CYAN}Device Serial: {serial if serial else "None"}{Color.RESET}')
                if self.license.is_verified():
                    data = self.license.get_verified_data()
                    print(f'  {Color.GREEN}[+] License Verified! Credits: {data.get("credits", "N/A")}{Color.RESET}')
                press_enter()
            elif choice == '2':
                key = input(f'  {Color.CYAN}Enter license key: {Color.RESET}').strip()
                if key:
                    self.license.set_license_key(key)
                    print(f'  {Color.GREEN}[+] License key saved{Color.RESET}')
                press_enter()
            elif choice == '3':
                key = self.license.get_license_key()
                if not key:
                    key = input(f'  {Color.CYAN}Enter license key: {Color.RESET}').strip()
                if key:
                    valid, data = self.license.verify(key)
                    if valid:
                        self.audio.speak_license_verified()
                        print(f'  {Color.GREEN}[+] License verified successfully!{Color.RESET}')
                press_enter()
            elif choice == '4':
                serial = input(f'  {Color.CYAN}Enter device serial: {Color.RESET}').strip()
                if serial:
                    self.license.register_device(serial)
                press_enter()
            elif choice == '5':
                try:
                    result = server_request("status", 'GET')
                    if result:
                        print(f'\n  {Color.GREEN}[+] Server Status:{Color.RESET}')
                        print(f'    Database: {result.get("database", "N/A")}')
                        print(f'    Licenses: {result.get("license_count", 0)}')
                        print(f'    Devices: {result.get("device_count", 0)}')
                    else:
                        print(f'\n  {Color.RED}[-] Server not reachable{Color.RESET}')
                except Exception as e:
                    print(f'\n  {Color.RED}[-] Error: {e}{Color.RESET}')
                press_enter()
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_audio(self):
        while True:
            self.show_header()
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}AUDIO SETTINGS{Color.RESET}{Color.CYAN}                                ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Test Sound Effects              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Test Voice Feedback             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Toggle Background Audio         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Audio Status                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[5]{Color.RESET} Re-download Sounds              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                print(f'\n  {Color.CYAN}Testing sounds...{Color.RESET}')
                self.audio.play_click()
                time.sleep(0.5)
                self.audio.play_success()
                time.sleep(0.5)
                self.audio.play_fail()
                time.sleep(0.5)
                self.audio.play_done()
                press_enter()
            elif choice == '2':
                self.audio.speak('This is a voice test message', 'high')
                print(f'  {Color.GREEN}[+] Voice test completed{Color.RESET}')
                press_enter()
            elif choice == '3':
                if self.audio.bg_playing:
                    self.audio.stop_background_sound()
                    print(f'  {Color.YELLOW}[!] Background audio stopped{Color.RESET}')
                else:
                    self.audio.play_background()
                    print(f'  {Color.GREEN}[+] Background audio started{Color.RESET}')
                press_enter()
            elif choice == '4':
                print(f'\n{self.audio.get_status()}')
                press_enter()
            elif choice == '5':
                print(f'\n  {Color.CYAN}Re-downloading all sounds...{Color.RESET}')
                self.audio.stop_background_sound()
                for f in os.listdir(self.audio.sound_dir):
                    if f.endswith(('.wav', '.mp3', '.ogg')):
                        os.remove(os.path.join(self.audio.sound_dir, f))
                for f in os.listdir(self.audio.custom_sound_dir):
                    if f.endswith(('.wav', '.mp3', '.ogg')):
                        os.remove(os.path.join(self.audio.custom_sound_dir, f))
                download_all_sounds()
                download_custom_background()
                self.audio.play_background()
                print(f'  {Color.GREEN}[+] Sounds re-downloaded!{Color.RESET}')
                press_enter()
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_help(self):
        self.show_header()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}HELP{Color.RESET}{Color.CYAN}                                        ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [?] {Color.WHITE}How to Use{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  1. Install Browser Pilot (Setup -> 1)            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  2. Set License Key (Setup -> 2)                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  3. Add phone numbers to numbers.txt              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  4. Start Bot (Main Menu -> 2)                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  5. Press 0 to stop bot anytime                   {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [#] {Color.WHITE}Features{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - SOCKS5 Proxy Rotation                         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Auto Name + DOB + Gender Generation           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Auto Password Generation                      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - OTP SMS Sender                                {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - 1 Credit per number                           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - 10s delay between numbers                     {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Live Status Bar                               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        press_enter()
    
    def menu_exit(self):
        if self.bot_running:
            self.bot_running = False
            if self.bot:
                self.bot.stop()
        threading.Thread(target=self.audio.speak_goodbye, daemon=True).start()
        time.sleep(0.5)
        print(f'\n{Color.GREEN}Goodbye!{Color.RESET}')
        sys.exit(0)

# ==================== MAIN ====================
if __name__ == '__main__':
    try:
        download_all_sounds()
        time.sleep(0.5)
        menu = MainMenu()
        menu.menu_main()
    except KeyboardInterrupt:
        print(f'\n\n{Color.YELLOW}[!] Interrupted{Color.RESET}')
        sys.exit(0)
    except Exception as e:
        print(f'\n{Color.RED}[-] Error: {e}{Color.RESET}')
        sys.exit(1)