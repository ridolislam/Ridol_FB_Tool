#!/usr/bin/env python3
"""
Ridol FB Tool v7.0 - License & Credit Based Proxy System
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
import math
import struct
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
APP_VERSION = 'v7.0'

# ==================== SERVER CONFIG ====================
SERVER_URL = 'https://ridol-fb-tool.onrender.com'

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

# ==================== COUNTRY CODES ====================
COUNTRY_CODES = {
    '93': 'AF', '374': 'AM', '994': 'AZ', '880': 'BD', '975': 'BT',
    '673': 'BN', '855': 'KH', '86': 'CN', '852': 'HK', '91': 'IN',
    '62': 'ID', '98': 'IR', '964': 'IQ', '972': 'IL', '81': 'JP',
    '962': 'JO', '7': 'KZ', '965': 'KW', '996': 'KG', '856': 'LA',
    '961': 'LB', '60': 'MY', '960': 'MV', '976': 'MN', '95': 'MM',
    '977': 'NP', '850': 'KP', '968': 'OM', '92': 'PK', '970': 'PS',
    '63': 'PH', '974': 'QA', '966': 'SA', '65': 'SG', '82': 'KR',
    '94': 'LK', '963': 'SY', '886': 'TW', '992': 'TJ', '66': 'TH',
    '90': 'TR', '993': 'TM', '971': 'AE', '998': 'UZ', '84': 'VN',
    '967': 'YE',
    '355': 'AL', '376': 'AD', '43': 'AT', '375': 'BY', '32': 'BE',
    '387': 'BA', '359': 'BG', '385': 'HR', '357': 'CY', '420': 'CZ',
    '45': 'DK', '372': 'EE', '358': 'FI', '33': 'FR', '995': 'GE',
    '49': 'DE', '30': 'GR', '36': 'HU', '354': 'IS', '353': 'IE',
    '39': 'IT', '371': 'LV', '423': 'LI', '370': 'LT', '352': 'LU',
    '389': 'MK', '356': 'MT', '373': 'MD', '377': 'MC', '382': 'ME',
    '31': 'NL', '47': 'NO', '48': 'PL', '351': 'PT', '40': 'RO',
    '7': 'RU', '381': 'RS', '421': 'SK', '386': 'SI', '34': 'ES',
    '46': 'SE', '41': 'CH', '380': 'UA', '44': 'GB', '379': 'VA',
    '1': 'US', '52': 'MX', '501': 'BZ', '506': 'CR', '53': 'CU',
    '1': 'DM', '1': 'DO', '503': 'SV', '502': 'GT', '504': 'HN',
    '1': 'JM', '505': 'NI', '507': 'PA', '1': 'TT', '1': 'BS',
    '1': 'BB', '1': 'GD', '1': 'LC', '1': 'VC',
    '54': 'AR', '591': 'BO', '55': 'BR', '56': 'CL', '57': 'CO',
    '593': 'EC', '592': 'GY', '595': 'PY', '51': 'PE', '597': 'SR',
    '598': 'UY', '58': 'VE',
    '213': 'DZ', '244': 'AO', '229': 'BJ', '267': 'BW', '226': 'BF',
    '257': 'BI', '237': 'CM', '238': 'CV', '236': 'CF', '235': 'TD',
    '269': 'KM', '243': 'CD', '242': 'CG', '253': 'DJ', '20': 'EG',
    '240': 'GQ', '291': 'ER', '251': 'ET', '241': 'GA', '220': 'GM',
    '233': 'GH', '224': 'GN', '245': 'GW', '254': 'KE', '266': 'LS',
    '231': 'LR', '218': 'LY', '261': 'MG', '265': 'MW', '223': 'ML',
    '222': 'MR', '230': 'MU', '212': 'MA', '258': 'MZ', '264': 'NA',
    '227': 'NE', '234': 'NG', '250': 'RW', '239': 'ST', '221': 'SN',
    '248': 'SC', '232': 'SL', '252': 'SO', '27': 'ZA', '211': 'SS',
    '249': 'SD', '268': 'SZ', '255': 'TZ', '228': 'TG', '216': 'TN',
    '256': 'UG', '260': 'ZM', '263': 'ZW',
    '61': 'AU', '679': 'FJ', '686': 'KI', '692': 'MH', '691': 'FM',
    '674': 'NR', '64': 'NZ', '675': 'PG', '685': 'WS', '677': 'SB',
    '676': 'TO', '688': 'TV', '678': 'VU',
    'XX': 'XX',
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
    """Make request to license server"""
    url = f"{SERVER_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            return None
        if response.status_code in [200, 201, 204]:
            if response.text:
                return response.json()
            return {'success': True}
        return None
    except:
        return None

def check_server_status():
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

# ==================== NAME GENERATOR ====================
class NameGenerator:
    NAMES_DATABASE = {
        'BD': {'first': ['Mohammad', 'Abdullah', 'Rafiq', 'Shahid', 'Kamal', 'Jamal', 'Rahim', 'Karim', 'Hasan', 'Ali'], 'last': ['Rahman', 'Ahmed', 'Islam', 'Hossain', 'Ali', 'Khan', 'Haque', 'Sarkar', 'Mia', 'Pramanik']},
        'IN': {'first': ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Pranav', 'Dhruv', 'Aryan', 'Reyansh'], 'last': ['Sharma', 'Verma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Gandhi', 'Prasad', 'Sinha']},
        'US': {'first': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles'], 'last': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']},
        'GB': {'first': ['Oliver', 'George', 'Harry', 'Jack', 'Jacob', 'Charlie', 'Thomas', 'James', 'William', 'Muhammad'], 'last': ['Smith', 'Jones', 'Williams', 'Taylor', 'Brown', 'Davies', 'Evans', 'Thomas', 'Johnson', 'Roberts']},
        'PK': {'first': ['Muhammad', 'Ali', 'Ahmed', 'Hassan', 'Usman', 'Omar', 'Zain', 'Hamza', 'Bilal', 'Raza'], 'last': ['Khan', 'Malik', 'Akhtar', 'Shah', 'Chaudhry', 'Butt', 'Qureshi', 'Sheikh', 'Abbasi', 'Javed']},
        'ID': {'first': ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fitri', 'Gilang', 'Hana', 'Indra', 'Joko'], 'last': ['Siregar', 'Nasution', 'Harahap', 'Lubis', 'Batubara', 'Sinaga', 'Saragih', 'Ginting']},
        'MY': {'first': ['Ahmad', 'Mohd', 'Abdullah', 'Ali', 'Hassan', 'Zainal', 'Kamarul', 'Azman', 'Razali', 'Idris'], 'last': ['Abdullah', 'Ali', 'Hassan', 'Ahmad', 'Mohd', 'Ismail', 'Othman', 'Rahman', 'Hussein', 'Yusof']},
        'SG': {'first': ['Wei', 'Ming', 'Li', 'Xin', 'Yi', 'Jun', 'Hui', 'Ling', 'Yan', 'Hao'], 'last': ['Tan', 'Lim', 'Lee', 'Ng', 'Wong', 'Ong', 'Goh', 'Chua', 'Koh', 'Chew']},
        'PH': {'first': ['Jose', 'Juan', 'Carlos', 'Ramon', 'Pedro', 'Andres', 'Emilio', 'Josefino', 'Ronaldo', 'Ferdinand'], 'last': ['Santos', 'Reyes', 'Cruz', 'Garcia', 'Martinez', 'Lopez', 'Gonzales', 'Flores', 'Perez', 'Ramos']},
        'TH': {'first': ['Somchai', 'Somsak', 'Prasert', 'Kriangkrai', 'Pongsak', 'Nattaporn', 'Wichian', 'Somkiat', 'Suthep', 'Anuchit'], 'last': ['Somchai', 'Somsak', 'Prasert', 'Kriangkrai', 'Pongsak', 'Nattaporn', 'Wichian', 'Somkiat', 'Suthep', 'Anuchit']},
        'VN': {'first': ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Bui', 'Do', 'Huynh'], 'last': ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Bui', 'Do', 'Huynh']},
        'AE': {'first': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Omar', 'Khalid', 'Saeed', 'Abdulla', 'Rashid', 'Hamad'], 'last': ['Al Maktoum', 'Al Nahyan', 'Al Suwaidi', 'Al Tayer', 'Al Ghurair', 'Al Habtoor', 'Al Futtaim']},
        'SA': {'first': ['Mohammed', 'Ahmed', 'Ali', 'Abdullah', 'Omar', 'Saud', 'Khalid', 'Sultan', 'Faisal', 'Nayef'], 'last': ['Al Saud', 'Al Thani', 'Al Otaibi', 'Al Harbi', 'Al Anzi', 'Al Shamrani', 'Al Mutairi']},
        'TR': {'first': ['Mehmet', 'Ahmet', 'Ali', 'Mustafa', 'Hasan', 'Huseyin', 'Osman', 'Yusuf', 'Ibrahim', 'Ismail'], 'last': ['Yilmaz', 'Kaya', 'Demir', 'Celik', 'Aydin', 'Ozdemir', 'Arslan', 'Dogan', 'Kilic', 'Yildirim']},
        'RU': {'first': ['Alexander', 'Dmitri', 'Ivan', 'Mikhail', 'Nikolai', 'Sergei', 'Vladimir', 'Yuri', 'Andrei', 'Pavel'], 'last': ['Ivanov', 'Petrov', 'Sidorov', 'Kuznetsov', 'Smirnov', 'Popov', 'Sokolov', 'Lebedev', 'Kozlov', 'Novikov']},
        'BR': {'first': ['Joao', 'Jose', 'Maria', 'Antonio', 'Francisco', 'Carlos', 'Paulo', 'Pedro', 'Lucas', 'Gabriel'], 'last': ['Silva', 'Santos', 'Souza', 'Oliveira', 'Pereira', 'Costa', 'Rodrigues', 'Almeida', 'Nascimento', 'Lima']},
        'JP': {'first': ['Haruto', 'Sota', 'Yuki', 'Riku', 'Hinata', 'Sakura', 'Hana', 'Yui', 'Mio', 'Rin'], 'last': ['Sato', 'Suzuki', 'Takahashi', 'Tanaka', 'Watanabe', 'Ito', 'Yamamoto', 'Nakamura', 'Kobayashi', 'Kato']},
        'CN': {'first': ['Wei', 'Ming', 'Li', 'Xin', 'Yi', 'Jun', 'Hui', 'Ling', 'Yan', 'Hao'], 'last': ['Wang', 'Li', 'Zhang', 'Liu', 'Chen', 'Yang', 'Huang', 'Zhao', 'Wu', 'Zhou']},
        'DE': {'first': ['Hans', 'Peter', 'Klaus', 'Wolfgang', 'Thomas', 'Andreas', 'Michael', 'Stefan', 'Markus', 'Daniel'], 'last': ['Muller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker', 'Schulz', 'Hoffmann']},
        'FR': {'first': ['Jean', 'Pierre', 'Michel', 'Philippe', 'Alain', 'Bernard', 'Eric', 'Nicolas', 'David', 'Christophe'], 'last': ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau']},
        'IT': {'first': ['Marco', 'Giuseppe', 'Antonio', 'Giovanni', 'Francesco', 'Andrea', 'Luca', 'Mario', 'Paolo', 'Roberto'], 'last': ['Rossi', 'Russo', 'Ferrari', 'Esposito', 'Bianchi', 'Romano', 'Colombo', 'Ricci', 'Marino', 'Greco']},
        'ES': {'first': ['Antonio', 'Jose', 'Manuel', 'Francisco', 'Juan', 'David', 'Javier', 'Carlos', 'Daniel', 'Luis'], 'last': ['Garcia', 'Rodriguez', 'Gonzalez', 'Fernandez', 'Lopez', 'Martinez', 'Sanchez', 'Perez', 'Gomez', 'Martin']},
        'AU': {'first': ['Jack', 'Oliver', 'William', 'James', 'Thomas', 'Liam', 'Noah', 'Ethan', 'Lucas', 'Mason'], 'last': ['Smith', 'Jones', 'Williams', 'Brown', 'Wilson', 'Taylor', 'Johnson', 'White', 'Martin', 'Anderson']},
        'ZA': {'first': ['Nelson', 'Jacob', 'Cyril', 'Thabo', 'Kofi', 'Mandela', 'Desmond', 'Winnie', 'Graça', 'Miriam'], 'last': ['Mbeki', 'Zuma', 'Ramaphosa', 'Tambo', 'Machel', 'Tutu', 'Sisulu', 'Motlanthe', 'Msimang', 'Madikizela']},
        'EG': {'first': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Omar', 'Mahmoud', 'Tarek', 'Khaled', 'Amr', 'Youssef'], 'last': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Mahmoud', 'Tarek', 'Khaled', 'Amr', 'Youssef', 'Ibrahim']},
        'NG': {'first': ['Oluwaseun', 'Chukwudi', 'Adebayo', 'Olayinka', 'Emeka', 'Chidi', 'Adeola', 'Babatunde', 'Olumide', 'Segun'], 'last': ['Adeyemi', 'Ogunlade', 'Bamidele', 'Okonkwo', 'Eze', 'Nwosu', 'Okafor', 'Igwe', 'Umeh', 'Obi']},
        'XX': {'first': ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Hayden', 'Harper'], 'last': ['Chen', 'Singh', 'Garcia', 'Wang', 'Perez', 'Nguyen', 'Patel', 'Smith', 'Jones', 'Williams']}
    }
    
    @classmethod
    def get_random_name(cls, country_code):
        country_data = cls.NAMES_DATABASE.get(country_code, cls.NAMES_DATABASE['XX'])
        return random.choice(country_data['first']), random.choice(country_data['last'])
    
    @classmethod
    def get_full_name(cls, country_code):
        first, last = cls.get_random_name(country_code)
        return f"{first} {last}"

# ==================== LICENSE MANAGER ====================
class LicenseManager:
    def __init__(self):
        self.config = load_json(CONFIG_FILE)
        self.server_url = SERVER_URL
        self.license_key = self.config.get('license_key', '')
        self.credits = 0
        self.max_browsers = 1
        self.used_credits = 0
        self.is_valid = False
        self.expires_at = None
        self.user_id = None
        
    def verify(self, license_key):
        """Verify license with server"""
        try:
            url = f"{self.server_url}/api/verify"
            response = requests.post(url, json={'license_key': license_key}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    self.license_key = license_key
                    self.credits = data.get('credits', 0)
                    self.max_browsers = data.get('max_browsers', 1)
                    self.used_credits = data.get('used_credits', 0)
                    self.expires_at = data.get('expires_at')
                    self.user_id = data.get('user_id', '')
                    self.is_valid = True
                    self.config['license_key'] = license_key
                    save_json(CONFIG_FILE, self.config)
                    return True, data
                else:
                    self.is_valid = False
                    return False, data
            else:
                self.is_valid = False
                return False, {'error': 'Server error'}
                
        except Exception as e:
            self.is_valid = False
            return False, {'error': str(e)}
    
    def get_ip(self, country='Rand'):
        """Get IP from server (deducts 1 credit)"""
        if not self.is_valid:
            return None, 'License not valid'
        
        try:
            url = f"{self.server_url}/api/get_ip"
            response = requests.post(url, json={
                'license_key': self.license_key,
                'country': country
            }, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.credits = data.get('remaining_credits', 0)
                    return data.get('ip'), None
                else:
                    return None, data.get('error', 'Failed to get IP')
            else:
                return None, f'Server error: {response.status_code}'
                
        except Exception as e:
            return None, str(e)
    
    def get_status(self):
        """Get current license status"""
        return {
            'valid': self.is_valid,
            'credits': self.credits,
            'max_browsers': self.max_browsers,
            'used_credits': self.used_credits,
            'license_key': self.license_key,
            'expires_at': self.expires_at,
            'user_id': self.user_id
        }
    
    def check_status(self):
        """Check license status from server"""
        if not self.license_key:
            return {'valid': False, 'error': 'No license key set'}
        
        try:
            url = f"{self.server_url}/api/status"
            response = requests.post(url, json={'license_key': self.license_key}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    self.credits = data.get('credits', 0)
                    self.max_browsers = data.get('max_browsers', 1)
                    self.used_credits = data.get('used_credits', 0)
                    self.expires_at = data.get('expires_at')
                    self.user_id = data.get('user_id', '')
                    self.is_valid = True
                    return data
                else:
                    self.is_valid = False
                    return data
            else:
                return {'valid': False, 'error': 'Server error'}
                
        except Exception as e:
            return {'valid': False, 'error': str(e)}

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self):
        self.proxy_pool = []
        self.current_proxy = None
        self.current_country = None
        self.proxy_history = []
        self.api_key = None
        self.last_refresh = 0
        self.refresh_interval = 300
        self.use_default_ip = True
        self.connected_ip_url = None
        self.ip_connected = False
        self.user_id = None
        self.license_manager = LicenseManager()
        
    def _get_country_from_phone(self, phone_number):
        phone = phone_number.strip().replace('+', '').replace(' ', '').replace('-', '')
        for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
            if phone.startswith(code):
                return COUNTRY_CODES[code]
        return 'XX'
    
    def connect_via_license(self, country_code):
        """Get IP using license credits"""
        print(f"{Color.CYAN}[*] Requesting IP for {country_code} using license...{Color.RESET}")
        
        ip, error = self.license_manager.get_ip(country_code)
        
        if error:
            print(f"{Color.RED}[-] Error: {error}{Color.RESET}")
            return False
        
        if ip:
            proxy_url = f"socks5://{ip}:3010"
            print(f"{Color.GREEN}[+] Got IP: {ip}{Color.RESET}")
            print(f"{Color.CYAN}[+] Remaining credits: {self.license_manager.credits}{Color.RESET}")
            
            # Test proxy
            test_proxies = {'http': proxy_url, 'https': proxy_url}
            try:
                response = requests.get('http://ip-api.com/json', proxies=test_proxies, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    print(f"{Color.GREEN}[+] Proxy works!{Color.RESET}")
                    print(f"{Color.CYAN}[+] IP: {data.get('query')} | Country: {data.get('countryCode')}{Color.RESET}")
                    
                    self.connected_ip_url = proxy_url
                    self.ip_connected = True
                    self.current_country = country_code
                    self.user_id = ip
                    return True
                else:
                    print(f"{Color.RED}[-] Proxy test failed: {response.status_code}{Color.RESET}")
                    return False
            except Exception as e:
                print(f"{Color.RED}[-] Proxy test error: {e}{Color.RESET}")
                return False
        
        return False
    
    def disconnect_ip(self):
        self.connected_ip_url = None
        self.ip_connected = False
        self.user_id = None
        print(f"{Color.YELLOW}[!] IP Disconnected{Color.RESET}")
        return True
    
    def refresh_proxy_pool(self):
        print(f"{Color.CYAN}[*] Refreshing proxy pool...{Color.RESET}")
        all_proxies = []
        if self.connected_ip_url and self.ip_connected:
            all_proxies.append({'proxy': self.connected_ip_url, 'country': 'XX', 'type': 'socks5'})
            print(f"{Color.GREEN}[+] Added Connected IP to pool{Color.RESET}")
        self.proxy_pool = all_proxies
        self.last_refresh = time.time()
        if len(self.proxy_pool) == 0:
            print(f"{Color.YELLOW}[!] No proxies found. Please connect an IP first.{Color.RESET}")
        else:
            print(f"{Color.GREEN}[+] Total proxies: {len(self.proxy_pool)}{Color.RESET}")
        return len(self.proxy_pool)
    
    def get_proxy_for_number(self, phone_number):
        country_code = self._get_country_from_phone(phone_number)
        print(f"{Color.CYAN}[+] Country detected: {country_code}{Color.RESET}")
        
        # Check if license is valid
        if not self.license_manager.is_valid:
            print(f"{Color.RED}[-] License not valid. Please enter valid license key.{Color.RESET}")
            self.current_proxy = None
            self.current_country = 'XX'
            return None, country_code
        
        # Check credits
        if self.license_manager.credits <= 0:
            print(f"{Color.RED}[-] Insufficient credits. Please add more credits.{Color.RESET}")
            self.current_proxy = None
            self.current_country = 'XX'
            return None, country_code
        
        # Get new IP for this country
        if not self.connect_via_license(country_code):
            print(f"{Color.YELLOW}[!] Failed to get IP for {country_code}. Using default.{Color.RESET}")
            self.current_proxy = None
            self.current_country = 'XX'
            return None, country_code
        
        if self.connected_ip_url:
            self.current_proxy = self.connected_ip_url
            self.proxy_history.append({
                'phone': phone_number,
                'proxy': self.connected_ip_url,
                'country': country_code,
                'type': 'license_credit'
            })
            return self.connected_ip_url, country_code
        
        print(f"{Color.YELLOW}[!] No proxy available. Using default IP.{Color.RESET}")
        self.current_proxy = None
        self.current_country = 'XX'
        return None, country_code
    
    def get_proxy_stats(self):
        return {
            'total': len(self.proxy_pool),
            'current': self.current_proxy,
            'country': self.current_country,
            'history_count': len(self.proxy_history),
            'last_refresh': self.last_refresh,
            'using_default_ip': self.current_proxy is None,
            'ip_connected': self.ip_connected,
            'connected_ip': self.connected_ip_url,
            'user_id': self.user_id,
            'credits': self.license_manager.credits,
            'license_valid': self.license_manager.is_valid
        }

# ==================== SOUND FUNCTIONS ====================

def download_from_google_drive():
    try:
        print(f"{Color.CYAN}[*] Downloading custom MP3 from Google Drive...{Color.RESET}")
        response = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL, stream=True, timeout=60, allow_redirects=True)
        if response.status_code != 200:
            print(f"{Color.YELLOW}[!] Google Drive download failed: {response.status_code}{Color.RESET}")
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
            print(f"{Color.GREEN}[+] Downloaded: background.mp3 ({os.path.getsize(filepath)} bytes){Color.RESET}")
            return filepath
        return None
    except Exception as e:
        print(f"{Color.RED}[-] Google Drive download error: {e}{Color.RESET}")
        return None

def download_sound_from_github(filename):
    url = f"{GITHUB_SOUND_URL}/{filename}"
    filepath = os.path.join(SOUND_DIR, filename)
    try:
        print(f"{Color.CYAN}[*] Downloading {filename} from GitHub...{Color.RESET}")
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code != 200:
            print(f"{Color.YELLOW}[!] {filename} not found on GitHub{Color.RESET}")
            return None
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"{Color.GREEN}[+] Downloaded: {filename}{Color.RESET}")
        return filepath
    except Exception as e:
        print(f"{Color.RED}[-] Download error: {e}{Color.RESET}")
        return None

def download_all_sounds():
    sounds = ['binary_rain.wav', 'startup.wav', 'click.wav', 'success.wav', 'fail.wav', 'done.wav']
    print(f"{Color.CYAN}[*] Checking default sounds...{Color.RESET}")
    for sound in sounds:
        filepath = os.path.join(SOUND_DIR, sound)
        if not os.path.exists(filepath):
            download_sound_from_github(sound)

def download_custom_background():
    custom_mp3 = os.path.join(CUSTOM_SOUND_DIR, 'background.mp3')
    if os.path.exists(custom_mp3) and os.path.getsize(custom_mp3) > 0:
        print(f"{Color.DIM}[*] Custom background MP3 already exists{Color.RESET}")
        return True
    result = download_from_google_drive()
    if result:
        return True
    print(f"{Color.YELLOW}[!] No custom background sound found. Using default.{Color.RESET}")
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
{Color.CYAN}║{Color.RESET}           {Color.WHITE}{Color.BOLD}RIDOL FB TOOL v{APP_VERSION}{Color.RESET}               {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}      {Color.DIM}License & Credit Based Proxy System{Color.RESET}       {Color.CYAN}║{Color.RESET}
{Color.CYAN}╠════════════════════════════════════════════════════════════╣{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}FACEBOOK{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}AUTO CREATE{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}CREDIT SYSTEM{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}AUTO NAME{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}OTP RETRY{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}VOICE FEEDBACK{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}AUTO COUNTRY{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}LICENSE SYSTEM{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}╚════════════════════════════════════════════════════════════╝{Color.RESET}
"""
        print(banner)
        time.sleep(0.5)

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
    
    def play_startup(self): self.play_sound('startup.wav', '-3')
    def play_click(self): self.play_sound('click.wav', '-8')
    def play_success(self): self.play_sound('success.wav', '-5')
    def play_fail(self): self.play_sound('fail.wav', '-5')
    def play_done(self): self.play_sound('done.wav', '-3')
    
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
    def speak_ip_connected(self): self.speak('IP connected successfully', 'high')
    def speak_ip_disconnected(self): self.speak('IP disconnected', 'high')
    
    def get_status(self):
        bg_status = 'Playing' if self.bg_playing else 'Stopped'
        if self.background_file:
            bg_status += f' ({os.path.basename(self.background_file)})'
        return f""" {Color.GREEN}*{Color.RESET} Voice: {'Active' if self.voice_available else 'Not available'}
 {Color.GREEN}*{Color.RESET} Sound: {'Active' if self.sound_available else 'Not available'}
 {Color.GREEN}*{Color.RESET} Background: {bg_status}"""

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
            print(f"{Color.GREEN}[+] termux-browser-pilot installed successfully{Color.RESET}")
            return True
        except Exception as e:
            print(f"{Color.RED}[-] Failed to install: {e}{Color.RESET}")
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
                print(f"{Color.CYAN}[*] Browser using proxy{Color.RESET}")
            else:
                os.environ.pop('http_proxy', None)
                os.environ.pop('https_proxy', None)
                print(f"{Color.CYAN}[*] Browser using default IP{Color.RESET}")
            self.browser = Browser(headless=headless)
            self.browser_started = True
            print(f"{Color.GREEN}[+] Browser started successfully{Color.RESET}")
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
    
    def wait_for_text(self, selector, timeout=60):
        if not self.browser_started:
            return None
        try:
            return self.browser.wait_for_text(selector, timeout=timeout)
        except:
            return None
    
    def wait_for_element(self, selector, timeout=60):
        if not self.browser_started:
            return None
        try:
            return self.browser.wait_for_element(selector, timeout=timeout)
        except:
            return None
    
    def screenshot(self, filename):
        if not self.browser_started:
            return False
        try:
            self.browser.screenshot(filename)
            return True
        except:
            return False
    
    def close_browser(self):
        self.browser_started = False
        try:
            self.browser.close()
        except:
            pass

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
    
    def _fill_registration_form(self, phone_number, country_code):
        try:
            first_name, last_name = self.name_generator.get_random_name(country_code)
            full_name = f"{first_name} {last_name}"
            print(f"{Color.CYAN}  [*] Generated name: {full_name} ({country_code}){Color.RESET}")
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
        except Exception as e:
            print(f"{Color.RED}  [-] Form fill error: {e}{Color.RESET}")
            return False
    
    def _request_otp_with_retry(self):
        for attempt in range(FB_CONFIG['MAX_OTP_RETRIES']):
            try:
                print(f"{Color.CYAN}  [*] OTP Attempt {attempt + 1}/{FB_CONFIG['MAX_OTP_RETRIES']}{Color.RESET}")
                otp_text = self.browser_manager.wait_for_text(".otp-code, .verification-code, input[name='otp']", 
                                                             timeout=FB_CONFIG['OTP_WAIT_TIMEOUT'])
                if otp_text:
                    print(f"{Color.GREEN}  [+] OTP received: {otp_text}{Color.RESET}")
                    self.stats['otp_sent'] += 1
                    return otp_text
                if attempt < FB_CONFIG['MAX_OTP_RETRIES'] - 1:
                    print(f"{Color.YELLOW}  [*] Resending OTP...{Color.RESET}")
                    resend_btn = "button:has-text('Resend'), #resend_otp, .resend-btn"
                    self.browser_manager.click(resend_btn)
                    time.sleep(FB_CONFIG['OTP_RETRY_DELAY'])
            except Exception as e:
                print(f"{Color.RED}  [-] OTP error: {e}{Color.RESET}")
                time.sleep(FB_CONFIG['OTP_RETRY_DELAY'])
        print(f"{Color.RED}  [-] OTP failed after {FB_CONFIG['MAX_OTP_RETRIES']} attempts{Color.RESET}")
        return None
    
    def _complete_registration(self, otp_code):
        try:
            print(f"{Color.CYAN}  [*] Entering OTP: {otp_code}{Color.RESET}")
            self.browser_manager.type_text(FB_CONFIG['UI_ELEMENTS']['otp_input'], otp_code)
            time.sleep(1)
            self.browser_manager.click(FB_CONFIG['UI_ELEMENTS']['otp_submit'])
            time.sleep(3)
            return True
        except Exception as e:
            print(f"{Color.RED}  [-] OTP submit error: {e}{Color.RESET}")
            return False
    
    def _process_single_number(self, phone_number):
        print(f"\n{Color.CYAN}[+] Processing: {phone_number}{Color.RESET}")
        proxy, country_code = self.proxy_manager.get_proxy_for_number(phone_number)
        if proxy:
            print(f"{Color.GREEN}[+] Using proxy: {proxy}{Color.RESET}")
        else:
            print(f"{Color.YELLOW}[!] Using default IP{Color.RESET}")
        
        if not self.browser_manager.start_browser(headless=False, proxy=proxy):
            print(f"{Color.RED}  [-] Failed to start browser!{Color.RESET}")
            self.stats['failed'] += 1
            return False
        try:
            print(f"{Color.CYAN}  [*] Navigating to Facebook signup...{Color.RESET}")
            self.browser_manager.goto("https://m.facebook.com/create-account")
            time.sleep(2)
            if not self._fill_registration_form(phone_number, country_code):
                print(f"{Color.RED}  [-] Failed to fill form{Color.RESET}")
                self.stats['failed'] += 1
                return False
            time.sleep(2)
            print(f"{Color.CYAN}  [*] Requesting OTP...{Color.RESET}")
            otp = self._request_otp_with_retry()
            if not otp:
                print(f"{Color.RED}  [-] OTP request failed{Color.RESET}")
                self.stats['failed'] += 1
                if self.audio:
                    self.audio.play_fail()
                    self.audio.speak_otp_fail()
                return False
            if not self._complete_registration(otp):
                print(f"{Color.RED}  [-] OTP submission failed{Color.RESET}")
                self.stats['failed'] += 1
                return False
            print(f"{Color.GREEN}  [+] Successfully processed {phone_number}{Color.RESET}")
            self.stats['success'] += 1
            if self.audio:
                self.audio.play_success()
                self.audio.speak_account_created()
            return True
        except Exception as e:
            print(f"{Color.RED}  [-] Error: {e}{Color.RESET}")
            self.stats['failed'] += 1
            return False
        finally:
            self.browser_manager.close_browser()
    
    def start_batch_processing(self, numbers):
        if not numbers:
            print(f"{Color.RED}[-] No numbers to process{Color.RESET}")
            return
        print(f"\n{Color.GREEN}[+] Starting batch processing{Color.RESET}")
        print(f"{Color.CYAN}[+] Total numbers: {len(numbers)}{Color.RESET}")
        print("-" * 60)
        
        # Check license and credits before starting
        if not self.proxy_manager.license_manager.is_valid:
            print(f"{Color.RED}[-] License not valid. Please enter a valid license key.{Color.RESET}")
            return
        
        if self.proxy_manager.license_manager.credits <= 0:
            print(f"{Color.RED}[-] Insufficient credits. Please add more credits.{Color.RESET}")
            return
        
        print(f"{Color.CYAN}[+] Available credits: {self.proxy_manager.license_manager.credits}{Color.RESET}")
        print(f"{Color.CYAN}[+] Estimated operations: {min(len(numbers), self.proxy_manager.license_manager.credits)}{Color.RESET}")
        
        self.proxy_manager.refresh_proxy_pool()
        self.is_running = True
        
        for idx, phone in enumerate(numbers, 1):
            if not self.is_running:
                break
            
            # Check credits before each operation
            if self.proxy_manager.license_manager.credits <= 0:
                print(f"{Color.RED}[-] No credits left! Stopping...{Color.RESET}")
                break
            
            print(f"\n{Color.GOLD}{'='*50}{Color.RESET}")
            print(f"{Color.GOLD}Processing {idx}/{len(numbers)}{Color.RESET}")
            print(f"{Color.GOLD}{'='*50}{Color.RESET}")
            
            try:
                self._process_single_number(phone)
                self.stats['processed'] += 1
            except Exception as e:
                print(f"{Color.RED}[-] Error: {e}{Color.RESET}")
                self.stats['failed'] += 1
            
            if idx < len(numbers) and self.is_running:
                delay = random.randint(FB_CONFIG['BATCH_DELAY_MIN'], FB_CONFIG['BATCH_DELAY_MAX'])
                print(f"\n{Color.DIM}[*] Waiting {delay}s before next number...{Color.RESET}")
                for remaining in range(delay, 0, -1):
                    if not self.is_running:
                        break
                    if remaining % 10 == 0:
                        print(f"    {remaining}s remaining...")
                    time.sleep(1)
        
        print("\n" + "="*60)
        print(f"{Color.GREEN}BATCH PROCESSING COMPLETE{Color.RESET}")
        print("="*60)
        print(f"Total Processed: {self.stats['processed']}")
        print(f"Success: {Color.GREEN}{self.stats['success']}{Color.RESET}")
        print(f"Failed: {Color.RED}{self.stats['failed']}{Color.RESET}")
        print(f"OTP Sent: {self.stats['otp_sent']}")
        print(f"Remaining Credits: {self.proxy_manager.license_manager.credits}")
        print("="*60)
        if self.audio:
            self.audio.play_done()
            self.audio.speak_bot_complete()
        self.is_running = False
    
    def stop(self):
        print(f"\n{Color.YELLOW}[!] Stopping automation...{Color.RESET}")
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
    
    def get_status(self):
        s = 'RUNNING' if self.running else 'STOPPED'
        return f'\n{Color.CYAN}Numbers: {len(self.numbers)} | Success: {self.stats["success"]} | Failed: {self.stats["failed"]} | Status: {s}{Color.RESET}'
    
    def run_bot(self, workers=1):
        if not self.numbers:
            print(f'\n{Color.RED}[-] No numbers found in numbers.txt{Color.RESET}')
            return
        self.running = True
        self.stats = {'success': 0, 'failed': 0, 'total': 0}
        print(f'\n{Color.GREEN}[+] Starting bot{Color.RESET}')
        print(f'{Color.CYAN}Total numbers: {len(self.numbers)}{Color.RESET}')
        print(f'{Color.YELLOW}[!] Press 0 and Enter to stop{Color.RESET}')
        print("-" * 60)
        self.automation_engine = FacebookAutomationEngine()
        self.automation_engine.audio = self.audio
        self.automation_engine.start_batch_processing(self.numbers)
        self.running = False
        print(f'\n\n{Color.GREEN}[+] ALL TASKS COMPLETE{Color.RESET}')
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
    def spinner(duration=2, message=''):
        spin = ['-', '\\', '|', '/']
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f'\r{Color.CYAN}{spin[i % len(spin)]}{Color.RESET} {message}', end='', flush=True)
            i += 1
            time.sleep(0.1)
        print()
    
    @staticmethod
    def progress_bar(duration=3, message='Loading'):
        for i in range(21):
            progress = '#' * i + '-' * (20 - i)
            percent = i * 5
            print(f'\r{Color.CYAN}{message}: [{progress}] {percent}%{Color.RESET}', end='', flush=True)
            time.sleep(duration / 20)
        print()
    
    @staticmethod
    def matrix_effect(duration=2):
        chars = '01'
        end_time = time.time() + duration
        while time.time() < end_time:
            line = ''.join(random.choice(chars) if random.random() < 0.7 else ' ' for _ in range(40))
            print(f'\r{Color.GREEN}{line}{Color.RESET}')
            time.sleep(0.05)
    
    @staticmethod
    def ending_animation():
        print(f'\n{Color.CYAN}')
        print('    ╔══════════════════════════════════════════════╗')
        print('    ║     Thank you for using Ridol FB Tool        ║')
        print(f'    ║     {Color.YELLOW}Stay Secure!{Color.CYAN}                              ║')
        print('    ╚══════════════════════════════════════════════╝')
        print(f'{Color.RESET}')
        for i in range(3):
            print(f'\r{Color.DIM}Shutting down{"." * (i+1)}{" " * (3-i)}{Color.RESET}', end='', flush=True)
            time.sleep(0.5)
        print()

