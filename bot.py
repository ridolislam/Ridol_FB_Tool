#!/usr/bin/env python3
"""
Ridol FB Tool v7.0 - Proxy Rotation & Auto Name Generation
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

# ==================== PROXY CONFIG ====================
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

# ==================== COUNTRY CODES ====================
COUNTRY_CODES = {
    # Asia
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
    # Europe
    '355': 'AL', '376': 'AD', '43': 'AT', '375': 'BY', '32': 'BE',
    '387': 'BA', '359': 'BG', '385': 'HR', '357': 'CY', '420': 'CZ',
    '45': 'DK', '372': 'EE', '358': 'FI', '33': 'FR', '995': 'GE',
    '49': 'DE', '30': 'GR', '36': 'HU', '354': 'IS', '353': 'IE',
    '39': 'IT', '371': 'LV', '423': 'LI', '370': 'LT', '352': 'LU',
    '389': 'MK', '356': 'MT', '373': 'MD', '377': 'MC', '382': 'ME',
    '31': 'NL', '47': 'NO', '48': 'PL', '351': 'PT', '40': 'RO',
    '7': 'RU', '381': 'RS', '421': 'SK', '386': 'SI', '34': 'ES',
    '46': 'SE', '41': 'CH', '380': 'UA', '44': 'GB', '379': 'VA',
    # North America
    '1': 'US', '52': 'MX', '501': 'BZ', '506': 'CR', '53': 'CU',
    '1': 'DM', '1': 'DO', '503': 'SV', '502': 'GT', '504': 'HN',
    '1': 'JM', '505': 'NI', '507': 'PA', '1': 'TT', '1': 'BS',
    '1': 'BB', '1': 'GD', '1': 'LC', '1': 'VC',
    # South America
    '54': 'AR', '591': 'BO', '55': 'BR', '56': 'CL', '57': 'CO',
    '593': 'EC', '592': 'GY', '595': 'PY', '51': 'PE', '597': 'SR',
    '598': 'UY', '58': 'VE',
    # Africa
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
    # Oceania
    '61': 'AU', '679': 'FJ', '686': 'KI', '692': 'MH', '691': 'FM',
    '674': 'NR', '64': 'NZ', '675': 'PG', '685': 'WS', '677': 'SB',
    '676': 'TO', '688': 'TV', '678': 'VU',
    # Default
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
            'first': ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fitri', 'Gilang', 'Hana', 'Indra', 'Joko'],
            'last': ['Siregar', 'Nasution', 'Harahap', 'Lubis', 'Batubara', 'Sinaga', 'Saragih', 'Ginting']
        },
        'US': {
            'first': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles'],
            'last': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        },
        'GB': {
            'first': ['Oliver', 'George', 'Harry', 'Jack', 'Jacob', 'Charlie', 'Thomas', 'James', 'William', 'Muhammad'],
            'last': ['Smith', 'Jones', 'Williams', 'Taylor', 'Brown', 'Davies', 'Evans', 'Thomas', 'Johnson', 'Roberts']
        },
        'IN': {
            'first': ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Pranav', 'Dhruv', 'Aryan', 'Reyansh'],
            'last': ['Sharma', 'Verma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Gandhi', 'Prasad', 'Sinha']
        },
        'BD': {
            'first': ['Mohammad', 'Abdullah', 'Rafiq', 'Shahid', 'Kamal', 'Jamal', 'Rahim', 'Karim', 'Hasan', 'Ali'],
            'last': ['Rahman', 'Ahmed', 'Islam', 'Hossain', 'Ali', 'Khan', 'Haque', 'Sarkar', 'Mia', 'Pramanik']
        },
        'PK': {
            'first': ['Muhammad', 'Ali', 'Ahmed', 'Hassan', 'Usman', 'Omar', 'Zain', 'Hamza', 'Bilal', 'Raza'],
            'last': ['Khan', 'Malik', 'Akhtar', 'Shah', 'Chaudhry', 'Butt', 'Qureshi', 'Sheikh', 'Abbasi', 'Javed']
        },
        'PH': {
            'first': ['Jose', 'Juan', 'Carlos', 'Ramon', 'Pedro', 'Andres', 'Emilio', 'Josefino', 'Ronaldo', 'Ferdinand'],
            'last': ['Santos', 'Reyes', 'Cruz', 'Garcia', 'Martinez', 'Lopez', 'Gonzales', 'Flores', 'Perez', 'Ramos']
        },
        'MY': {
            'first': ['Ahmad', 'Mohd', 'Abdullah', 'Ali', 'Hassan', 'Zainal', 'Kamarul', 'Azman', 'Razali', 'Idris'],
            'last': ['Abdullah', 'Ali', 'Hassan', 'Ahmad', 'Mohd', 'Ismail', 'Othman', 'Rahman', 'Hussein', 'Yusof']
        },
        'SG': {
            'first': ['Wei', 'Ming', 'Li', 'Xin', 'Yi', 'Jun', 'Hui', 'Ling', 'Yan', 'Hao'],
            'last': ['Tan', 'Lim', 'Lee', 'Ng', 'Wong', 'Ong', 'Goh', 'Chua', 'Koh', 'Chew']
        },
        'TH': {
            'first': ['Somchai', 'Somsak', 'Prasert', 'Kriangkrai', 'Pongsak', 'Nattaporn', 'Wichian', 'Somkiat', 'Suthep', 'Anuchit'],
            'last': ['Somchai', 'Somsak', 'Prasert', 'Kriangkrai', 'Pongsak', 'Nattaporn', 'Wichian', 'Somkiat', 'Suthep', 'Anuchit']
        },
        'VN': {
            'first': ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Bui', 'Do', 'Huynh'],
            'last': ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Bui', 'Do', 'Huynh']
        },
        'AE': {
            'first': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Omar', 'Khalid', 'Saeed', 'Abdulla', 'Rashid', 'Hamad'],
            'last': ['Al Maktoum', 'Al Nahyan', 'Al Suwaidi', 'Al Tayer', 'Al Ghurair', 'Al Habtoor', 'Al Futtaim']
        },
        'SA': {
            'first': ['Mohammed', 'Ahmed', 'Ali', 'Abdullah', 'Omar', 'Saud', 'Khalid', 'Sultan', 'Faisal', 'Nayef'],
            'last': ['Al Saud', 'Al Thani', 'Al Otaibi', 'Al Harbi', 'Al Anzi', 'Al Shamrani', 'Al Mutairi']
        },
        'TR': {
            'first': ['Mehmet', 'Ahmet', 'Ali', 'Mustafa', 'Hasan', 'Huseyin', 'Osman', 'Yusuf', 'Ibrahim', 'Ismail'],
            'last': ['Yilmaz', 'Kaya', 'Demir', 'Celik', 'Aydin', 'Ozdemir', 'Arslan', 'Dogan', 'Kilic', 'Yildirim']
        },
        'RU': {
            'first': ['Alexander', 'Dmitri', 'Ivan', 'Mikhail', 'Nikolai', 'Sergei', 'Vladimir', 'Yuri', 'Andrei', 'Pavel'],
            'last': ['Ivanov', 'Petrov', 'Sidorov', 'Kuznetsov', 'Smirnov', 'Popov', 'Sokolov', 'Lebedev', 'Kozlov', 'Novikov']
        },
        'BR': {
            'first': ['Joao', 'Jose', 'Maria', 'Antonio', 'Francisco', 'Carlos', 'Paulo', 'Pedro', 'Lucas', 'Gabriel'],
            'last': ['Silva', 'Santos', 'Souza', 'Oliveira', 'Pereira', 'Costa', 'Rodrigues', 'Almeida', 'Nascimento', 'Lima']
        },
        'JP': {
            'first': ['Haruto', 'Sota', 'Yuki', 'Riku', 'Hinata', 'Sakura', 'Hana', 'Yui', 'Mio', 'Rin'],
            'last': ['Sato', 'Suzuki', 'Takahashi', 'Tanaka', 'Watanabe', 'Ito', 'Yamamoto', 'Nakamura', 'Kobayashi', 'Kato']
        },
        'CN': {
            'first': ['Wei', 'Ming', 'Li', 'Xin', 'Yi', 'Jun', 'Hui', 'Ling', 'Yan', 'Hao'],
            'last': ['Wang', 'Li', 'Zhang', 'Liu', 'Chen', 'Yang', 'Huang', 'Zhao', 'Wu', 'Zhou']
        },
        'DE': {
            'first': ['Hans', 'Peter', 'Klaus', 'Wolfgang', 'Thomas', 'Andreas', 'Michael', 'Stefan', 'Markus', 'Daniel'],
            'last': ['Muller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker', 'Schulz', 'Hoffmann']
        },
        'FR': {
            'first': ['Jean', 'Pierre', 'Michel', 'Philippe', 'Alain', 'Bernard', 'Eric', 'Nicolas', 'David', 'Christophe'],
            'last': ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau']
        },
        'IT': {
            'first': ['Marco', 'Giuseppe', 'Antonio', 'Giovanni', 'Francesco', 'Andrea', 'Luca', 'Mario', 'Paolo', 'Roberto'],
            'last': ['Rossi', 'Russo', 'Ferrari', 'Esposito', 'Bianchi', 'Romano', 'Colombo', 'Ricci', 'Marino', 'Greco']
        },
        'ES': {
            'first': ['Antonio', 'Jose', 'Manuel', 'Francisco', 'Juan', 'David', 'Javier', 'Carlos', 'Daniel', 'Luis'],
            'last': ['Garcia', 'Rodriguez', 'Gonzalez', 'Fernandez', 'Lopez', 'Martinez', 'Sanchez', 'Perez', 'Gomez', 'Martin']
        },
        'NL': {
            'first': ['Jan', 'Peter', 'Hans', 'Kees', 'Pieter', 'Johan', 'Willem', 'Hendrik', 'Dirk', 'Gerard'],
            'last': ['De Jong', 'Jansen', 'De Vries', 'Van den Berg', 'Van Dijk', 'Bakker', 'Janssen', 'Visser', 'Smit', 'Meijer']
        },
        'AU': {
            'first': ['Jack', 'Oliver', 'William', 'James', 'Thomas', 'Liam', 'Noah', 'Ethan', 'Lucas', 'Mason'],
            'last': ['Smith', 'Jones', 'Williams', 'Brown', 'Wilson', 'Taylor', 'Johnson', 'White', 'Martin', 'Anderson']
        },
        'ZA': {
            'first': ['Nelson', 'Jacob', 'Cyril', 'Thabo', 'Kofi', 'Mandela', 'Desmond', 'Winnie', 'Graça', 'Miriam'],
            'last': ['Mbeki', 'Zuma', 'Ramaphosa', 'Tambo', 'Machel', 'Tutu', 'Sisulu', 'Motlanthe', 'Msimang', 'Madikizela']
        },
        'EG': {
            'first': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Omar', 'Mahmoud', 'Tarek', 'Khaled', 'Amr', 'Youssef'],
            'last': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Mahmoud', 'Tarek', 'Khaled', 'Amr', 'Youssef', 'Ibrahim']
        },
        'NG': {
            'first': ['Oluwaseun', 'Chukwudi', 'Adebayo', 'Olayinka', 'Emeka', 'Chidi', 'Adeola', 'Babatunde', 'Olumide', 'Segun'],
            'last': ['Adeyemi', 'Ogunlade', 'Bamidele', 'Okonkwo', 'Eze', 'Nwosu', 'Okafor', 'Igwe', 'Umeh', 'Obi']
        },
        'XX': {
            'first': ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Hayden', 'Harper'],
            'last': ['Chen', 'Singh', 'Garcia', 'Wang', 'Perez', 'Nguyen', 'Patel', 'Smith', 'Jones', 'Williams']
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
    """Manage proxy - Connects with Cliproxy All region and auto-switches based on country"""
    
    def __init__(self):
        self.proxy_pool = []
        self.current_proxy = None
        self.current_country = None
        self.proxy_history = []
        self.api_key = PROXY_API_KEY
        self.last_refresh = 0
        self.refresh_interval = 300
        self.use_default_ip = True
        self.connected_ip_url = None
        self.ip_connected = False
        self.base_username = 'ridolislam-region'
        self.password = 'Ridol123'
        self.host = 'sg.cliproxy.io'
        self.port = '3010'
        self.user_id = None  # Will store connected user ID
        
    def _get_country_from_phone(self, phone_number):
        phone = phone_number.strip().replace('+', '').replace(' ', '').replace('-', '')
        for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
            if phone.startswith(code):
                return COUNTRY_CODES[code]
        return 'XX'
    
    def connect_ip(self, ip_url):
        """Connect to a specific IP URL and extract user ID"""
        try:
            print(f"{Color.CYAN}[*] Connecting to IP: {ip_url}{Color.RESET}")
            
            # Extract user ID from URL
            # Format: socks5://ridolislam-region-XX:Ridol123@sg.cliproxy.io:3010
            match = re.search(r'ridolislam-region-([A-Z]+):', ip_url)
            if match:
                self.user_id = match.group(1)
                print(f"{Color.GREEN}[+] User ID: {self.user_id}{Color.RESET}")
            else:
                # Try to extract any username
                match2 = re.search(r'socks5://([^:]+):', ip_url)
                if match2:
                    self.user_id = match2.group(1)
                    print(f"{Color.GREEN}[+] User ID: {self.user_id}{Color.RESET}")
                else:
                    self.user_id = 'Connected'
            
            # Test the connection
            test_proxies = {'http': ip_url, 'https': ip_url}
            response = requests.get('http://ip-api.com/json', proxies=test_proxies, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"{Color.GREEN}[+] IP Connected Successfully!{Color.RESET}")
                print(f"{Color.CYAN}[+] IP: {data.get('query', 'Unknown')}{Color.RESET}")
                print(f"{Color.CYAN}[+] Country: {data.get('countryCode', 'Unknown')}{Color.RESET}")
                print(f"{Color.CYAN}[+] Region: {data.get('regionName', 'Unknown')}{Color.RESET}")
                print(f"{Color.CYAN}[+] ISP: {data.get('isp', 'Unknown')}{Color.RESET}")
                print(f"{Color.CYAN}[+] User ID: {self.user_id}{Color.RESET}")
                
                self.connected_ip_url = ip_url
                self.ip_connected = True
                return True
            else:
                print(f"{Color.RED}[-] Failed to connect to IP. Status: {response.status_code}{Color.RESET}")
                return False
                
        except Exception as e:
            print(f"{Color.RED}[-] Connection failed: {e}{Color.RESET}")
            return False
    
    def disconnect_ip(self):
        """Disconnect current IP"""
        self.connected_ip_url = None
        self.ip_connected = False
        self.user_id = None
        print(f"{Color.YELLOW}[!] IP Disconnected{Color.RESET}")
        return True
    
    def get_proxy_for_country(self, country_code):
        """Generate proxy URL for a specific country"""
        if not self.ip_connected or not self.connected_ip_url:
            print(f"{Color.YELLOW}[!] No IP connected. Please connect first.{Color.RESET}")
            return None
        
        # Extract base URL and replace region
        # Original: socks5://ridolislam-region-XX:Ridol123@sg.cliproxy.io:3010
        # Replace XX with country code
        base_url = self.connected_ip_url
        # Replace region in URL
        new_url = re.sub(r'ridolislam-region-[A-Z]+:', f'ridolislam-region-{country_code}:', base_url)
        
        return new_url
    
    def refresh_proxy_pool(self):
        """Refresh proxy pool"""
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
        """Get proxy based on phone number's country code"""
        country_code = self._get_country_from_phone(phone_number)
        print(f"{Color.CYAN}[+] Country detected: {country_code}{Color.RESET}")
        
        # Use connected IP with country-specific region
        if self.connected_ip_url and self.ip_connected:
            # Generate country-specific proxy URL
            proxy_url = self.get_proxy_for_country(country_code)
            if proxy_url:
                print(f"{Color.GREEN}[+] Generated proxy for {country_code}: {proxy_url}{Color.RESET}")
                self.current_proxy = proxy_url
                self.current_country = country_code
                self.proxy_history.append({
                    'phone': phone_number,
                    'proxy': proxy_url,
                    'country': country_code,
                    'type': 'cliproxy'
                })
                return proxy_url, country_code
        
        # Fallback: Use default IP
        print(f"{Color.YELLOW}[!] No IP connected or country proxy failed. Using default IP.{Color.RESET}")
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
            'user_id': self.user_id
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
{Color.CYAN}║{Color.RESET}      {Color.DIM}Proxy Rotation + Auto Name Gen{Color.RESET}          {Color.CYAN}║{Color.RESET}
{Color.CYAN}╠════════════════════════════════════════════════════════════╣{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}FACEBOOK{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}AUTO CREATE{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}PROXY ROTATION{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}AUTO NAME{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}OTP RETRY{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}CLIPROXY{Color.RESET}    {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}VOICE FEEDBACK{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}AUTO COUNTRY{Color.RESET}  {Color.CYAN}║{Color.RESET}
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
                print(f"{Color.CYAN}[*] Browser using proxy: {proxy}{Color.RESET}")
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

