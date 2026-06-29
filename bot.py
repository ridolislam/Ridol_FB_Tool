#!/usr/bin/env python3
"""
Ridol FB Tool v6.5 - Proxy Rotation & Auto Name Generation
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
LICENSE_SERVER = 'https://ridol-fb-tool.onrender.com'
APP_NAME = 'Ridol FB Tool'
APP_VERSION = 'v6.5'

# ==================== PROXY CONFIG ====================
PROXY_SOURCES = {
    '9proxy': 'https://api.9proxy.com/get?api_key={api_key}&format=json',
    'webshare': 'https://api.webshare.io/v2/proxy/list/',
    'proxy_scrape': 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all'
}
PROXY_API_KEY = os.environ.get('PROXY_API_KEY', '')
PROXY_COUNTRY_MAP = {}

# ==================== GOOGLE DRIVE CONFIG ====================
GOOGLE_DRIVE_FILE_ID = "1jBDWRKJ0ry9lZUMc8IaVI8zDKvtVzVma"
GOOGLE_DRIVE_DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"

GITHUB_SOUND_URL = "https://raw.githubusercontent.com/ridolislam/Ridol_FB_Tool/main/sounds"

os.makedirs(SOUND_DIR, exist_ok=True)
os.makedirs(CUSTOM_SOUND_DIR, exist_ok=True)

# ==================== FACEBOOK AUTOMATION CONFIG ====================
FB_CONFIG = {
    'MAX_OTP_RETRIES': 3,
    'OTP_RETRY_DELAY': 30,
    'OTP_WAIT_TIMEOUT': 60,
    'ROTATE_IP': True,
    'ROTATE_DEVICE': True,
    'BATCH_DELAY_MIN': 45,
    'BATCH_DELAY_MAX': 90,
    'UI_ELEMENTS': {
        'phone_input': 'input[name="phone_number"]',
        'next_button': 'button[type="submit"]',
        'otp_input': 'input[name="otp"]',
        'otp_submit': 'button[type="submit"]',
        'fullname_input': 'input[name="full_name"]',
        'birthday_input': 'input[name="birthday"]',
        'gender_select': 'select[name="gender"]',
        'password_input': 'input[name="password"]',
        'signup_btn': 'button[type="submit"]',
    }
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
    url = f"{LICENSE_SERVER}/api/v1/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=15)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=15)
        else:
            return None
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.text else {'success': True}
        return None
    except Exception as e:
        print(f"{Color.RED}[-] Server Error: {e}{Color.RESET}")
        return None

def verify_license(key, device_serial):
    """Verify license using server"""
    result = server_request("license/verify", 'POST', {
        'license_key': key,
        'device_serial': device_serial
    })
    if result:
        return result
    return {'valid': False, 'message': 'Server error'}

def register_device(device_serial, license_key):
    """Register device with server"""
    result = server_request("device/register", 'POST', {
        'device_serial': device_serial,
        'license_key': license_key
    })
    if result:
        return result
    return {'success': False, 'message': 'Server error'}

# ==================== NAME GENERATOR ====================
class NameGenerator:
    """Generate local names based on country code"""
    
    NAMES_DATABASE = {
        'ID': {
            'first': ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fitri', 'Gilang', 'Hana', 'Indra', 'Joko',
                      'Kartika', 'Lestari', 'Maya', 'Nanda', 'Oka', 'Purnama', 'Ratna', 'Sari', 'Tono', 'Utami',
                      'Wahyu', 'Yuni', 'Zahra', 'Agung', 'Bayu', 'Cahya', 'Dian', 'Eka', 'Fajar', 'Gita',
                      'Hendra', 'Intan', 'Jaya', 'Kusuma', 'Lina', 'Mega', 'Nova', 'Oktaviani', 'Putri', 'Rina'],
            'last': ['Siregar', 'Nasution', 'Harahap', 'Lubis', 'Batubara', 'Sinaga', 'Saragih', 'Ginting',
                     'Manurung', 'Simanjuntak', 'Situmorang', 'Sihombing', 'Hutagalung', 'Simatupang', 'Tambunan',
                     'Tampubolon', 'Silalahi', 'Panggabean', 'Simarmata', 'Sibarani', 'Hutapea', 'Sianturi',
                     'Hasibuan', 'Rambe', 'Daulay', 'Rangkuti', 'Nasution']
        },
        'US': {
            'first': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles',
                      'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth', 'Susan', 'Jessica', 'Sarah', 'Karen',
                      'Daniel', 'Matthew', 'Christopher', 'Andrew', 'Joshua', 'Ashley', 'Amanda', 'Melissa', 'Stephanie', 'Nicole'],
            'last': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                     'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee']
        },
        'GB': {
            'first': ['Oliver', 'George', 'Harry', 'Jack', 'Jacob', 'Charlie', 'Thomas', 'James', 'William', 'Muhammad',
                      'Amelia', 'Olivia', 'Isla', 'Emily', 'Poppy', 'Ava', 'Isabella', 'Jessica', 'Lily', 'Sophie'],
            'last': ['Smith', 'Jones', 'Williams', 'Taylor', 'Brown', 'Davies', 'Evans', 'Thomas', 'Johnson', 'Roberts',
                     'Walker', 'Wright', 'Robinson', 'Thompson', 'White', 'Hughes', 'Edwards', 'Green', 'Lewis', 'Wood']
        },
        'IN': {
            'first': ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Pranav', 'Dhruv', 'Aryan', 'Reyansh',
                      'Aanya', 'Ananya', 'Diya', 'Aadhya', 'Myra', 'Sara', 'Ishaan', 'Anika', 'Aarohi', 'Advik'],
            'last': ['Sharma', 'Verma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Gandhi', 'Prasad', 'Sinha',
                     'Pandey', 'Tiwari', 'Chaudhary', 'Srivastava', 'Roy', 'Nair', 'Reddy', 'Rao', 'Mishra', 'Trivedi']
        },
        'BD': {
            'first': ['Mohammad', 'Abdullah', 'Rafiq', 'Shahid', 'Kamal', 'Jamal', 'Rahim', 'Karim', 'Hasan', 'Ali',
                      'Fatima', 'Ayesha', 'Nadia', 'Taslima', 'Rokeya', 'Shirin', 'Nasrin', 'Jahan', 'Morshed', 'Rashed'],
            'last': ['Rahman', 'Ahmed', 'Islam', 'Hossain', 'Ali', 'Khan', 'Haque', 'Sarkar', 'Mia', 'Pramanik',
                     'Chowdhury', 'Begum', 'Shah', 'Siddiqui', 'Zaman', 'Mollah', 'Hasan', 'Uddin', 'Faruque', 'Rashid']
        },
        'PK': {
            'first': ['Muhammad', 'Ali', 'Ahmed', 'Hassan', 'Usman', 'Omar', 'Zain', 'Hamza', 'Bilal', 'Raza',
                      'Ayesha', 'Fatima', 'Zara', 'Hira', 'Noor', 'Sana', 'Kiran', 'Mehak', 'Saima', 'Rabia'],
            'last': ['Khan', 'Malik', 'Akhtar', 'Shah', 'Chaudhry', 'Butt', 'Qureshi', 'Sheikh', 'Abbasi', 'Javed',
                     'Rana', 'Iqbal', 'Rehman', 'Gul', 'Haq', 'Nazir', 'Saeed', 'Yousaf', 'Afzal', 'Aslam']
        },
        'PH': {
            'first': ['Jose', 'Juan', 'Carlos', 'Ramon', 'Pedro', 'Andres', 'Emilio', 'Josefino', 'Ronaldo', 'Ferdinand',
                      'Maria', 'Josefa', 'Teresita', 'Rosa', 'Luz', 'Cristina', 'Angelica', 'Marisol', 'Lorna', 'Fe'],
            'last': ['Santos', 'Reyes', 'Cruz', 'Garcia', 'Martinez', 'Lopez', 'Gonzales', 'Flores', 'Perez', 'Ramos',
                     'Aguilar', 'Torres', 'Rivera', 'Diaz', 'Romero', 'Sanchez', 'Castro', 'Ortiz', 'Morales', 'Valdez']
        },
        'MY': {
            'first': ['Ahmad', 'Mohd', 'Abdullah', 'Ali', 'Hassan', 'Zainal', 'Kamarul', 'Azman', 'Razali', 'Idris',
                      'Siti', 'Nur', 'Aishah', 'Fatimah', 'Zaharah', 'Rohani', 'Nor', 'Azizah', 'Hamidah', 'Salbiah'],
            'last': ['Abdullah', 'Ali', 'Hassan', 'Ahmad', 'Mohd', 'Ismail', 'Othman', 'Rahman', 'Hussein', 'Yusof',
                     'Wan', 'Zainal', 'Abdul', 'Razak', 'Ibrahim', 'Sulaiman', 'Mat', 'Hassan', 'Din', 'Shariff']
        },
        'SG': {
            'first': ['Wei', 'Ming', 'Li', 'Xin', 'Yi', 'Jun', 'Hui', 'Ling', 'Yan', 'Hao',
                      'Mei', 'Jing', 'Qiang', 'Yong', 'Chun', 'Kim', 'Seng', 'Wah', 'Choon', 'Yew'],
            'last': ['Tan', 'Lim', 'Lee', 'Ng', 'Wong', 'Ong', 'Goh', 'Chua', 'Koh', 'Chew',
                     'Yeo', 'Chong', 'Teo', 'Yap', 'Soh', 'Tay', 'Chan', 'See', 'Ang', 'Poh']
        },
        'TH': {
            'first': ['Somchai', 'Somsak', 'Prasert', 'Kriangkrai', 'Pongsak', 'Nattaporn', 'Wichian', 'Somkiat', 'Suthep', 'Anuchit',
                      'Nongnuch', 'Somjai', 'Siriporn', 'Saowanee', 'Jintana', 'Wannapa', 'Supaporn', 'Kannika', 'Ratchanee', 'Pornpimon'],
            'last': ['Somchai', 'Somsak', 'Prasert', 'Kriangkrai', 'Pongsak', 'Nattaporn', 'Wichian', 'Somkiat', 'Suthep', 'Anuchit',
                     'Nongnuch', 'Somjai', 'Siriporn', 'Saowanee', 'Jintana', 'Wannapa', 'Supaporn', 'Kannika', 'Ratchanee', 'Pornpimon']
        },
        'VN': {
            'first': ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Bui', 'Do', 'Huynh',
                      'Thi', 'Van', 'Quang', 'Minh', 'Tuan', 'Phuong', 'Anh', 'Hoa', 'Lan', 'Hai'],
            'last': ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Bui', 'Do', 'Huynh',
                     'Truong', 'Ly', 'Dinh', 'Chau', 'Ta', 'Mai', 'Duong', 'Lam', 'Phan', 'Vuong']
        },
        'XX': {
            'first': ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Hayden', 'Harper',
                      'Emerson', 'Reese', 'Charlie', 'Blake', 'Sage', 'Rowan', 'Logan', 'Peyton', 'Ari', 'Ellis'],
            'last': ['Chen', 'Singh', 'Garcia', 'Wang', 'Perez', 'Nguyen', 'Patel', 'Smith', 'Jones', 'Williams',
                     'Davis', 'Brown', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'Martin']
        }
    }
    
    @classmethod
    def get_random_name(cls, country_code):
        country_data = cls.NAMES_DATABASE.get(country_code, cls.NAMES_DATABASE['XX'])
        first_name = random.choice(country_data['first'])
        last_name = random.choice(country_data['last'])
        return first_name, last_name
    
    @classmethod
    def get_full_name(cls, country_code):
        first, last = cls.get_random_name(country_code)
        return f"{first} {last}"

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self):
        self.proxy_pool = []
        self.current_proxy = None
        self.current_country = None
        self.proxy_history = []
        self.api_key = PROXY_API_KEY
        self.last_refresh = 0
        self.refresh_interval = 300
        
    def _get_country_from_ip(self, ip):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return data.get('countryCode', 'XX')
            return 'XX'
        except:
            return 'XX'
    
    def _fetch_proxies_from_9proxy(self):
        if not self.api_key:
            return []
        try:
            url = f"https://api.9proxy.com/get?api_key={self.api_key}&format=json"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                proxies = []
                if isinstance(data, list):
                    for item in data:
                        if 'ip' in item and 'port' in item:
                            proxy = f"http://{item['ip']}:{item['port']}"
                            country = item.get('country', 'XX')
                            proxies.append({'proxy': proxy, 'country': country})
                elif isinstance(data, dict) and 'data' in data:
                    for item in data['data']:
                        if 'ip' in item and 'port' in item:
                            proxy = f"http://{item['ip']}:{item['port']}"
                            country = item.get('country', 'XX')
                            proxies.append({'proxy': proxy, 'country': country})
                return proxies
            return []
        except:
            return []
    
    def _fetch_proxies_from_webshare(self):
        if not self.api_key:
            return []
        try:
            url = f"https://api.webshare.io/v2/proxy/list/"
            headers = {'Authorization': f'Token {self.api_key}'}
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                proxies = []
                for item in data.get('results', []):
                    if 'proxy_address' in item and 'port' in item:
                        proxy = f"http://{item['proxy_address']}:{item['port']}"
                        country = item.get('country_code', 'XX')
                        proxies.append({'proxy': proxy, 'country': country})
                return proxies
            return []
        except:
            return []
    
    def _fetch_proxies_from_scrape(self):
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                proxies = []
                for line in lines:
                    if ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ip, port = parts[0], parts[1]
                            proxy = f"http://{ip}:{port}"
                            country = self._get_country_from_ip(ip)
                            proxies.append({'proxy': proxy, 'country': country})
                            time.sleep(0.1)
                return proxies
            return []
        except:
            return []
    
    def refresh_proxy_pool(self):
        all_proxies = []
        proxies = self._fetch_proxies_from_9proxy()
        if proxies:
            all_proxies.extend(proxies)
        proxies = self._fetch_proxies_from_webshare()
        if proxies:
            all_proxies.extend(proxies)
        proxies = self._fetch_proxies_from_scrape()
        if proxies:
            all_proxies.extend(proxies)
        
        seen = set()
        unique_proxies = []
        for p in all_proxies:
            if p['proxy'] not in seen:
                seen.add(p['proxy'])
                unique_proxies.append(p)
        
        self.proxy_pool = unique_proxies
        self.last_refresh = time.time()
        return len(self.proxy_pool)
    
    def get_proxy_for_number(self, phone_number):
        country_code = self._get_country_from_phone(phone_number)
        
        if not self.proxy_pool:
            self.refresh_proxy_pool()
            if not self.proxy_pool:
                self.current_proxy = None
                self.current_country = 'XX'
                return None, country_code
        
        matching_proxies = [p for p in self.proxy_pool if p['country'] == country_code]
        
        if matching_proxies:
            selected = random.choice(matching_proxies)
        else:
            selected = random.choice(self.proxy_pool)
        
        self.current_proxy = selected['proxy']
        self.current_country = selected['country']
        self.proxy_history.append({
            'phone': phone_number,
            'proxy': selected['proxy'],
            'country': selected['country']
        })
        
        return selected['proxy'], country_code
    
    def _get_country_from_phone(self, phone_number):
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
    
    def get_proxy_stats(self):
        return {
            'total': len(self.proxy_pool),
            'current': self.current_proxy,
            'country': self.current_country,
            'history_count': len(self.proxy_history),
            'last_refresh': self.last_refresh
        }

# ==================== SOUND FUNCTIONS ====================

def download_from_google_drive():
    try:
        response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL, stream=True, timeout=60, allow_redirects=True)
        if response.status_code != 200:
            return None
        filepath = os.path.join(CUSTOM_SOUND_DIR, 'background.mp3')
        if 'confirm' in response.url:
            confirm_match = re.search(r'confirm=([^&]+)', response.url)
            if confirm_match:
                confirm_code = confirm_match.group(1)
                download_url = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}&confirm={confirm_code}"
                response = requests.get(download_url, stream=True, timeout=60)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath
        return None
    except:
        return None

def download_sound_from_github(filename):
    url = f"{GITHUB_SOUND_URL}/{filename}"
    filepath = os.path.join(SOUND_DIR, filename)
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code != 200:
            return None
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filepath
    except:
        return None

def download_all_sounds():
    sounds = ['binary_rain.wav', 'startup.wav', 'click.wav', 'success.wav', 'fail.wav', 'done.wav']
    for sound in sounds:
        filepath = os.path.join(SOUND_DIR, sound)
        if not os.path.exists(filepath):
            download_sound_from_github(sound)

def download_custom_background():
    custom_mp3 = os.path.join(CUSTOM_SOUND_DIR, 'background.mp3')
    custom_wav = os.path.join(CUSTOM_SOUND_DIR, 'background.wav')
    if os.path.exists(custom_mp3) and os.path.getsize(custom_mp3) > 0:
        return True
    if os.path.exists(custom_wav) and os.path.getsize(custom_wav) > 0:
        return True
    result = download_from_google_drive()
    if result:
        return True
    return False

# ==================== TITLE ====================
class TitleAnimation:
    @staticmethod
    def compact_banner():
        os.system('clear')
        # শুধু ব্যানার - ফিচার লিস্ট বাদ
        print(f"""
{Color.CYAN}╔════════════════════════════════════════════════════════════╗{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.GOLD}RIDOL FB TOOL v{APP_VERSION}{Color.RESET}                         {Color.CYAN}║{Color.RESET}
{Color.CYAN}╚════════════════════════════════════════════════════════════╝{Color.RESET}
""")

# ==================== AUDIO ENGINE ====================
class AudioEngine:
    def __init__(self):
        self.sound_dir = SOUND_DIR
        self.custom_sound_dir = CUSTOM_SOUND_DIR
        self.voice_available = self._check_voice()
        self.sound_available = self._check_sound()
        self.bg_playing = False
        self.bg_thread = None
        self.background_file = None
        os.makedirs(self.sound_dir, exist_ok=True)
        os.makedirs(self.custom_sound_dir, exist_ok=True)
        download_all_sounds()
        download_custom_background()
    
    def _check_voice(self):
        try:
            subprocess.run(['espeak', '--help'], capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def _check_sound(self):
        try:
            subprocess.run(['mpv', '--version'], capture_output=True, timeout=2)
            return True
        except:
            try:
                subprocess.run(['play', '--help', '-q'], capture_output=True, timeout=2)
                return True
            except:
                return False
    
    def play_sound(self, filename, gain='-5'):
        if not self.sound_available:
            return
        filepath = os.path.join(self.sound_dir, filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(self.custom_sound_dir, filename)
            if not os.path.exists(filepath):
                if filename == 'background.mp3' or filename == 'background.wav':
                    download_custom_background()
                else:
                    download_sound_from_github(filename)
                if not os.path.exists(filepath):
                    return
        if filename.endswith('.mp3'):
            try:
                subprocess.Popen(['mpv', '--no-video', '--really-quiet', '--volume=80', filepath],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except:
                pass
        try:
            subprocess.Popen(['play', '-q', filepath, 'gain', gain],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    
    def play_startup(self): 
        self.play_sound('startup.wav', '-3')
    
    def play_click(self): 
        self.play_sound('click.wav', '-8')
    
    def play_success(self): 
        self.play_sound('success.wav', '-5')
    
    def play_fail(self): 
        self.play_sound('fail.wav', '-5')
    
    def play_done(self): 
        self.play_sound('done.wav', '-3')
    
    def play_background_loop(self):
        if not self.sound_available:
            return
        custom_mp3 = os.path.join(self.custom_sound_dir, 'background.mp3')
        custom_wav = os.path.join(self.custom_sound_dir, 'background.wav')
        default_bg = os.path.join(self.sound_dir, 'binary_rain.wav')
        if os.path.exists(custom_mp3) and os.path.getsize(custom_mp3) > 0:
            bg_file = custom_mp3
        elif os.path.exists(custom_wav) and os.path.getsize(custom_wav) > 0:
            bg_file = custom_wav
        else:
            bg_file = default_bg
            if not os.path.exists(bg_file):
                download_sound_from_github('binary_rain.wav')
                if not os.path.exists(bg_file):
                    return
        self.background_file = bg_file
        self.bg_playing = True
        while self.bg_playing:
            try:
                if bg_file.endswith('.mp3'):
                    subprocess.run(['mpv', '--no-video', '--really-quiet', '--volume=70', '--loop=inf', bg_file],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
                else:
                    subprocess.run(['play', '-q', bg_file, 'gain', '-3', 'repeat', '999'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            except:
                break
    
    def play_background(self):
        if self.bg_playing:
            return
        self.bg_thread = threading.Thread(target=self.play_background_loop, daemon=True)
        self.bg_thread.start()
        time.sleep(1)
    
    def stop_background_sound(self):
        self.bg_playing = False
        try:
            subprocess.run(['pkill', '-f', 'mpv.*background'], capture_output=True)
            subprocess.run(['pkill', '-f', 'play.*background'], capture_output=True)
            subprocess.run(['pkill', '-f', 'mpv.*binary_rain'], capture_output=True)
            subprocess.run(['pkill', '-f', 'play.*binary_rain'], capture_output=True)
        except:
            pass
    
    def speak(self, text, priority='normal'):
        if not self.voice_available:
            return
        try:
            speed = '110' if priority == 'high' else '125'
            subprocess.run(['espeak', text, '-v', 'en+m3', '-p', '0', '-s', speed, '-a', '200', '-g', '10'],
                         capture_output=True, timeout=10)
        except:
            pass
    
    def speak_welcome(self): self.speak('Welcome to Ridol FB Tool', 'high')
    def speak_success(self): self.speak('Success', 'high')
    def speak_otp_fail(self): self.speak('OTP send failed', 'high')
    def speak_license_verified(self): self.speak('License verified', 'high')
    def speak_bot_starting(self): self.speak('Starting bot operation', 'high')
    def speak_bot_complete(self): self.speak('All tasks completed', 'high')
    def speak_goodbye(self): self.speak('Goodbye, stay secure', 'high')
    def speak_account_created(self): self.speak('Account created')
    def speak_folder_found(self): self.speak('Folder found', 'high')
    def speak_folder_not_found(self): self.speak('Your folder not exists', 'high')
    def speak_content_found(self): self.speak('Content found', 'high')
    def speak_content_not_found(self): self.speak('Content not found', 'high')
    def speak_stopping(self): self.speak('Stopping operation', 'high')
    
    def get_status(self):
        bg_status = 'Playing' if self.bg_playing else 'Stopped'
        if self.background_file:
            bg_status += f' ({os.path.basename(self.background_file)})'
        return f""" Voice: {'Active' if self.voice_available else 'Not available'}
 Sound: {'Active' if self.sound_available else 'Not available'}
 Background: {bg_status}"""

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
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'termux-browser-pilot'], 
                         capture_output=True, timeout=60)
            return True
        except:
            return False
    
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
            if proxy:
                os.environ['http_proxy'] = proxy
                os.environ['https_proxy'] = proxy
            self.browser = Browser(headless=headless)
            self.browser_started = True
            return True
        except:
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
    
    def wait_for_text(self, selector, timeout=60):
        if not self.browser_started:
            return None
        try:
            return self.browser.wait_for_text(selector, timeout=timeout)
        except:
            return None
    
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
    
    def save(self): save_json(CONFIG_FILE, self.config)
    def get_license_key(self): return self.config.get('license_key', '')
    def set_license_key(self, key): self.config['license_key'] = key; self.save()
    def get_device_serial(self): return self.config.get('device_serial', '')
    def set_device_serial(self, s): self.config['device_serial'] = s; self.save()
    def get_proxy_api_key(self): return self.config.get('proxy_api_key', '')
    def set_proxy_api_key(self, key): self.config['proxy_api_key'] = key; self.save()
    
    def verify(self, key):
        result = verify_license(key, self.get_device_serial())
        if result.get('valid'):
            self.set_license_key(key)
            return True, result
        else:
            return False, result
    
    def register_device(self, device_serial):
        result = register_device(device_serial, self.get_license_key())
        if result.get('success'):
            self.set_device_serial(device_serial)
            return True
        else:
            return False

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

# ==================== FACEBOOK AUTOMATION ENGINE ====================
class FacebookAutomationEngine:
    def __init__(self):
        self.is_running = False
        self.stats = {'processed': 0, 'success': 0, 'failed': 0, 'otp_sent': 0}
        self.browser_manager = BrowserPilotManager()
        self.proxy_manager = ProxyManager()
        self.name_generator = NameGenerator()
        self.audio = None
    
    def _generate_device_fingerprint(self):
        brands = ['Samsung', 'Xiaomi', 'OnePlus', 'Google', 'Motorola', 'Realme']
        models = ['SM-G998B', 'SM-G991B', 'M2101K7AG', 'LE2123', 'Pixel 6', 'Moto G100']
        android_versions = ['11', '12', '13']
        return {
            'brand': random.choice(brands),
            'model': random.choice(models),
            'android_version': random.choice(android_versions),
            'android_id': ''.join(random.choices('0123456789abcdef', k=16)),
            'imei': ''.join(random.choices('0123456789', k=15)),
            'serial': ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
        }
    
    def _fill_registration_form(self, phone_number, country_code):
        try:
            first_name, last_name = self.name_generator.get_random_name(country_code)
            full_name = f"{first_name} {last_name}"
            self.browser_manager.type_text(FB_CONFIG['UI_ELEMENTS']['phone_input'], phone_number)
            time.sleep(1)
            self.browser_manager.click(FB_CONFIG['UI_ELEMENTS']['next_button'])
            time.sleep(3)
            try:
                self.browser_manager.type_text(FB_CONFIG['UI_ELEMENTS']['fullname_input'], full_name)
                time.sleep(1)
            except:
                pass
            return True
        except:
            return False
    
    def _request_otp_with_retry(self):
        for attempt in range(FB_CONFIG['MAX_OTP_RETRIES']):
            try:
                otp_text = self.browser_manager.wait_for_text(".otp-code, .verification-code, input[name='otp']", 
                                                             timeout=FB_CONFIG['OTP_WAIT_TIMEOUT'])
                if otp_text:
                    self.stats['otp_sent'] += 1
                    return otp_text
                if attempt < FB_CONFIG['MAX_OTP_RETRIES'] - 1:
                    resend_btn = "button:has-text('Resend'), #resend_otp, .resend-btn"
                    self.browser_manager.click(resend_btn)
                    time.sleep(FB_CONFIG['OTP_RETRY_DELAY'])
            except:
                time.sleep(FB_CONFIG['OTP_RETRY_DELAY'])
        return None
    
    def _complete_registration(self, otp_code):
        try:
            self.browser_manager.type_text(FB_CONFIG['UI_ELEMENTS']['otp_input'], otp_code)
            time.sleep(1)
            self.browser_manager.click(FB_CONFIG['UI_ELEMENTS']['otp_submit'])
            time.sleep(3)
            return True
        except:
            return False
    
    def _process_single_number(self, phone_number):
        country_code = self.proxy_manager._get_country_from_phone(phone_number)
        proxy, _ = self.proxy_manager.get_proxy_for_number(phone_number)
        
        if not self.browser_manager.start_browser(headless=False, proxy=proxy):
            self.stats['failed'] += 1
            return False
        
        try:
            self.browser_manager.goto("https://m.facebook.com/create-account")
            time.sleep(2)
            if not self._fill_registration_form(phone_number, country_code):
                self.stats['failed'] += 1
                return False
            time.sleep(2)
            otp = self._request_otp_with_retry()
            if not otp:
                self.stats['failed'] += 1
                if self.audio:
                    self.audio.play_fail()
                    self.audio.speak_otp_fail()
                return False
            if not self._complete_registration(otp):
                self.stats['failed'] += 1
                return False
            self.stats['success'] += 1
            if self.audio:
                self.audio.play_success()
                self.audio.speak_account_created()
            return True
        except:
            self.stats['failed'] += 1
            return False
        finally:
            self.browser_manager.close_browser()
    
    def start_batch_processing(self, numbers):
        if not numbers:
            return
        self.proxy_manager.refresh_proxy_pool()
        self.is_running = True
        for idx, phone in enumerate(numbers, 1):
            if not self.is_running:
                break
            try:
                self._process_single_number(phone)
                self.stats['processed'] += 1
            except:
                self.stats['failed'] += 1
            if idx < len(numbers) and self.is_running:
                delay = random.randint(FB_CONFIG['BATCH_DELAY_MIN'], FB_CONFIG['BATCH_DELAY_MAX'])
                for remaining in range(delay, 0, -1):
                    if not self.is_running:
                        break
                    time.sleep(1)
        if self.audio:
            self.audio.play_done()
            self.audio.speak_bot_complete()
        self.is_running = False
    
    def stop(self):
        self.is_running = False
        self.browser_manager.close_browser()
        if self.audio:
            self.audio.speak_stopping()

# ==================== FACEBOOK BOT ====================
class FacebookBot:
    def __init__(self, data_dir, license_key, audio):
        self.data_dir = data_dir
        self.license_key = license_key
        self.audio = audio
        self.numbers = load_file_lines(os.path.join(data_dir, 'numbers.txt'))
        self.running = False
        self.stats = {'success': 0, 'failed': 0, 'total': 0}
        self.automation_engine = None
    
    def run_bot(self, workers=1):
        if not self.numbers:
            return
        self.running = True
        self.stats = {'success': 0, 'failed': 0, 'total': 0}
        self.automation_engine = FacebookAutomationEngine()
        self.automation_engine.audio = self.audio
        self.automation_engine.start_batch_processing(self.numbers)
        self.running = False
        self.audio.play_done()
        self.audio.speak_bot_complete()

# ==================== ANIMATION ====================
class Animation:
    @staticmethod
    def typing(text, delay=0.03, color=Color.CYAN):
        for char in text:
            print(f'{color}{char}{Color.RESET}', end='', flush=True)
            time.sleep(delay)
        print()
    
    @staticmethod
    def ending_animation():
        print(f'\n{Color.CYAN}')
        print('    ╔══════════════════════════════════════════════╗')
        print('    ║     Thank you for using Ridol FB Tool        ║')
        print(f'    ║     {Color.YELLOW}Stay Secure!{Color.CYAN}                              ║')
        print('    ╚══════════════════════════════════════════════╝')
        print(f'{Color.RESET}')

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
        
        api_key = self.config.get('proxy_api_key', '')
        if api_key:
            PROXY_API_KEY = api_key
    
    def show_header(self):
        clear_screen()
        TitleAnimation.compact_banner()
        print()
    
    def welcome_screen(self):
        clear_screen()
        TitleAnimation.compact_banner()
        self.audio.play_startup()
        self.audio.play_background()
        threading.Thread(target=self.audio.speak_welcome, daemon=True).start()
        time.sleep(1)
        clear_screen()
        TitleAnimation.compact_banner()
        time.sleep(0.5)
    
    def check_stop_input(self):
        while self.bot_running:
            try:
                if sys.stdin.isatty():
                    inp = sys.stdin.read(1)
                    if inp == '0':
                        self.bot_running = False
                        if self.bot and self.bot.automation_engine:
                            self.bot.automation_engine.stop()
                        self.audio.speak_stopping()
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
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Proxy Info                     {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1': self.menu_setup()
            elif choice == '2': self.menu_start_bot()
            elif choice == '3': self.menu_status()
            elif choice == '4': self.menu_proxy_info()
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
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Set Proxy API Key               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Set Data Folder                 {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[5]{Color.RESET} Create Required Files           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[6]{Color.RESET} Refresh Proxy Pool              {Color.CYAN}║{Color.RESET}
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
                press_enter()
            elif choice == '3':
                key = input(f'  {Color.CYAN}Enter proxy API key: {Color.RESET}').strip()
                if key:
                    self.license.set_proxy_api_key(key)
                    self.proxy_manager.api_key = key
                press_enter()
            elif choice == '4':
                path = input(f'  {Color.CYAN}Enter data folder path: {Color.RESET}').strip()
                if path:
                    self.data_dir = path
                    self.config['data_dir'] = path
                    save_json(CONFIG_FILE, self.config)
                press_enter()
            elif choice == '5':
                os.makedirs(self.data_dir, exist_ok=True)
                for fname in ['numbers.txt', 'names.txt', 'proxies.txt']:
                    fpath = os.path.join(self.data_dir, fname)
                    if not os.path.exists(fpath):
                        with open(fpath, 'w') as f:
                            f.write(f'# {fname}\n')
                press_enter()
            elif choice == '6':
                count = self.proxy_manager.refresh_proxy_pool()
                print(f'  {Color.GREEN}[+] Refreshed! {count} proxies available{Color.RESET}')
                press_enter()
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_start_bot(self):
        self.show_header()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}START BOT{Color.RESET}{Color.CYAN}                                     ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Numbers: {len(load_file_lines(os.path.join(self.data_dir, "numbers.txt")))}                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.DIM}{self.license.get_license_key() or "Not set"}{Color.RESET}{Color.CYAN}             ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        
        if not self.license.get_license_key():
            print(f'\n{Color.RED}[-] No license key set!{Color.RESET}')
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
        
        self.bot = FacebookBot(self.data_dir, self.license.get_license_key(), self.audio)
        self.audio.speak_bot_starting()
        self.bot.run_bot(1)
        
        self.bot_running = False
        time.sleep(1)
        
        print(f'\n{Color.GREEN}[+] Done{Color.RESET}')
        press_enter()
    
    def menu_status(self):
        self.show_header()
        proxy_stats = self.proxy_manager.get_proxy_stats()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}STATUS{Color.RESET}{Color.CYAN}                                      ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Browser: {Color.WHITE}{"Installed" if self.browser_manager.browser_available else "Not installed"}{Color.RESET}{Color.CYAN}  ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Proxies: {Color.WHITE}{proxy_stats['total']}{Color.RESET}{Color.CYAN}                                ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.WHITE}{"Active" if self.license.get_license_key() else "None"}{Color.RESET}{Color.CYAN}             ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {self.audio.get_status()}{Color.CYAN}         ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        if self.bot:
            print(self.bot.get_status())
        press_enter()
    
    def menu_proxy_info(self):
        """Proxy info - এখানে প্রোক্সি ডিটেইলস দেখাবে"""
        self.show_header()
        proxy_stats = self.proxy_manager.get_proxy_stats()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}PROXY INFO{Color.RESET}{Color.CYAN}                                   ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Total Proxies: {Color.WHITE}{proxy_stats['total']}{Color.RESET}{Color.CYAN}                           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Current Proxy: {Color.WHITE}{proxy_stats.get('current', 'None')}{Color.RESET}{Color.CYAN}             ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Country: {Color.WHITE}{proxy_stats.get('country', 'None')}{Color.RESET}{Color.CYAN}                     ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  History: {Color.WHITE}{proxy_stats['history_count']}{Color.RESET}{Color.CYAN}                           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Last Refresh: {Color.WHITE}{time.strftime('%H:%M:%S', time.localtime(proxy_stats['last_refresh']))}{Color.RESET}{Color.CYAN}     ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        press_enter()
    
    def menu_exit(self):
        if self.bot_running:
            self.bot_running = False
            if self.bot and self.bot.automation_engine:
                self.bot.automation_engine.stop()
        self.audio.stop_background_sound()
        Animation.ending_animation()
        threading.Thread(target=self.audio.speak_goodbye, daemon=True).start()
        time.sleep(1)
        print(f'\n{Color.GREEN}Goodbye!{Color.RESET}')
        sys.exit(0)

# ==================== MAIN ====================
if __name__ == '__main__':
    try:
        try:
            subprocess.run(['mpv', '--version'], capture_output=True, check=True)
        except:
            pass
        
        download_all_sounds()
        download_custom_background()
        time.sleep(1)
        menu = MainMenu()
        menu.menu_main()
    except KeyboardInterrupt:
        print(f'\n\n{Color.YELLOW}[!] Interrupted{Color.RESET}')
        sys.exit(0)
    except Exception as e:
        print(f'\n{Color.RED}[-] Error: {e}{Color.RESET}')
        sys.exit(1)