# ==================== MAIN MENU ====================
class MainMenu:
    def __init__(self):
        self.browser_manager = BrowserPilotManager()
        self.proxy_manager = ProxyManager()
        self.audio = AudioEngine()
        self.bot = None
        self.config = load_json(CONFIG_FILE)
        self.data_dir = self.config.get('data_dir', '/storage/emulated/0/Download/Ridol FB Tool')
        self.browser_ready = self.config.get('browser_ready', False)
        self.bot_running = False
        
        # Initialize license from config
        license_key = self.config.get('license_key', '')
        if license_key:
            self.proxy_manager.license_manager.verify(license_key)
    
    def show_header(self):
        clear_screen()
        TitleAnimation.compact_banner()
        proxy_stats = self.proxy_manager.get_proxy_stats()
        license_status = self.proxy_manager.license_manager.get_status()
        
        # Proxy status
        proxy_count = proxy_stats.get('total', 0)
        proxy_status = f"● {proxy_count} proxies"
        proxy_color = Color.GREEN if proxy_count > 0 else Color.RED
        
        # IP Connect status
        ip_connected = proxy_stats.get('ip_connected', False)
        ip_status = "● CONNECTED" if ip_connected else "● DISCONNECTED"
        ip_color = Color.GREEN if ip_connected else Color.RED
        
        # License status
        license_valid = license_status.get('valid', False)
        lic_status = "● ACTIVE" if license_valid else "● INACTIVE"
        lic_color = Color.GREEN if license_valid else Color.RED
        
        # Credits
        credits = license_status.get('credits', 0)
        credits_color = Color.GREEN if credits > 100 else Color.YELLOW if credits > 10 else Color.RED
        
        # Server status
        server_online = check_server_status()
        server_status = "ONLINE" if server_online else "OFFLINE"
        server_color = Color.GREEN if server_online else Color.RED
        
        # User ID
        user_id = license_status.get('user_id', '')
        user_display = f"User: {user_id}" if user_id else "User: None"
        
        print(f' {proxy_color}{proxy_status}{Color.RESET} Proxy Pool: {Color.WHITE}{"Ready" if proxy_count > 0 else "Empty"}{Color.RESET}')
        print(f' {ip_color}{ip_status}{Color.RESET} IP Connect: {Color.WHITE}{"Connected" if ip_connected else "Disconnected"} | {user_display}{Color.RESET}')
        print(f' {lic_color}{lic_status}{Color.RESET} License: {Color.WHITE}{"Valid" if license_valid else "Invalid"}{Color.RESET}')
        print(f' {credits_color}● Credits: {credits}{Color.RESET}')
        print(f' {Color.CYAN}◉{Color.RESET} Server: {server_color}{server_status}{Color.RESET}\n')
    
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
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        inp = sys.stdin.read(1).strip()
                        if inp == '0':
                            print(f"\n\n{Color.YELLOW}[!] Stop command received! Stopping bot...{Color.RESET}")
                            self.bot_running = False
                            if self.bot and self.bot.automation_engine:
                                self.bot.automation_engine.stop()
                            self.audio.speak_stopping()
                            break
            except:
                pass
            time.sleep(0.5)
    
    def menu_license(self):
        """License management menu"""
        while True:
            self.show_header()
            status = self.proxy_manager.license_manager.get_status()
            
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}LICENSE MANAGEMENT{Color.RESET}{Color.CYAN}                           ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Status: {Color.WHITE}{"● Active" if status['valid'] else "● Inactive"}{Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.WHITE}{status['license_key'][:20] + '...' if status['license_key'] else 'None'}{Color.RESET}{Color.CYAN}  ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Credits: {Color.WHITE}{status['credits']}{Color.RESET}{Color.CYAN}                              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Used: {Color.WHITE}{status['used_credits']}{Color.RESET}{Color.CYAN}                              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Max Browsers: {Color.WHITE}{status['max_browsers']}{Color.RESET}{Color.CYAN}                      ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  User ID: {Color.WHITE}{status.get('user_id', 'None')}{Color.RESET}{Color.CYAN}                        ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Expires: {Color.WHITE}{status.get('expires_at', 'N/A')[:10] if status.get('expires_at') else 'N/A'}{Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Enter License Key               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Check License Status            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            
            if choice == '1':
                key = input(f'  {Color.CYAN}Enter license key (RIDOL-XXXX-XXXX-XXXX-XXXX): {Color.RESET}').strip().upper()
                if key:
                    valid, data = self.proxy_manager.license_manager.verify(key)
                    if valid:
                        print(f'  {Color.GREEN}[+] License verified!{Color.RESET}')
                        print(f'  {Color.CYAN}[+] Credits: {data.get("credits")}{Color.RESET}')
                        print(f'  {Color.CYAN}[+] Max Browsers: {data.get("max_browsers")}{Color.RESET}')
                        self.audio.speak_license_verified()
                    else:
                        print(f'  {Color.RED}[-] {data.get("error", "Invalid license")}{Color.RESET}')
                press_enter()
                
            elif choice == '2':
                if self.proxy_manager.license_manager.license_key:
                    status = self.proxy_manager.license_manager.check_status()
                    if status.get('valid'):
                        print(f'  {Color.GREEN}[+] License Active{Color.RESET}')
                        print(f'  {Color.CYAN}Credits: {status.get("credits")}{Color.RESET}')
                        print(f'  {Color.CYAN}Used: {status.get("used_credits")}{Color.RESET}')
                        print(f'  {Color.CYAN}Max Browsers: {status.get("max_browsers")}{Color.RESET}')
                        print(f'  {Color.CYAN}User ID: {status.get("user_id", "None")}{Color.RESET}')
                        print(f'  {Color.CYAN}Expires: {status.get("expires_at", "N/A")[:10]}{Color.RESET}')
                    else:
                        print(f'  {Color.RED}[-] {status.get("error", "License invalid or expired")}{Color.RESET}')
                else:
                    print(f'  {Color.YELLOW}[!] No license key set{Color.RESET}')
                press_enter()
                
            elif choice == '0':
                break
            else:
                print(f'{Color.RED}Invalid!{Color.RESET}')
                press_enter()
    
    def menu_main(self):
        self.welcome_screen()
        while True:
            self.show_header()
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}MAIN MENU - LICENSE & CREDIT SYSTEM{Color.RESET}{Color.CYAN}          ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Browser Pilot Setup             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} License Management              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Data Folder                     {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Start Bot                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[5]{Color.RESET} Status                           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[6]{Color.RESET} Audio Settings                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[7]{Color.RESET} Demo                             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[8]{Color.RESET} Help                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                self.menu_browser()
            elif choice == '2':
                self.menu_license()
            elif choice == '3':
                self.menu_folder()
            elif choice == '4':
                self.menu_start_bot()
            elif choice == '5':
                self.menu_status()
            elif choice == '6':
                self.menu_audio()
            elif choice == '7':
                self.menu_demo()
            elif choice == '8':
                self.menu_help()
            elif choice == '0':
                self.menu_exit()
                break
            else:
                print(f'{Color.RED}Invalid!{Color.RESET}')
                press_enter()
    
    def menu_browser(self):
        while True:
            self.show_header()
            browser_available = self.browser_manager.browser_available
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}BROWSER PILOT SETUP{Color.RESET}{Color.CYAN}                          ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Status: {Color.WHITE}{"● Installed" if browser_available else "○ Not Installed"}{Color.RESET}{Color.CYAN}       ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Install Browser Pilot            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Test Browser Launch              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Test Facebook Navigation         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                print(f'  {Color.CYAN}[*] Installing termux-browser-pilot...{Color.RESET}')
                success = self.browser_manager._install_browser_pilot()
                if success:
                    self.browser_manager.browser_available = True
                    print(f'  {Color.GREEN}[+] Installation complete!{Color.RESET}')
                press_enter()
            elif choice == '2':
                print(f'  {Color.CYAN}[*] Testing browser launch...{Color.RESET}')
                success = self.browser_manager.start_browser(headless=False)
                if success:
                    print(f'  {Color.GREEN}[+] Browser launched successfully!{Color.RESET}')
                    time.sleep(3)
                    self.browser_manager.close_browser()
                press_enter()
            elif choice == '3':
                print(f'  {Color.CYAN}[*] Testing Facebook navigation...{Color.RESET}')
                if self.browser_manager.start_browser(headless=False):
                    self.browser_manager.goto("https://m.facebook.com")
                    time.sleep(3)
                    print(f'  {Color.GREEN}[+] Navigation successful!{Color.RESET}')
                    self.browser_manager.screenshot("test_facebook.png")
                    print(f'  {Color.DIM}[*] Screenshot saved: test_facebook.png{Color.RESET}')
                    time.sleep(2)
                    self.browser_manager.close_browser()
                press_enter()
            elif choice == '0':
                break
            else:
                print(f'{Color.RED}Invalid!{Color.RESET}')
                press_enter()
    
    def menu_folder(self):
        while True:
            self.show_header()
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}DATA FOLDER{Color.RESET}{Color.CYAN}                                   ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Select Folder (Check/Connect)    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} View Folder Contents             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Set New Path                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Create Required Files           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                folder_path = self.data_dir
                if os.path.exists(folder_path):
                    print(f'\n  {Color.GREEN}[+] Folder found: {folder_path}{Color.RESET}')
                    self.audio.speak_folder_found()
                    numbers_file = os.path.join(folder_path, 'numbers.txt')
                    if os.path.exists(numbers_file):
                        try:
                            with open(numbers_file, 'r') as f:
                                count = sum(1 for line in f if line.strip() and not line.startswith('#'))
                            print(f'  {Color.CYAN}[*] numbers.txt contains {count} numbers{Color.RESET}')
                        except:
                            print(f'  {Color.YELLOW}[!] Could not read numbers.txt{Color.RESET}')
                    else:
                        print(f'  {Color.YELLOW}[!] numbers.txt not found{Color.RESET}')
                else:
                    print(f'\n  {Color.RED}[-] Folder not found: {folder_path}{Color.RESET}')
                    self.audio.speak_folder_not_found()
                press_enter()
            elif choice == '2':
                folder_path = self.data_dir
                if os.path.exists(folder_path):
                    print(f'\n  {Color.GREEN}[+] Folder contents: {folder_path}{Color.RESET}')
                    self.audio.speak_content_found()
                    try:
                        files = os.listdir(folder_path)
                        txt_files = [f for f in files if f.endswith('.txt')]
                        if txt_files:
                            print(f'  {Color.CYAN}[*] Found {len(txt_files)} text files:{Color.RESET}')
                            for txt in txt_files:
                                filepath = os.path.join(folder_path, txt)
                                try:
                                    with open(filepath, 'r') as f:
                                        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                                    print(f'    {Color.WHITE}{txt}{Color.RESET}: {len(lines)} entries')
                                except:
                                    print(f'    {Color.WHITE}{txt}{Color.RESET}: (error reading)')
                        else:
                            print(f'  {Color.YELLOW}[!] No .txt files found{Color.RESET}')
                            self.audio.speak_content_not_found()
                    except:
                        print(f'  {Color.RED}[-] Error reading folder contents{Color.RESET}')
                        self.audio.speak_content_not_found()
                else:
                    print(f'\n  {Color.RED}[-] Folder not found: {folder_path}{Color.RESET}')
                    self.audio.speak_folder_not_found()
                press_enter()
            elif choice == '3':
                new_path = input(f'  {Color.CYAN}Enter new data directory path: {Color.RESET}').strip()
                if new_path:
                    self.data_dir = new_path
                    self.config['data_dir'] = new_path
                    save_json(CONFIG_FILE, self.config)
                    print(f'  {Color.GREEN}[+] Data directory updated{Color.RESET}')
                press_enter()
            elif choice == '4':
                os.makedirs(self.data_dir, exist_ok=True)
                for fname in ['numbers.txt', 'names.txt', 'proxies.txt']:
                    fpath = os.path.join(self.data_dir, fname)
                    if not os.path.exists(fpath):
                        with open(fpath, 'w') as f:
                            f.write(f'# {fname} - Add your data here\n')
                print(f'  {Color.GREEN}[+] Required files created in {self.data_dir}{Color.RESET}')
                press_enter()
            elif choice == '0':
                break
            else:
                print(f'{Color.RED}Invalid!{Color.RESET}')
                press_enter()
    
    def menu_start_bot(self):
        self.show_header()
        folder_path = self.data_dir
        folder_exists = os.path.exists(folder_path)
        license_status = self.proxy_manager.license_manager.get_status()
        
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}START BOT{Color.RESET}{Color.CYAN}                                        ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Numbers: {len(load_file_lines(os.path.join(self.data_dir, "numbers.txt")))}                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.DIM}{"Active" if license_status.get('valid') else "Inactive"}{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Credits: {Color.DIM}{license_status.get('credits', 0)}{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Browser: {Color.DIM}{"● Ready" if self.browser_manager.browser_available else "○ Not installed"}{Color.RESET}{Color.CYAN}    ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Folder Status: {Color.DIM}{"✓ Exists" if folder_exists else "✗ Not found"}{Color.RESET}{Color.CYAN}        ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        
        if not folder_exists:
            print(f'\n{Color.RED}[-] Data folder not found!{Color.RESET}')
            self.audio.speak_folder_not_found()
            press_enter()
            return
        
        if not license_status.get('valid'):
            print(f'\n{Color.RED}[-] License not valid! Please enter a valid license key.{Color.RESET}')
            print(f'  {Color.DIM}Go to License Management -> Enter License Key{Color.RESET}')
            press_enter()
            return
        
        if license_status.get('credits', 0) <= 0:
            print(f'\n{Color.RED}[-] Insufficient credits! Please add more credits.{Color.RESET}')
            press_enter()
            return
        
        if not self.browser_manager.browser_available:
            print(f'\n{Color.RED}[-] Browser Pilot not installed!{Color.RESET}')
            print(f'{Color.YELLOW}[!] Go to Main Menu -> 1. Browser Pilot Setup -> 1. Install Browser Pilot{Color.RESET}')
            press_enter()
            return
        
        workers = input(f'\n {Color.CYAN}Number of workers [1-5, default 1]: {Color.RESET}').strip()
        try:
            workers = int(workers) if workers else 1
            workers = max(1, min(5, workers))
        except:
            workers = 1
        
        print(f'\n{Color.YELLOW}[!] Press 0 and Enter to stop the bot{Color.RESET}')
        print(f'{Color.CYAN}[+] Each operation will consume 1 credit{Color.RESET}')
        print(f'{Color.CYAN}[+] Available credits: {license_status.get("credits", 0)}{Color.RESET}')
        
        self.bot_running = True
        stop_thread = threading.Thread(target=self.check_stop_input, daemon=True)
        stop_thread.start()
        
        self.bot = FacebookBot(self.data_dir, '', self.audio)
        self.audio.speak_bot_starting()
        self.bot.run_bot(workers)
        
        self.bot_running = False
        time.sleep(1)
        print(f'\n{Color.GREEN}[+] Returned to main menu{Color.RESET}')
        press_enter()
    
    def menu_status(self):
        self.show_header()
        proxy_stats = self.proxy_manager.get_proxy_stats()
        license_status = self.proxy_manager.license_manager.get_status()
        
        server_online = check_server_status()
        server_status = "ONLINE" if server_online else "OFFLINE"
        server_color = Color.GREEN if server_online else Color.RED
        
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}SYSTEM STATUS{Color.RESET}{Color.CYAN}                                 ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Browser Pilot: {Color.WHITE}{"Available" if self.browser_manager.browser_available else "Not installed"}{Color.RESET}{Color.CYAN} ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Proxy Pool: {Color.WHITE}{proxy_stats["total"]} proxies{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} IP Connected: {Color.WHITE}{'Yes' if proxy_stats.get('ip_connected') else 'No'}{Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} License: {Color.WHITE}{"Active" if license_status.get('valid') else "Inactive"}{Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Credits: {Color.WHITE}{license_status.get('credits', 0)}{Color.RESET}{Color.CYAN}                          ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Used Credits: {Color.WHITE}{license_status.get('used_credits', 0)}{Color.RESET}{Color.CYAN}                    ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Data Dir: {Color.WHITE}{self.data_dir}{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {self.audio.get_status()}{Color.CYAN}         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Automation: {Color.WHITE}{"Running" if self.bot and self.bot.running else "Idle"}{Color.RESET}{Color.CYAN}          ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Server: {server_color}{server_status}{Color.RESET}{Color.CYAN}                        ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        
        if self.bot:
            print(self.bot.get_status())
        press_enter()
    
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
            elif choice == '0':
                break
            else:
                print(f'{Color.RED}Invalid!{Color.RESET}')
                press_enter()
    
    def menu_demo(self):
        self.show_header()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}DEMO{Color.RESET}{Color.CYAN}                                      ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Matrix Rain Animation            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Sound Effects Demo              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Voice Messages Demo             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Progress Bar Demo               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[5]{Color.RESET} Typing Effect Demo              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
        self.audio.play_click()
        if choice == '1':
            Animation.matrix_effect(3)
            press_enter()
        elif choice == '2':
            self.audio.play_startup()
            time.sleep(0.5)
            self.audio.play_click()
            time.sleep(0.5)
            self.audio.play_success()
            time.sleep(0.5)
            self.audio.play_fail()
            time.sleep(0.5)
            self.audio.play_done()
            press_enter()
        elif choice == '3':
            self.audio.speak_welcome()
            time.sleep(1)
            self.audio.speak_success()
            time.sleep(1)
            self.audio.speak_goodbye()
            press_enter()
        elif choice == '4':
            Animation.progress_bar(3, 'Demo Progress')
            press_enter()
        elif choice == '5':
            Animation.typing('This is a typing effect demo!', 0.05, Color.GOLD)
            press_enter()
        elif choice == '0':
            pass
        else:
            print(f'{Color.RED}Invalid!{Color.RESET}')
            press_enter()
    
    def menu_help(self):
        self.show_header()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}HELP - LICENSE & CREDIT SYSTEM{Color.RESET}{Color.CYAN}                  ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [?] {Color.WHITE}How It Works{Color.RESET}{Color.CYAN}                                ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  1. Get a license key from admin                     {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  2. Enter license key in License Management         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  3. License has credits (e.g., 1000)                {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  4. Each IP request consumes 1 credit               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  5. Bot gets IP from server using Cliproxy API     {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  6. No separate proxy setup needed                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [#] {Color.WHITE}Features{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Credit based system (pay per use)               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Auto country detection from phone number         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Auto name generation by country                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - OTP retry with voice feedback                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Stop bot with '0' key                            {Color.CYAN}║{Color.RESET}
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
            print(f'{Color.GREEN}[+] mpv found - MP3 support enabled{Color.RESET}')
        except:
            print(f'{Color.YELLOW}[!] mpv not found - install: pkg install mpv{Color.RESET}')
            print(f'{Color.YELLOW}[!] Only WAV files will play{Color.RESET}')
        
        print(f'{Color.CYAN}[*] Initializing...{Color.RESET}')
        download_all_sounds()
        download_custom_background()
        time.sleep(1)
        menu = MainMenu()
        menu.menu_main()
    except KeyboardInterrupt:
        print(f'\n\n{Color.YELLOW}[!] Interrupted by user{Color.RESET}')
        sys.exit(0)
    except Exception as e:
        print(f'\n{Color.RED}[-] Error: {e}{Color.RESET}')
        sys.exit(1)