# ==================== LICENSE MANAGER ====================
class LicenseManager:
    def __init__(self):
        self.config = load_json(CONFIG_FILE)
    
    def save(self): save_json(CONFIG_FILE, self.config)
    def get_license_key(self): return self.config.get('license_key', '')
    def set_license_key(self, key): self.config['license_key'] = key; self.save()
    def get_device_serial(self): return self.config.get('device_serial', '')
    def set_device_serial(self, s): self.config['device_serial'] = s; self.save()
    def get_browser_ready(self): return self.config.get('browser_ready', False)
    def set_browser_ready(self, status): self.config['browser_ready'] = status; self.save()
    def get_proxy_api_key(self): return self.config.get('proxy_api_key', '')
    def set_proxy_api_key(self, key): self.config['proxy_api_key'] = key; self.save()
    
    def verify(self, key):
        print(f'  {Color.YELLOW}[*] Verifying license via server...{Color.RESET}')
        result = verify_license(key, self.get_device_serial())
        if result.get('valid'):
            print(f'  {Color.GREEN}[+] License Active! Expires: {result.get("expires_at", "N/A")}{Color.RESET}')
            self.set_license_key(key)
            return True, result
        else:
            print(f'  {Color.RED}[-] {result.get("message", "Invalid license")}{Color.RESET}')
            return False, result
    
    def register_device(self, device_serial):
        print(f'  {Color.CYAN}[*] Registering device via server...{Color.RESET}')
        result = register_device(device_serial, self.get_license_key())
        if result.get('success'):
            self.set_device_serial(device_serial)
            print(f'  {Color.GREEN}[+] Device registered successfully{Color.RESET}')
            return True
        else:
            print(f'  {Color.RED}[-] {result.get("message", "Registration failed")}{Color.RESET}')
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
            print(f"{Color.GREEN}[+] Proxy: {proxy}{Color.RESET}")
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
        self.proxy_manager.refresh_proxy_pool()
        self.is_running = True
        for idx, phone in enumerate(numbers, 1):
            if not self.is_running:
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
        self.license = LicenseManager()
        self.audio = AudioEngine()
        self.bot = None
        self.config = load_json(CONFIG_FILE)
        self.data_dir = self.config.get('data_dir', '/storage/emulated/0/Download/Ridol FB Tool')
        self.browser_ready = self.config.get('browser_ready', False)
        self.bot_running = False
        
        api_key = self.config.get('proxy_api_key', '')
        if api_key:
            PROXY_API_KEY = api_key
    
    def show_header(self):
        clear_screen()
        TitleAnimation.compact_banner()
        proxy_stats = self.proxy_manager.get_proxy_stats()
        proxy_status = f"● {proxy_stats['total']} proxies"
        proxy_color = Color.GREEN if proxy_stats['total'] > 0 else Color.RED
        ip_status = "● CONNECTED" if proxy_stats.get('ip_connected') else "● DISCONNECTED"
        ip_color = Color.GREEN if proxy_stats.get('ip_connected') else Color.RED
        
        user_id = proxy_stats.get('user_id', 'None')
        user_display = f"User: {user_id}" if user_id else "User: None"
        
        print(f' {proxy_color}{proxy_status}{Color.RESET} Proxy Pool: {Color.WHITE}{"Ready" if proxy_stats["total"] > 0 else "Empty"}{Color.RESET}')
        print(f' {ip_color}{ip_status}{Color.RESET} IP Connect: {Color.WHITE}{"Connected" if proxy_stats.get("ip_connected") else "Disconnected"} | {user_display}{Color.RESET}')
        browser_status = "● READY" if self.browser_manager.browser_available else "● NOT INSTALLED"
        browser_color = Color.GREEN if self.browser_manager.browser_available else Color.RED
        print(f' {browser_color}{browser_status}{Color.RESET} Browser Pilot: {Color.WHITE}{"Available" if self.browser_manager.browser_available else "Run Setup"}{Color.RESET}')
        lic_key = self.license.get_license_key()
        print(f' {Color.GREEN}●{Color.RESET} License: {Color.WHITE}{"Active" if lic_key else "Not Set"}{Color.RESET}')
        try:
            result = server_request("ping", 'GET')
            connected = result is not None
        except:
            connected = False
        status_color = Color.GREEN if connected else Color.RED
        status_text = "ONLINE" if connected else "OFFLINE"
        print(f' {Color.CYAN}◉{Color.RESET} Server: {status_color}{status_text}{Color.RESET}\n')
    
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
    
    def get_current_provider(self):
        config = load_json(CONFIG_FILE)
        provider = config.get('proxy_provider', 'None')
        return provider if provider else 'None'
    
    def connect_cliproxy_all(self):
        """Connect Cliproxy with All region - User provides URL"""
        print(f'\n  {Color.CYAN}--- Cliproxy Connection (All Region) ---{Color.RESET}')
        print(f'  {Color.DIM}Enter your Cliproxy URL with "All" as region{Color.RESET}')
        print(f'  {Color.DIM}Example: socks5://ridolislam-region-All:Ridol123@sg.cliproxy.io:3010{Color.RESET}')
        
        proxy_url = input(f'\n  {Color.CYAN}Enter SOCKS5 URL: {Color.RESET}').strip()
        
        if not proxy_url:
            print(f'  {Color.RED}[-] URL cannot be empty!{Color.RESET}')
            press_enter()
            return
        
        if not proxy_url.startswith('socks5://'):
            print(f'  {Color.YELLOW}[!] URL should start with socks5://{Color.RESET}')
            proxy_url = f"socks5://{proxy_url}"
        
        # Check if URL contains "All" as region
        if 'region-All' not in proxy_url:
            print(f'  {Color.YELLOW}[!] URL should contain "region-All" for auto country switching{Color.RESET}')
            print(f'  {Color.DIM}Example: socks5://ridolislam-region-All:Ridol123@sg.cliproxy.io:3010{Color.RESET}')
            confirm = input(f'  {Color.CYAN}Continue anyway? (y/n): {Color.RESET}').strip().lower()
            if confirm != 'y':
                press_enter()
                return
        
        print(f'\n  {Color.CYAN}[*] Connecting to: {proxy_url}{Color.RESET}')
        
        # Test and connect
        success = self.proxy_manager.connect_ip(proxy_url)
        
        if success:
            print(f'  {Color.GREEN}[+] Cliproxy Connected Successfully!{Color.RESET}')
            print(f'  {Color.CYAN}[+] Auto country switching enabled!{Color.RESET}')
            print(f'  {Color.CYAN}[+] User ID: {self.proxy_manager.user_id}{Color.RESET}')
            self.audio.speak_ip_connected()
            
            config = load_json(CONFIG_FILE)
            config['proxy_provider'] = 'Cliproxy (All Region)'
            config['proxy_url'] = proxy_url
            config['proxy_user_id'] = self.proxy_manager.user_id
            save_json(CONFIG_FILE, config)
            
            self.proxy_manager.connected_ip_url = proxy_url
            self.proxy_manager.ip_connected = True
        else:
            print(f'  {Color.RED}[-] Failed to connect. Please check your URL.{Color.RESET}')
        
        press_enter()
    
    def view_connected_ip(self):
        proxy_stats = self.proxy_manager.get_proxy_stats()
        config = load_json(CONFIG_FILE)
        print(f'\n  {Color.CYAN}--- Connected IP Status ---{Color.RESET}')
        if proxy_stats.get('ip_connected'):
            print(f'  {Color.GREEN}[+] IP Connected: Yes{Color.RESET}')
            print(f'  {Color.CYAN}Provider: {config.get("proxy_provider", "Unknown")}{Color.RESET}')
            print(f'  {Color.CYAN}User ID: {proxy_stats.get("user_id", "Unknown")}{Color.RESET}')
            print(f'  {Color.CYAN}Connected IP: {proxy_stats.get("connected_ip", "None")}{Color.RESET}')
            print(f'  {Color.CYAN}Auto Country: Enabled (will switch based on phone number){Color.RESET}')
            try:
                proxy_url = proxy_stats.get('connected_ip')
                if proxy_url:
                    proxies = {'http': proxy_url, 'https': proxy_url}
                    response = requests.get('http://ip-api.com/json', proxies=proxies, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        print(f'  {Color.CYAN}IP Address: {data.get("query", "Unknown")}{Color.RESET}')
                        print(f'  {Color.CYAN}Country: {data.get("country", "Unknown")} ({data.get("countryCode", "XX")}){Color.RESET}')
                        print(f'  {Color.CYAN}Region: {data.get("regionName", "Unknown")}{Color.RESET}')
                        print(f'  {Color.CYAN}City: {data.get("city", "Unknown")}{Color.RESET}')
                        print(f'  {Color.CYAN}ISP: {data.get("isp", "Unknown")}{Color.RESET}')
            except Exception as e:
                print(f'  {Color.YELLOW}[!] Could not fetch IP details: {e}{Color.RESET}')
        else:
            print(f'  {Color.RED}[-] No IP Connected{Color.RESET}')
            print(f'  {Color.YELLOW}[!] Please connect a proxy first{Color.RESET}')
        press_enter()
    
    def disconnect_ip(self):
        print(f'\n  {Color.CYAN}[*] Disconnecting IP...{Color.RESET}')
        if self.proxy_manager.disconnect_ip():
            print(f'  {Color.GREEN}[+] IP Disconnected Successfully!{Color.RESET}')
            self.audio.speak_ip_disconnected()
            config = load_json(CONFIG_FILE)
            config['proxy_provider'] = 'None'
            config['proxy_url'] = ''
            config['proxy_user_id'] = ''
            save_json(CONFIG_FILE, config)
        else:
            print(f'  {Color.YELLOW}[!] No IP to disconnect{Color.RESET}')
        press_enter()
    
    def test_current_ip(self):
        proxy_stats = self.proxy_manager.get_proxy_stats()
        print(f'\n  {Color.CYAN}--- Testing Current IP ---{Color.RESET}')
        if not proxy_stats.get('ip_connected'):
            print(f'  {Color.RED}[-] No IP Connected!{Color.RESET}')
            print(f'  {Color.YELLOW}[!] Please connect a proxy first{Color.RESET}')
            press_enter()
            return
        proxy_url = proxy_stats.get('connected_ip')
        print(f'  {Color.CYAN}[*] Testing: {proxy_url}{Color.RESET}')
        try:
            proxies = {'http': proxy_url, 'https': proxy_url}
            start_time = time.time()
            response = requests.get('http://ip-api.com/json', proxies=proxies, timeout=15)
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                data = response.json()
                print(f'  {Color.GREEN}[+] IP is Working!{Color.RESET}')
                print(f'  {Color.CYAN}Response Time: {response_time:.0f}ms{Color.RESET}')
                print(f'  {Color.CYAN}IP Address: {data.get("query", "Unknown")}{Color.RESET}')
                print(f'  {Color.CYAN}Country: {data.get("country", "Unknown")} ({data.get("countryCode", "XX")}){Color.RESET}')
                print(f'  {Color.CYAN}Region: {data.get("regionName", "Unknown")}{Color.RESET}')
                print(f'  {Color.CYAN}City: {data.get("city", "Unknown")}{Color.RESET}')
                print(f'  {Color.CYAN}ISP: {data.get("isp", "Unknown")}{Color.RESET}')
                self.audio.speak('IP test successful')
            else:
                print(f'  {Color.RED}[-] IP test failed. Status: {response.status_code}{Color.RESET}')
        except requests.exceptions.Timeout:
            print(f'  {Color.RED}[-] Connection timeout! IP may be slow or down.{Color.RESET}')
        except Exception as e:
            print(f'  {Color.RED}[-] Test error: {e}{Color.RESET}')
        press_enter()
    
    def ip_management_menu(self):
        """IP Management Menu - Connect Cliproxy All Region"""
        while True:
            self.show_header()
            proxy_stats = self.proxy_manager.get_proxy_stats()
            ip_status = "Connected" if proxy_stats.get('ip_connected') else "Disconnected"
            ip_color = Color.GREEN if proxy_stats.get('ip_connected') else Color.RED
            user_id = proxy_stats.get('user_id', 'None')
            
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}IP MANAGEMENT - CLIPROXY ALL REGION{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Status: {ip_color}{ip_status}{Color.RESET}{Color.CYAN}                                     ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  User ID: {Color.WHITE}{user_id}{Color.RESET}{Color.CYAN}                                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Auto Country: {Color.WHITE}Enabled (based on phone number){Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Connect Cliproxy (All Region)        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} View Connected IP                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Disconnect IP                      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Test Current IP                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back to Main Menu                 {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                self.connect_cliproxy_all()
            elif choice == '2':
                self.view_connected_ip()
            elif choice == '3':
                self.disconnect_ip()
            elif choice == '4':
                self.test_current_ip()
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
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}MAIN MENU - PROXY + AUTO NAME{Color.RESET}{Color.CYAN}                 ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Browser Pilot Setup             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} IP Management                   {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} License Management              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} Data Folder                     {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[5]{Color.RESET} Start Bot                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[6]{Color.RESET} Status                           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[7]{Color.RESET} Audio Settings                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[8]{Color.RESET} Demo                             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[9]{Color.RESET} Help                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                self.menu_browser()
            elif choice == '2':
                self.ip_management_menu()
            elif choice == '3':
                self.menu_license()
            elif choice == '4':
                self.menu_folder()
            elif choice == '5':
                self.menu_start_bot()
            elif choice == '6':
                self.menu_status()
            elif choice == '7':
                self.menu_audio()
            elif choice == '8':
                self.menu_demo()
            elif choice == '9':
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
        proxy_stats = self.proxy_manager.get_proxy_stats()
        
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}START BOT{Color.RESET}{Color.CYAN}                                        ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Numbers: {len(load_file_lines(os.path.join(self.data_dir, "numbers.txt")))}                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.DIM}{self.license.get_license_key() or "Not set"}{Color.RESET}{Color.CYAN}             ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Browser: {Color.DIM}{"● Ready" if self.browser_manager.browser_available else "○ Not installed"}{Color.RESET}{Color.CYAN}    ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  IP Connected: {Color.DIM}{"Yes" if proxy_stats.get("ip_connected") else "No"}{Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  User ID: {Color.DIM}{proxy_stats.get("user_id", "None")}{Color.RESET}{Color.CYAN}                     ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Auto Country: {Color.DIM}Enabled (based on phone number){Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Folder Status: {Color.DIM}{"✓ Exists" if folder_exists else "✗ Not found"}{Color.RESET}{Color.CYAN}        ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        
        if not folder_exists:
            print(f'\n{Color.RED}[-] Data folder not found!{Color.RESET}')
            self.audio.speak_folder_not_found()
            press_enter()
            return
        if not self.license.get_license_key():
            print(f'\n{Color.RED}[-] No license key set!{Color.RESET}')
            press_enter()
            return
        if not self.browser_manager.browser_available:
            print(f'\n{Color.RED}[-] Browser Pilot not installed!{Color.RESET}')
            press_enter()
            return
        if not proxy_stats.get('ip_connected'):
            print(f'\n{Color.YELLOW}[!] No IP connected! Please connect Cliproxy first.{Color.RESET}')
            print(f'  {Color.DIM}Go to IP Management -> Connect Cliproxy (All Region){Color.RESET}')
            press_enter()
            return
        
        workers = input(f'\n {Color.CYAN}Number of workers [1-5, default 1]: {Color.RESET}').strip()
        try:
            workers = int(workers) if workers else 1
            workers = max(1, min(5, workers))
        except:
            workers = 1
        print(f'\n{Color.YELLOW}[!] Press 0 and Enter to stop the bot{Color.RESET}')
        self.bot_running = True
        stop_thread = threading.Thread(target=self.check_stop_input, daemon=True)
        stop_thread.start()
        self.bot = FacebookBot(self.data_dir, self.license.get_license_key(), self.audio)
        self.audio.speak_bot_starting()
        self.bot.run_bot(workers)
        self.bot_running = False
        time.sleep(1)
        print(f'\n{Color.GREEN}[+] Returned to main menu{Color.RESET}')
        press_enter()
    
    def menu_status(self):
        self.show_header()
        proxy_stats = self.proxy_manager.get_proxy_stats()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}SYSTEM STATUS{Color.RESET}{Color.CYAN}                                 ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Browser Pilot: {Color.WHITE}{"Available" if self.browser_manager.browser_available else "Not installed"}{Color.RESET}{Color.CYAN} ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Proxy Pool: {Color.WHITE}{proxy_stats["total"]} proxies{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} IP Connected: {Color.WHITE}{'Yes' if proxy_stats.get('ip_connected') else 'No'}{Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} User ID: {Color.WHITE}{proxy_stats.get('user_id', 'None')}{Color.RESET}{Color.CYAN}                  ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Auto Country: {Color.WHITE}Enabled{Color.RESET}{Color.CYAN}                        ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} License: {Color.WHITE}{"Active" if self.license.get_license_key() else "None"}{Color.RESET}{Color.CYAN}                  ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Data Dir: {Color.WHITE}{self.data_dir}{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {self.audio.get_status()}{Color.CYAN}         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Automation: {Color.WHITE}{"Running" if self.bot and self.bot.running else "Idle"}{Color.RESET}{Color.CYAN}          ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        try:
            result = server_request("status", 'GET')
            if result:
                print(f'\n{Color.CYAN}Server Status:{Color.RESET}')
                print(f'  Database: {result.get("database", "N/A")}')
                print(f'  Licenses: {result.get("license_count", 0)}')
                print(f'  Devices: {result.get("device_count", 0)}')
            else:
                print(f'\n{Color.RED}Server: OFFLINE{Color.RESET}')
        except:
            print(f'\n{Color.RED}Server: OFFLINE{Color.RESET}')
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
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}HELP - CLIPROXY ALL REGION{Color.RESET}{Color.CYAN}                        ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [?] {Color.WHITE}How to Setup{Color.RESET}{Color.CYAN}                                    ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  1. Go to IP Management (Option 2)                   {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  2. Select "Connect Cliproxy (All Region)"           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  3. Enter your URL:                                   {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}     socks5://ridolislam-region-All:Ridol123@...     {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  4. Bot will auto-detect country from phone number   {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  5. Start the bot (Option 5)                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [#] {Color.WHITE}Features{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - One URL for all countries                         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Auto country switching based on phone number     {Color.CYAN}║{Color.RESET}
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
