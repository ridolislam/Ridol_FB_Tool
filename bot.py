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
APP_VERSION = 'v6.5'

# ==================== PROXY CONFIG ====================
PROXY_SOURCES = {
    '9proxy': 'https://api.9proxy.com/get?api_key={api_key}&format=json',
    'webshare': 'https://api.webshare.io/v2/proxy/list/',
    'proxy_scrape': 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all',
    'cliproxy': 'socks5://{username}:{password}@{host}:{port}'
}

# Cliproxy Configuration
CLIPROXY_CONFIG = {
    'host': 'sg.cliproxy.io',
    'port': 3010,
    'base_username': 'ridolislam-region',
    'password': 'Ridol123',
    'enabled': True
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

# ==================== COUNTRY CODES ====================
# Complete country codes for all countries
COUNTRY_CODES = {
    # Asia
    '93': 'AF',  # Afghanistan
    '374': 'AM', # Armenia
    '994': 'AZ', # Azerbaijan
    '880': 'BD', # Bangladesh
    '975': 'BT', # Bhutan
    '673': 'BN', # Brunei
    '855': 'KH', # Cambodia
    '86': 'CN',  # China
    '852': 'HK', # Hong Kong
    '91': 'IN',  # India
    '62': 'ID',  # Indonesia
    '98': 'IR',  # Iran
    '964': 'IQ', # Iraq
    '972': 'IL', # Israel
    '81': 'JP',  # Japan
    '962': 'JO', # Jordan
    '7': 'KZ',   # Kazakhstan
    '965': 'KW', # Kuwait
    '996': 'KG', # Kyrgyzstan
    '856': 'LA', # Laos
    '961': 'LB', # Lebanon
    '60': 'MY',  # Malaysia
    '960': 'MV', # Maldives
    '976': 'MN', # Mongolia
    '95': 'MM',  # Myanmar
    '977': 'NP', # Nepal
    '850': 'KP', # North Korea
    '968': 'OM', # Oman
    '92': 'PK',  # Pakistan
    '970': 'PS', # Palestine
    '63': 'PH',  # Philippines
    '974': 'QA', # Qatar
    '966': 'SA', # Saudi Arabia
    '65': 'SG',  # Singapore
    '82': 'KR',  # South Korea
    '94': 'LK',  # Sri Lanka
    '963': 'SY', # Syria
    '886': 'TW', # Taiwan
    '992': 'TJ', # Tajikistan
    '66': 'TH',  # Thailand
    '90': 'TR',  # Turkey
    '993': 'TM', # Turkmenistan
    '971': 'AE', # UAE
    '998': 'UZ', # Uzbekistan
    '84': 'VN',  # Vietnam
    '967': 'YE', # Yemen

    # Europe
    '355': 'AL', # Albania
    '376': 'AD', # Andorra
    '43': 'AT',  # Austria
    '375': 'BY', # Belarus
    '32': 'BE',  # Belgium
    '387': 'BA', # Bosnia and Herzegovina
    '359': 'BG', # Bulgaria
    '385': 'HR', # Croatia
    '357': 'CY', # Cyprus
    '420': 'CZ', # Czech Republic
    '45': 'DK',  # Denmark
    '372': 'EE', # Estonia
    '358': 'FI', # Finland
    '33': 'FR',  # France
    '995': 'GE', # Georgia
    '49': 'DE',  # Germany
    '30': 'GR',  # Greece
    '36': 'HU',  # Hungary
    '354': 'IS', # Iceland
    '353': 'IE', # Ireland
    '39': 'IT',  # Italy
    '371': 'LV', # Latvia
    '423': 'LI', # Liechtenstein
    '370': 'LT', # Lithuania
    '352': 'LU', # Luxembourg
    '389': 'MK', # North Macedonia
    '356': 'MT', # Malta
    '373': 'MD', # Moldova
    '377': 'MC', # Monaco
    '382': 'ME', # Montenegro
    '31': 'NL',  # Netherlands
    '47': 'NO',  # Norway
    '48': 'PL',  # Poland
    '351': 'PT', # Portugal
    '40': 'RO',  # Romania
    '7': 'RU',   # Russia
    '381': 'RS', # Serbia
    '421': 'SK', # Slovakia
    '386': 'SI', # Slovenia
    '34': 'ES',  # Spain
    '46': 'SE',  # Sweden
    '41': 'CH',  # Switzerland
    '380': 'UA', # Ukraine
    '44': 'GB',  # UK
    '379': 'VA', # Vatican City

    # North America
    '1': 'US',   # USA/Canada
    '52': 'MX',  # Mexico
    '501': 'BZ', # Belize
    '506': 'CR', # Costa Rica
    '53': 'CU',  # Cuba
    '1': 'DM',   # Dominica
    '1': 'DO',   # Dominican Republic
    '503': 'SV', # El Salvador
    '502': 'GT', # Guatemala
    '504': 'HN', # Honduras
    '1': 'JM',   # Jamaica
    '505': 'NI', # Nicaragua
    '507': 'PA', # Panama
    '1': 'TT',   # Trinidad and Tobago
    '1': 'BS',   # Bahamas
    '1': 'BB',   # Barbados
    '1': 'GD',   # Grenada
    '1': 'LC',   # Saint Lucia
    '1': 'VC',   # Saint Vincent

    # South America
    '54': 'AR',  # Argentina
    '591': 'BO', # Bolivia
    '55': 'BR',  # Brazil
    '56': 'CL',  # Chile
    '57': 'CO',  # Colombia
    '593': 'EC', # Ecuador
    '592': 'GY', # Guyana
    '595': 'PY', # Paraguay
    '51': 'PE',  # Peru
    '597': 'SR', # Suriname
    '598': 'UY', # Uruguay
    '58': 'VE',  # Venezuela

    # Africa
    '213': 'DZ', # Algeria
    '244': 'AO', # Angola
    '229': 'BJ', # Benin
    '267': 'BW', # Botswana
    '226': 'BF', # Burkina Faso
    '257': 'BI', # Burundi
    '237': 'CM', # Cameroon
    '238': 'CV', # Cape Verde
    '236': 'CF', # Central African Republic
    '235': 'TD', # Chad
    '269': 'KM', # Comoros
    '243': 'CD', # Congo (Kinshasa)
    '242': 'CG', # Congo (Brazzaville)
    '253': 'DJ', # Djibouti
    '20': 'EG',  # Egypt
    '240': 'GQ', # Equatorial Guinea
    '291': 'ER', # Eritrea
    '251': 'ET', # Ethiopia
    '241': 'GA', # Gabon
    '220': 'GM', # Gambia
    '233': 'GH', # Ghana
    '224': 'GN', # Guinea
    '245': 'GW', # Guinea-Bissau
    '254': 'KE', # Kenya
    '266': 'LS', # Lesotho
    '231': 'LR', # Liberia
    '218': 'LY', # Libya
    '261': 'MG', # Madagascar
    '265': 'MW', # Malawi
    '223': 'ML', # Mali
    '222': 'MR', # Mauritania
    '230': 'MU', # Mauritius
    '212': 'MA', # Morocco
    '258': 'MZ', # Mozambique
    '264': 'NA', # Namibia
    '227': 'NE', # Niger
    '234': 'NG', # Nigeria
    '250': 'RW', # Rwanda
    '239': 'ST', # Sao Tome and Principe
    '221': 'SN', # Senegal
    '248': 'SC', # Seychelles
    '232': 'SL', # Sierra Leone
    '252': 'SO', # Somalia
    '27': 'ZA',  # South Africa
    '211': 'SS', # South Sudan
    '249': 'SD', # Sudan
    '268': 'SZ', # Swaziland
    '255': 'TZ', # Tanzania
    '228': 'TG', # Togo
    '216': 'TN', # Tunisia
    '256': 'UG', # Uganda
    '260': 'ZM', # Zambia
    '263': 'ZW', # Zimbabwe

    # Oceania
    '61': 'AU',  # Australia
    '679': 'FJ', # Fiji
    '686': 'KI', # Kiribati
    '692': 'MH', # Marshall Islands
    '691': 'FM', # Micronesia
    '674': 'NR', # Nauru
    '64': 'NZ',  # New Zealand
    '675': 'PG', # Papua New Guinea
    '685': 'WS', # Samoa
    '677': 'SB', # Solomon Islands
    '676': 'TO', # Tonga
    '688': 'TV', # Tuvalu
    '678': 'VU', # Vanuatu

    # Default
    'XX': 'XX',  # Unknown
}

# Country to region mapping for Cliproxy
COUNTRY_TO_REGION = {
    'US': 'US', 'CA': 'US',  # North America
    'GB': 'GB', 'DE': 'DE', 'FR': 'FR', 'IT': 'IT', 'ES': 'ES', 'NL': 'NL', # Europe
    'AU': 'AU', 'NZ': 'AU',  # Oceania
    'SG': 'SG', 'MY': 'MY', 'ID': 'ID', 'PH': 'PH', 'TH': 'TH', 'VN': 'VN', # Southeast Asia
    'BD': 'BD', 'IN': 'IN', 'PK': 'PK', 'LK': 'LK', 'NP': 'NP', # South Asia
    'CN': 'CN', 'JP': 'JP', 'KR': 'KR', # East Asia
    'AE': 'AE', 'SA': 'SA', 'KW': 'KW', 'QA': 'QA', # Middle East
    'BR': 'BR', 'AR': 'AR', 'CL': 'CL', # South America
    'ZA': 'ZA', 'NG': 'NG', 'EG': 'EG', # Africa
    'RU': 'RU', # Russia
    'TR': 'TR', # Turkey
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
    
    # দেশ অনুযায়ী নামের ডেটাবেস
    NAMES_DATABASE = {
        'ID': {  # Indonesia
            'first': ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fitri', 'Gilang', 'Hana', 'Indra', 'Joko',
                      'Kartika', 'Lestari', 'Maya', 'Nanda', 'Oka', 'Purnama', 'Ratna', 'Sari', 'Tono', 'Utami',
                      'Wahyu', 'Yuni', 'Zahra', 'Agung', 'Bayu', 'Cahya', 'Dian', 'Eka', 'Fajar', 'Gita',
                      'Hendra', 'Intan', 'Jaya', 'Kusuma', 'Lina', 'Mega', 'Nova', 'Oktaviani', 'Putri', 'Rina'],
            'last': ['Siregar', 'Nasution', 'Harahap', 'Lubis', 'Batubara', 'Sinaga', 'Saragih', 'Ginting',
                     'Manurung', 'Simanjuntak', 'Situmorang', 'Sihombing', 'Hutagalung', 'Simatupang', 'Tambunan',
                     'Tampubolon', 'Silalahi', 'Panggabean', 'Simarmata', 'Sibarani', 'Hutapea', 'Sianturi',
                     'Hasibuan', 'Rambe', 'Daulay', 'Rangkuti', 'Nasution']
        },
        'US': {  # USA
            'first': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles',
                      'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth', 'Susan', 'Jessica', 'Sarah', 'Karen',
                      'Daniel', 'Matthew', 'Christopher', 'Andrew', 'Joshua', 'Ashley', 'Amanda', 'Melissa', 'Stephanie', 'Nicole'],
            'last': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                     'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee']
        },
        'GB': {  # UK
            'first': ['Oliver', 'George', 'Harry', 'Jack', 'Jacob', 'Charlie', 'Thomas', 'James', 'William', 'Muhammad',
                      'Amelia', 'Olivia', 'Isla', 'Emily', 'Poppy', 'Ava', 'Isabella', 'Jessica', 'Lily', 'Sophie'],
            'last': ['Smith', 'Jones', 'Williams', 'Taylor', 'Brown', 'Davies', 'Evans', 'Thomas', 'Johnson', 'Roberts',
                     'Walker', 'Wright', 'Robinson', 'Thompson', 'White', 'Hughes', 'Edwards', 'Green', 'Lewis', 'Wood']
        },
        'IN': {  # India
            'first': ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Pranav', 'Dhruv', 'Aryan', 'Reyansh',
                      'Aanya', 'Ananya', 'Diya', 'Aadhya', 'Myra', 'Sara', 'Ishaan', 'Anika', 'Aarohi', 'Advik'],
            'last': ['Sharma', 'Verma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Gandhi', 'Prasad', 'Sinha',
                     'Pandey', 'Tiwari', 'Chaudhary', 'Srivastava', 'Roy', 'Nair', 'Reddy', 'Rao', 'Mishra', 'Trivedi']
        },
        'BD': {  # Bangladesh
            'first': ['Mohammad', 'Abdullah', 'Rafiq', 'Shahid', 'Kamal', 'Jamal', 'Rahim', 'Karim', 'Hasan', 'Ali',
                      'Fatima', 'Ayesha', 'Nadia', 'Taslima', 'Rokeya', 'Shirin', 'Nasrin', 'Jahan', 'Morshed', 'Rashed'],
            'last': ['Rahman', 'Ahmed', 'Islam', 'Hossain', 'Ali', 'Khan', 'Haque', 'Sarkar', 'Mia', 'Pramanik',
                     'Chowdhury', 'Begum', 'Shah', 'Siddiqui', 'Zaman', 'Mollah', 'Hasan', 'Uddin', 'Faruque', 'Rashid']
        },
        'PK': {  # Pakistan
            'first': ['Muhammad', 'Ali', 'Ahmed', 'Hassan', 'Usman', 'Omar', 'Zain', 'Hamza', 'Bilal', 'Raza',
                      'Ayesha', 'Fatima', 'Zara', 'Hira', 'Noor', 'Sana', 'Kiran', 'Mehak', 'Saima', 'Rabia'],
            'last': ['Khan', 'Malik', 'Akhtar', 'Shah', 'Chaudhry', 'Butt', 'Qureshi', 'Sheikh', 'Abbasi', 'Javed',
                     'Rana', 'Iqbal', 'Rehman', 'Gul', 'Haq', 'Nazir', 'Saeed', 'Yousaf', 'Afzal', 'Aslam']
        },
        'PH': {  # Philippines
            'first': ['Jose', 'Juan', 'Carlos', 'Ramon', 'Pedro', 'Andres', 'Emilio', 'Josefino', 'Ronaldo', 'Ferdinand',
                      'Maria', 'Josefa', 'Teresita', 'Rosa', 'Luz', 'Cristina', 'Angelica', 'Marisol', 'Lorna', 'Fe'],
            'last': ['Santos', 'Reyes', 'Cruz', 'Garcia', 'Martinez', 'Lopez', 'Gonzales', 'Flores', 'Perez', 'Ramos',
                     'Aguilar', 'Torres', 'Rivera', 'Diaz', 'Romero', 'Sanchez', 'Castro', 'Ortiz', 'Morales', 'Valdez']
        },
        'MY': {  # Malaysia
            'first': ['Ahmad', 'Mohd', 'Abdullah', 'Ali', 'Hassan', 'Zainal', 'Kamarul', 'Azman', 'Razali', 'Idris',
                      'Siti', 'Nur', 'Aishah', 'Fatimah', 'Zaharah', 'Rohani', 'Nor', 'Azizah', 'Hamidah', 'Salbiah'],
            'last': ['Abdullah', 'Ali', 'Hassan', 'Ahmad', 'Mohd', 'Ismail', 'Othman', 'Rahman', 'Hussein', 'Yusof',
                     'Wan', 'Zainal', 'Abdul', 'Razak', 'Ibrahim', 'Sulaiman', 'Mat', 'Hassan', 'Din', 'Shariff']
        },
        'SG': {  # Singapore
            'first': ['Wei', 'Ming', 'Li', 'Xin', 'Yi', 'Jun', 'Hui', 'Ling', 'Yan', 'Hao',
                      'Mei', 'Jing', 'Qiang', 'Yong', 'Chun', 'Kim', 'Seng', 'Wah', 'Choon', 'Yew'],
            'last': ['Tan', 'Lim', 'Lee', 'Ng', 'Wong', 'Ong', 'Goh', 'Chua', 'Koh', 'Chew',
                     'Yeo', 'Chong', 'Teo', 'Yap', 'Soh', 'Tay', 'Chan', 'See', 'Ang', 'Poh']
        },
        'TH': {  # Thailand
            'first': ['Somchai', 'Somsak', 'Prasert', 'Kriangkrai', 'Pongsak', 'Nattaporn', 'Wichian', 'Somkiat', 'Suthep', 'Anuchit',
                      'Nongnuch', 'Somjai', 'Siriporn', 'Saowanee', 'Jintana', 'Wannapa', 'Supaporn', 'Kannika', 'Ratchanee', 'Pornpimon'],
            'last': ['Somchai', 'Somsak', 'Prasert', 'Kriangkrai', 'Pongsak', 'Nattaporn', 'Wichian', 'Somkiat', 'Suthep', 'Anuchit',
                     'Nongnuch', 'Somjai', 'Siriporn', 'Saowanee', 'Jintana', 'Wannapa', 'Supaporn', 'Kannika', 'Ratchanee', 'Pornpimon']
        },
        'VN': {  # Vietnam
            'first': ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Bui', 'Do', 'Huynh',
                      'Thi', 'Van', 'Quang', 'Minh', 'Tuan', 'Phuong', 'Anh', 'Hoa', 'Lan', 'Hai'],
            'last': ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Bui', 'Do', 'Huynh',
                     'Truong', 'Ly', 'Dinh', 'Chau', 'Ta', 'Mai', 'Duong', 'Lam', 'Phan', 'Vuong']
        },
        'AE': {  # UAE
            'first': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Omar', 'Khalid', 'Saeed', 'Abdulla', 'Rashid', 'Hamad',
                      'Fatima', 'Aisha', 'Mariam', 'Noora', 'Hessa', 'Mouza', 'Shaikha', 'Amna', 'Latifa', 'Maitha'],
            'last': ['Al Maktoum', 'Al Nahyan', 'Al Suwaidi', 'Al Tayer', 'Al Ghurair', 'Al Habtoor', 'Al Futtaim',
                     'Al Shamsi', 'Al Mazrouei', 'Al Dhaheri']
        },
        'SA': {  # Saudi Arabia
            'first': ['Mohammed', 'Ahmed', 'Ali', 'Abdullah', 'Omar', 'Saud', 'Khalid', 'Sultan', 'Faisal', 'Nayef',
                      'Fatima', 'Noura', 'Haya', 'Mona', 'Layan', 'Sara', 'Reem', 'Dana', 'Maha', 'Lama'],
            'last': ['Al Saud', 'Al Thani', 'Al Otaibi', 'Al Harbi', 'Al Anzi', 'Al Shamrani', 'Al Mutairi',
                     'Al Enazi', 'Al Maliki', 'Al Dossary']
        },
        'TR': {  # Turkey
            'first': ['Mehmet', 'Ahmet', 'Ali', 'Mustafa', 'Hasan', 'Huseyin', 'Osman', 'Yusuf', 'Ibrahim', 'Ismail',
                      'Fatma', 'Ayse', 'Emine', 'Hatice', 'Zeynep', 'Elif', 'Meryem', 'Sultan', 'Rabia', 'Gul'],
            'last': ['Yilmaz', 'Kaya', 'Demir', 'Celik', 'Aydin', 'Ozdemir', 'Arslan', 'Dogan', 'Kilic', 'Yildirim']
        },
        'RU': {  # Russia
            'first': ['Alexander', 'Dmitri', 'Ivan', 'Mikhail', 'Nikolai', 'Sergei', 'Vladimir', 'Yuri', 'Andrei', 'Pavel',
                      'Anna', 'Olga', 'Tatiana', 'Natalia', 'Elena', 'Irina', 'Svetlana', 'Marina', 'Ekaterina', 'Daria'],
            'last': ['Ivanov', 'Petrov', 'Sidorov', 'Kuznetsov', 'Smirnov', 'Popov', 'Sokolov', 'Lebedev', 'Kozlov', 'Novikov']
        },
        'BR': {  # Brazil
            'first': ['Joao', 'Jose', 'Maria', 'Antonio', 'Francisco', 'Carlos', 'Paulo', 'Pedro', 'Lucas', 'Gabriel',
                      'Ana', 'Beatriz', 'Carla', 'Daniela', 'Eduarda', 'Fernanda', 'Gabriela', 'Helena', 'Isabela', 'Julia'],
            'last': ['Silva', 'Santos', 'Souza', 'Oliveira', 'Pereira', 'Costa', 'Rodrigues', 'Almeida', 'Nascimento', 'Lima']
        },
        'JP': {  # Japan
            'first': ['Haruto', 'Sota', 'Yuki', 'Riku', 'Hinata', 'Sakura', 'Hana', 'Yui', 'Mio', 'Rin',
                      'Aoi', 'Hina', 'Risa', 'Mai', 'Ayumi', 'Yuka', 'Nana', 'Momo', 'Saki', 'Aya'],
            'last': ['Sato', 'Suzuki', 'Takahashi', 'Tanaka', 'Watanabe', 'Ito', 'Yamamoto', 'Nakamura', 'Kobayashi', 'Kato']
        },
        'CN': {  # China
            'first': ['Wei', 'Ming', 'Li', 'Xin', 'Yi', 'Jun', 'Hui', 'Ling', 'Yan', 'Hao',
                      'Mei', 'Jing', 'Qiang', 'Yong', 'Chun', 'Kim', 'Seng', 'Wah', 'Choon', 'Yew'],
            'last': ['Wang', 'Li', 'Zhang', 'Liu', 'Chen', 'Yang', 'Huang', 'Zhao', 'Wu', 'Zhou']
        },
        'DE': {  # Germany
            'first': ['Hans', 'Peter', 'Klaus', 'Wolfgang', 'Thomas', 'Andreas', 'Michael', 'Stefan', 'Markus', 'Daniel',
                      'Anna', 'Maria', 'Sabine', 'Andrea', 'Ursula', 'Monika', 'Petra', 'Birgit', 'Claudia', 'Susanne'],
            'last': ['Muller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker', 'Schulz', 'Hoffmann']
        },
        'FR': {  # France
            'first': ['Jean', 'Pierre', 'Michel', 'Philippe', 'Alain', 'Bernard', 'Eric', 'Nicolas', 'David', 'Christophe',
                      'Marie', 'Nathalie', 'Isabelle', 'Catherine', 'Sophie', 'Anne', 'Laure', 'Caroline', 'Julie', 'Camille'],
            'last': ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau']
        },
        'IT': {  # Italy
            'first': ['Marco', 'Giuseppe', 'Antonio', 'Giovanni', 'Francesco', 'Andrea', 'Luca', 'Mario', 'Paolo', 'Roberto',
                      'Maria', 'Anna', 'Giulia', 'Laura', 'Martina', 'Sara', 'Chiara', 'Elena', 'Valentina', 'Francesca'],
            'last': ['Rossi', 'Russo', 'Ferrari', 'Esposito', 'Bianchi', 'Romano', 'Colombo', 'Ricci', 'Marino', 'Greco']
        },
        'ES': {  # Spain
            'first': ['Antonio', 'Jose', 'Manuel', 'Francisco', 'Juan', 'David', 'Javier', 'Carlos', 'Daniel', 'Luis',
                      'Maria', 'Carmen', 'Ana', 'Isabel', 'Dolores', 'Pilar', 'Josefa', 'Teresa', 'Rosa', 'Antonia'],
            'last': ['Garcia', 'Rodriguez', 'Gonzalez', 'Fernandez', 'Lopez', 'Martinez', 'Sanchez', 'Perez', 'Gomez', 'Martin']
        },
        'NL': {  # Netherlands
            'first': ['Jan', 'Peter', 'Hans', 'Kees', 'Pieter', 'Johan', 'Willem', 'Hendrik', 'Dirk', 'Gerard',
                      'Anna', 'Maria', 'Johanna', 'Elisabeth', 'Catharina', 'Cornelia', 'Petronella', 'Helena', 'Wilhelmina', 'Adriana'],
            'last': ['De Jong', 'Jansen', 'De Vries', 'Van den Berg', 'Van Dijk', 'Bakker', 'Janssen', 'Visser', 'Smit', 'Meijer']
        },
        'AU': {  # Australia
            'first': ['Jack', 'Oliver', 'William', 'James', 'Thomas', 'Liam', 'Noah', 'Ethan', 'Lucas', 'Mason',
                      'Olivia', 'Charlotte', 'Mia', 'Ava', 'Amelia', 'Sophie', 'Grace', 'Chloe', 'Lily', 'Emily'],
            'last': ['Smith', 'Jones', 'Williams', 'Brown', 'Wilson', 'Taylor', 'Johnson', 'White', 'Martin', 'Anderson']
        },
        'ZA': {  # South Africa
            'first': ['Nelson', 'Jacob', 'Cyril', 'Thabo', 'Kofi', 'Mandela', 'Desmond', 'Winnie', 'Graça', 'Miriam',
                      'Zanele', 'Lindiwe', 'Nkosazana', 'Phumzile', 'Baleka', 'Mamphela', 'Naledi', 'Pregs', 'Patience', 'Duduzile'],
            'last': ['Mbeki', 'Zuma', 'Ramaphosa', 'Tambo', 'Machel', 'Tutu', 'Sisulu', 'Motlanthe', 'Msimang', 'Madikizela']
        },
        'EG': {  # Egypt
            'first': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Omar', 'Mahmoud', 'Tarek', 'Khaled', 'Amr', 'Youssef',
                      'Fatima', 'Nadia', 'Laila', 'Samira', 'Huda', 'Aisha', 'Mona', 'Sara', 'Nora', 'Dina'],
            'last': ['Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Mahmoud', 'Tarek', 'Khaled', 'Amr', 'Youssef', 'Ibrahim']
        },
        'NG': {  # Nigeria
            'first': ['Oluwaseun', 'Chukwudi', 'Adebayo', 'Olayinka', 'Emeka', 'Chidi', 'Adeola', 'Babatunde', 'Olumide', 'Segun',
                      'Chioma', 'Ngozi', 'Bola', 'Funke', 'Tolu', 'Ronke', 'Shade', 'Moyo', 'Kemi', 'Bisi'],
            'last': ['Adeyemi', 'Ogunlade', 'Bamidele', 'Okonkwo', 'Eze', 'Nwosu', 'Okafor', 'Igwe', 'Umeh', 'Obi']
        },
        'XX': {  # Unknown/Default
            'first': ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Hayden', 'Harper',
                      'Emerson', 'Reese', 'Charlie', 'Blake', 'Sage', 'Rowan', 'Logan', 'Peyton', 'Ari', 'Ellis'],
            'last': ['Chen', 'Singh', 'Garcia', 'Wang', 'Perez', 'Nguyen', 'Patel', 'Smith', 'Jones', 'Williams',
                     'Davis', 'Brown', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'Martin']
        }
    }
    
    @classmethod
    def get_random_name(cls, country_code):
        """Get random first and last name for a country"""
        country_data = cls.NAMES_DATABASE.get(country_code, cls.NAMES_DATABASE['XX'])
        
        first_name = random.choice(country_data['first'])
        last_name = random.choice(country_data['last'])
        
        return first_name, last_name
    
    @classmethod
    def get_full_name(cls, country_code):
        """Get full name for a country"""
        first, last = cls.get_random_name(country_code)
        return f"{first} {last}"
    
    @classmethod
    def get_multiple_names(cls, country_code, count=5):
        """Get multiple random names for a country"""
        names = []
        for _ in range(count):
            first, last = cls.get_random_name(country_code)
            names.append({'first': first, 'last': last, 'full': f"{first} {last}"})
        return names

# ==================== PROXY MANAGER ====================
class ProxyManager:
    """Manage proxy rotation with country detection - uses default IP if no proxies available"""
    
    def __init__(self):
        self.proxy_pool = []
        self.current_proxy = None
        self.current_country = None
        self.proxy_history = []
        self.api_key = PROXY_API_KEY
        self.last_refresh = 0
        self.refresh_interval = 300  # 5 minutes
        self.use_default_ip = True
        self.cliproxy_enabled = CLIPROXY_CONFIG['enabled']
        
    def _get_country_from_phone(self, phone_number):
        """Get country code from phone number"""
        phone = phone_number.strip().replace('+', '').replace(' ', '').replace('-', '')
        
        # Sort by length (longest first) to avoid partial matches
        for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
            if phone.startswith(code):
                return COUNTRY_CODES[code]
        
        return 'XX'  # Unknown
    
    def _get_cliproxy_for_country(self, country_code):
        """Generate Cliproxy SOCKS5 URL for a specific country"""
        if not self.cliproxy_enabled:
            return None
        
        # Get region for this country
        region = COUNTRY_TO_REGION.get(country_code, country_code)
        
        username = f"{CLIPROXY_CONFIG['base_username']}-{region}"
        host = CLIPROXY_CONFIG['host']
        port = CLIPROXY_CONFIG['port']
        password = CLIPROXY_CONFIG['password']
        
        # SOCKS5 proxy URL
        proxy_url = f"socks5://{username}:{password}@{host}:{port}"
        return proxy_url
    
    def _fetch_proxies_from_9proxy(self):
        """Fetch proxies from 9proxy.com"""
        if not self.api_key:
            print(f"{Color.YELLOW}[!] No API key for 9proxy. Set PROXY_API_KEY environment variable.{Color.RESET}")
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
                            proxies.append({'proxy': proxy, 'country': country, 'type': 'http'})
                elif isinstance(data, dict) and 'data' in data:
                    for item in data['data']:
                        if 'ip' in item and 'port' in item:
                            proxy = f"http://{item['ip']}:{item['port']}"
                            country = item.get('country', 'XX')
                            proxies.append({'proxy': proxy, 'country': country, 'type': 'http'})
                return proxies
            return []
        except Exception as e:
            print(f"{Color.RED}[-] 9proxy fetch error: {e}{Color.RESET}")
            return []
    
    def _fetch_proxies_from_webshare(self):
        """Fetch proxies from webshare.io"""
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
                        proxies.append({'proxy': proxy, 'country': country, 'type': 'http'})
                return proxies
            return []
        except Exception as e:
            print(f"{Color.RED}[-] Webshare fetch error: {e}{Color.RESET}")
            return []
    
    def _fetch_proxies_from_scrape(self):
        """Fetch proxies from proxyscrape.com"""
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
                            country = 'XX'
                            proxies.append({'proxy': proxy, 'country': country, 'type': 'http'})
                            time.sleep(0.1)
                return proxies
            return []
        except Exception as e:
            print(f"{Color.RED}[-] Scrape fetch error: {e}{Color.RESET}")
            return []
    
    def refresh_proxy_pool(self):
        """Refresh proxy pool from all sources including Cliproxy"""
        print(f"{Color.CYAN}[*] Refreshing proxy pool...{Color.RESET}")
        
        all_proxies = []
        
        # Try 9proxy
        proxies = self._fetch_proxies_from_9proxy()
        if proxies:
            print(f"{Color.GREEN}[+] Got {len(proxies)} proxies from 9proxy{Color.RESET}")
            all_proxies.extend(proxies)
        
        # Try webshare
        proxies = self._fetch_proxies_from_webshare()
        if proxies:
            print(f"{Color.GREEN}[+] Got {len(proxies)} proxies from webshare{Color.RESET}")
            all_proxies.extend(proxies)
        
        # Try scrape
        proxies = self._fetch_proxies_from_scrape()
        if proxies:
            print(f"{Color.GREEN}[+] Got {len(proxies)} proxies from proxy-scrape{Color.RESET}")
            all_proxies.extend(proxies)
        
        # Add Cliproxy proxies for all supported countries
        if self.cliproxy_enabled:
            print(f"{Color.CYAN}[*] Adding Cliproxy proxies for all countries...{Color.RESET}")
            cliproxy_proxies = []
            for country_code in set(COUNTRY_CODES.values()):
                if country_code != 'XX':
                    proxy_url = self._get_cliproxy_for_country(country_code)
                    if proxy_url:
                        cliproxy_proxies.append({'proxy': proxy_url, 'country': country_code, 'type': 'socks5'})
            if cliproxy_proxies:
                print(f"{Color.GREEN}[+] Got {len(cliproxy_proxies)} Cliproxy proxies{Color.RESET}")
                all_proxies.extend(cliproxy_proxies)
        
        # Remove duplicates
        seen = set()
        unique_proxies = []
        for p in all_proxies:
            key = p['proxy']
            if key not in seen:
                seen.add(key)
                unique_proxies.append(p)
        
        self.proxy_pool = unique_proxies
        self.last_refresh = time.time()
        
        if len(self.proxy_pool) == 0:
            print(f"{Color.YELLOW}[!] No proxies found. Will use default IP for all operations.{Color.RESET}")
        else:
            print(f"{Color.GREEN}[+] Total unique proxies: {len(self.proxy_pool)}{Color.RESET}")
        
        return len(self.proxy_pool)
    
    def get_proxy_for_number(self, phone_number):
        """Get a proxy based on phone number's country code. Returns None for default IP."""
        country_code = self._get_country_from_phone(phone_number)
        print(f"{Color.CYAN}[+] Country detected: {country_code}{Color.RESET}")
        
        # First, try to get Cliproxy for this country
        if self.cliproxy_enabled:
            proxy_url = self._get_cliproxy_for_country(country_code)
            if proxy_url:
                print(f"{Color.GREEN}[+] Using Cliproxy for {country_code}: {proxy_url}{Color.RESET}")
                self.current_proxy = proxy_url
                self.current_country = country_code
                self.proxy_history.append({
                    'phone': phone_number,
                    'proxy': proxy_url,
                    'country': country_code,
                    'type': 'cliproxy'
                })
                return proxy_url, country_code
        
        # If no Cliproxy, try proxy pool
        if not self.proxy_pool:
            self.refresh_proxy_pool()
            if not self.proxy_pool:
                print(f"{Color.YELLOW}[!] No proxies available. Using default IP.{Color.RESET}")
                self.current_proxy = None
                self.current_country = 'XX'
                return None, country_code
        
        # Find proxy matching country in pool
        matching_proxies = [p for p in self.proxy_pool if p.get('country') == country_code]
        
        if matching_proxies:
            selected = random.choice(matching_proxies)
            print(f"{Color.GREEN}[+] Using proxy from {selected['country']} (matching number){Color.RESET}")
            self.current_proxy = selected['proxy']
            self.current_country = selected['country']
            self.proxy_history.append({
                'phone': phone_number,
                'proxy': selected['proxy'],
                'country': selected['country'],
                'type': selected.get('type', 'http')
            })
            return selected['proxy'], country_code
        else:
            # If no match, use default IP
            print(f"{Color.YELLOW}[!] No proxy for {country_code}, using default IP{Color.RESET}")
            self.current_proxy = None
            self.current_country = 'XX'
            return None, country_code
    
    def get_proxy_stats(self):
        """Get proxy statistics"""
        return {
            'total': len(self.proxy_pool),
            'current': self.current_proxy,
            'country': self.current_country,
            'history_count': len(self.proxy_history),
            'last_refresh': self.last_refresh,
            'using_default_ip': self.current_proxy is None,
            'cliproxy_enabled': self.cliproxy_enabled
        }

# ==================== SOUND FUNCTIONS ====================

def download_from_google_drive():
    """Download MP3 from Google Drive"""
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
        
        if 'html' in response.headers.get('content-type', '').lower():
            html_content = response.text
            download_link_match = re.search(r'"(https://drive\.google\.com/uc\?export=download&id=[^"]+)"', html_content)
            if download_link_match:
                download_url = download_link_match.group(1).replace('\\', '')
                response = requests.get(download_url, stream=True, timeout=60)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"{Color.GREEN}[+] Downloaded: background.mp3 from Google Drive ({os.path.getsize(filepath)} bytes){Color.RESET}")
            return filepath
        else:
            print(f"{Color.YELLOW}[!] Downloaded file is empty or invalid{Color.RESET}")
            return None
            
    except Exception as e:
        print(f"{Color.RED}[-] Google Drive download error: {e}{Color.RESET}")
        return None

def download_sound_from_github(filename):
    """Download sound file from GitHub"""
    url = f"{GITHUB_SOUND_URL}/{filename}"
    filepath = os.path.join(SOUND_DIR, filename)
    
    try:
        print(f"{Color.CYAN}[*] Downloading {filename} from GitHub...{Color.RESET}")
        response = requests.get(url, stream=True, timeout=30)
        
        if response.status_code != 200:
            print(f"{Color.YELLOW}[!] {filename} not found on GitHub (404){Color.RESET}")
            return None
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"{Color.GREEN}[+] Downloaded: {filename}{Color.RESET}")
        return filepath
    except Exception as e:
        print(f"{Color.RED}[-] Download error: {e}{Color.RESET}")
        return None

def download_all_sounds():
    """Download all default sound files from GitHub"""
    sounds = [
        'binary_rain.wav',
        'startup.wav',
        'click.wav',
        'success.wav',
        'fail.wav',
        'done.wav'
    ]
    
    print(f"{Color.CYAN}[*] Checking default sounds...{Color.RESET}")
    
    for sound in sounds:
        filepath = os.path.join(SOUND_DIR, sound)
        if not os.path.exists(filepath):
            download_sound_from_github(sound)
        else:
            print(f"{Color.DIM}[*] {sound} already exists{Color.RESET}")

def download_custom_background():
    """Download custom background MP3 from Google Drive"""
    custom_mp3 = os.path.join(CUSTOM_SOUND_DIR, 'background.mp3')
    custom_wav = os.path.join(CUSTOM_SOUND_DIR, 'background.wav')
    
    if os.path.exists(custom_mp3) and os.path.getsize(custom_mp3) > 0:
        print(f"{Color.DIM}[*] Custom background MP3 already exists{Color.RESET}")
        return True
    
    if os.path.exists(custom_wav) and os.path.getsize(custom_wav) > 0:
        print(f"{Color.DIM}[*] Custom background WAV already exists{Color.RESET}")
        return True
    
    print(f"{Color.CYAN}[*] Looking for custom background MP3...{Color.RESET}")
    result = download_from_google_drive()
    if result:
        return True
    
    try:
        print(f"{Color.CYAN}[*] Trying alternative download method...{Color.RESET}")
        filepath = os.path.join(CUSTOM_SOUND_DIR, 'background.mp3')
        cmd = ['wget', '-O', filepath, GOOGLE_DRIVE_DOWNLOAD_URL]
        subprocess.run(cmd, capture_output=True, timeout=60)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"{Color.GREEN}[+] Downloaded: background.mp3 using wget{Color.RESET}")
            return True
    except:
        pass
    
    print(f"{Color.YELLOW}[!] No custom background sound found. Using default.{Color.RESET}")
    return False

# ==================== TITLE ====================
class TitleAnimation:
    @staticmethod
    def compact_banner():
        """Compact banner style"""
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
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}OTP RETRY{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}SOUND SYSTEM{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}VOICE FEEDBACK{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}CLIPROXY{Color.RESET}     {Color.CYAN}║{Color.RESET}
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
            print(f"{Color.GREEN}[+] Playing custom MP3 background (Google Drive){Color.RESET}")
        elif os.path.exists(custom_wav) and os.path.getsize(custom_wav) > 0:
            bg_file = custom_wav
            print(f"{Color.GREEN}[+] Playing custom WAV background{Color.RESET}")
        else:
            bg_file = default_bg
            if not os.path.exists(bg_file):
                download_sound_from_github('binary_rain.wav')
                if not os.path.exists(bg_file):
                    return
            print(f"{Color.DIM}[*] Playing default background{Color.RESET}")
        
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
        return f""" {Color.GREEN}*{Color.RESET} Voice: {'Active' if self.voice_available else 'Not available'}
 {Color.GREEN}*{Color.RESET} Sound: {'Active' if self.sound_available else 'Not available'}
 {Color.GREEN}*{Color.RESET} Background: {bg_status}"""

# ==================== BROWSER PILOT MANAGER ====================
class BrowserPilotManager:
    """Termux Browser Pilot - ফেসবুক অটোমেশন ব্রাউজার কন্ট্রোলার"""
    
    def __init__(self):
        self.browser_available = self._check_browser_pilot()
        self.browser = None
        self.browser_started = False
    
    def _check_browser_pilot(self):
        """Check if termux-browser-pilot is installed"""
        try:
            import termux_browser_pilot
            return True
        except ImportError:
            return False
    
    def _install_browser_pilot(self):
        """Install termux-browser-pilot"""
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
        """Start browser using termux-browser-pilot with proxy"""
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
            
            # Check if proxy is SOCKS5
            if proxy and proxy.startswith('socks5://'):
                print(f"{Color.YELLOW}[!] SOCKS5 proxy detected. Browser may not support SOCKS5 directly.{Color.RESET}")
                print(f"{Color.YELLOW}[!] For SOCKS5, install privoxy to convert to HTTP.{Color.RESET}")
                print(f"{Color.YELLOW}[!] Trying to use proxy directly...{Color.RESET}")
                
                # Set environment variables for SOCKS5
                os.environ['http_proxy'] = proxy
                os.environ['https_proxy'] = proxy
                os.environ['all_proxy'] = proxy
            elif proxy:
                # Set proxy environment variable for HTTP
                os.environ['http_proxy'] = proxy
                os.environ['https_proxy'] = proxy
                print(f"{Color.CYAN}[*] Browser using proxy: {proxy}{Color.RESET}")
            else:
                # Clear proxy environment variables for default IP
                os.environ.pop('http_proxy', None)
                os.environ.pop('https_proxy', None)
                os.environ.pop('all_proxy', None)
                print(f"{Color.CYAN}[*] Browser using default IP (no proxy){Color.RESET}")
            
            self.browser = Browser(headless=headless)
            self.browser_started = True
            print(f"{Color.GREEN}[+] Browser started successfully{Color.RESET}")
            return True
        except Exception as e:
            print(f"{Color.RED}[-] Failed to start browser: {e}{Color.RESET}")
            return False
    
    def goto(self, url):
        """Navigate to URL"""
        if not self.browser_started:
            return False
        try:
            self.browser.goto(url)
            return True
        except:
            return False
    
    def type_text(self, selector, text):
        """Type text into field"""
        if not self.browser_started:
            return False
        try:
            self.browser.type(selector, text)
            return True
        except:
            return False
    
    def click(self, selector):
        """Click on element"""
        if not self.browser_started:
            return False
        try:
            self.browser.click(selector)
            return True
        except:
            return False
    
    def wait_for_text(self, selector, timeout=60):
        """Wait for text to appear"""
        if not self.browser_started:
            return None
        try:
            return self.browser.wait_for_text(selector, timeout=timeout)
        except:
            return None
    
    def get_text(self, selector):
        """Get text from element"""
        if not self.browser_started:
            return None
        try:
            element = self.browser.find(selector)
            return element.text if element else None
        except:
            return None
    
    def wait_for_element(self, selector, timeout=60):
        """Wait for element to appear"""
        if not self.browser_started:
            return None
        try:
            return self.browser.wait_for_element(selector, timeout=timeout)
        except:
            return None
    
    def wait_for_input(self, selector, timeout=60):
        """Wait for input field"""
        if not self.browser_started:
            return None
        try:
            return self.browser.wait_for_element(selector, timeout=timeout)
        except:
            return None
    
    def screenshot(self, filename):
        """Take screenshot"""
        if not self.browser_started:
            return False
        try:
            self.browser.screenshot(filename)
            return True
        except:
            return False
    
    def close_browser(self):
        """Close browser"""
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
    """Advanced Facebook automation with Browser Pilot + Proxy Rotation + Auto Name"""
    
    def __init__(self):
        self.is_running = False
        self.stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'otp_sent': 0
        }
        self.browser_manager = BrowserPilotManager()
        self.proxy_manager = ProxyManager()
        self.name_generator = NameGenerator()
        self.audio = None
    
    def _generate_device_fingerprint(self):
        """Generate new device fingerprint"""
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
        """Fill Facebook registration form using browser with local name"""
        try:
            # Generate local name based on country
            first_name, last_name = self.name_generator.get_random_name(country_code)
            full_name = f"{first_name} {last_name}"
            
            print(f"{Color.CYAN}  [*] Generated name: {full_name} ({country_code}){Color.RESET}")
            
            # Phone number input
            print(f"{Color.CYAN}  [*] Filling phone number: {phone_number}{Color.RESET}")
            self.browser_manager.type_text(FB_CONFIG['UI_ELEMENTS']['phone_input'], phone_number)
            time.sleep(1)
            
            print(f"{Color.CYAN}  [*] Clicking Next button{Color.RESET}")
            self.browser_manager.click(FB_CONFIG['UI_ELEMENTS']['next_button'])
            time.sleep(3)
            
            # Try to fill name if field appears
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
        """Request OTP with multiple retries"""
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
        """Complete registration with OTP"""
        try:
            print(f"{Color.CYAN}  [*] Entering OTP: {otp_code}{Color.RESET}")
            self.browser_manager.type_text(FB_CONFIG['UI_ELEMENTS']['otp_input'], otp_code)
            time.sleep(1)
            
            print(f"{Color.CYAN}  [*] Submitting OTP{Color.RESET}")
            self.browser_manager.click(FB_CONFIG['UI_ELEMENTS']['otp_submit'])
            time.sleep(3)
            return True
        except Exception as e:
            print(f"{Color.RED}  [-] OTP submit error: {e}{Color.RESET}")
            return False
    
    def _process_single_number(self, phone_number):
        """Process a single phone number with full automation + proxy rotation + auto name"""
        print(f"\n{Color.CYAN}[+] Processing: {phone_number}{Color.RESET}")
        
        # Get proxy for this number (returns None if using default IP)
        proxy, country_code = self.proxy_manager.get_proxy_for_number(phone_number)
        
        if proxy:
            print(f"{Color.GREEN}[+] Proxy: {proxy}{Color.RESET}")
        else:
            print(f"{Color.YELLOW}[!] Using default IP (no proxy){Color.RESET}")
        
        # Start browser with proxy (or without if None)
        if not self.browser_manager.start_browser(headless=False, proxy=proxy):
            print(f"{Color.RED}  [-] Failed to start browser!{Color.RESET}")
            self.stats['failed'] += 1
            return False
        
        try:
            # Facebook signup page
            print(f"{Color.CYAN}  [*] Navigating to Facebook signup...{Color.RESET}")
            self.browser_manager.goto("https://m.facebook.com/create-account")
            time.sleep(2)
            
            # Fill form with auto-generated name
            if not self._fill_registration_form(phone_number, country_code):
                print(f"{Color.RED}  [-] Failed to fill form{Color.RESET}")
                self.stats['failed'] += 1
                return False
            time.sleep(2)
            
            # Request OTP
            print(f"{Color.CYAN}  [*] Requesting OTP...{Color.RESET}")
            otp = self._request_otp_with_retry()
            
            if not otp:
                print(f"{Color.RED}  [-] OTP request failed{Color.RESET}")
                self.stats['failed'] += 1
                if self.audio:
                    self.audio.play_fail()
                    self.audio.speak_otp_fail()
                return False
            
            # Submit OTP
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
        """Process batch of phone numbers with proxy rotation"""
        if not numbers:
            print(f"{Color.RED}[-] No numbers to process{Color.RESET}")
            return
        
        print(f"\n{Color.GREEN}[+] Starting batch processing with Proxy Rotation + Auto Name{Color.RESET}")
        print(f"{Color.CYAN}[+] Total numbers: {len(numbers)}{Color.RESET}")
        print(f"{Color.CYAN}[+] OTP Retries: {FB_CONFIG['MAX_OTP_RETRIES']}{Color.RESET}")
        print(f"{Color.CYAN}[+] IP Rotation: {'Enabled' if FB_CONFIG['ROTATE_IP'] else 'Disabled'}{Color.RESET}")
        print(f"{Color.CYAN}[+] Device Rotation: {'Enabled' if FB_CONFIG['ROTATE_DEVICE'] else 'Disabled'}{Color.RESET}")
        print("-" * 60)
        
        # Refresh proxy pool
        self.proxy_manager.refresh_proxy_pool()
        
        self.is_running = True
        
        for idx, phone in enumerate(numbers, 1):
            if not self.is_running:
                break
            
            print(f"\n{Color.GOLD}{'='*50}{Color.RESET}")
            print(f"{Color.GOLD}Processing {idx}/{len(numbers)}{Color.RESET}")
            print(f"{Color.GOLD}{'='*50}{Color.RESET}")
            
            try:
                success = self._process_single_number(phone)
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
        """Stop the automation"""
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
        self.names = load_file_lines(os.path.join(data_dir, 'names.txt'))
        self.proxies = load_file_lines(os.path.join(data_dir, 'proxies.txt'))
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
        
        print(f'\n{Color.GREEN}[+] Starting bot with Proxy Rotation + Auto Name...{Color.RESET}')
        print(f'{Color.CYAN}Total numbers: {len(self.numbers)}{Color.RESET}')
        print(f'{Color.CYAN}OTP Retry Count: {FB_CONFIG["MAX_OTP_RETRIES"]}{Color.RESET}')
        print(f'{Color.CYAN}IP Rotation: {"Enabled" if FB_CONFIG["ROTATE_IP"] else "Disabled"}{Color.RESET}')
        print(f'{Color.CYAN}Device Spoofing: {"Enabled" if FB_CONFIG["ROTATE_DEVICE"] else "Disabled"}{Color.RESET}')
        print(f'{Color.YELLOW}[!] Press Ctrl+C to stop the bot anytime{Color.RESET}')
        print(f'{Color.YELLOW}[!] Press 0 and Enter to stop and go to main menu{Color.RESET}')
        print("-" * 60)
        
        self.automation_engine = FacebookAutomationEngine()
        self.automation_engine.audio = self.audio
        self.automation_engine.start_batch_processing(self.numbers)
        
        self.running = False
        print(f'\n\n{Color.GREEN}[+] ALL TASKS COMPLETE -- Success: {self.stats["success"]} | Failed: {self.stats["failed"]}{Color.RESET}')
        self.audio.play_done()
        self.audio.speak_bot_complete()
    
    def get_country(self, phone):
        phone = phone.strip().replace('+','').replace(' ','').replace('-','')
        for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
            if phone.startswith(code):
                return COUNTRY_CODES[code]
        return 'XX'

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
        self.bot_thread = None
        
        # Load proxy API key from config
        api_key = self.config.get('proxy_api_key', '')
        if api_key:
            PROXY_API_KEY = api_key
    
    def show_header(self):
        clear_screen()
        TitleAnimation.compact_banner()
        
        # Check proxy status
        proxy_stats = self.proxy_manager.get_proxy_stats()
        proxy_status = f"● {proxy_stats['total']} proxies"
        proxy_color = Color.GREEN if proxy_stats['total'] > 0 else Color.RED
        
        cliproxy_status = "● ON" if proxy_stats.get('cliproxy_enabled') else "● OFF"
        cliproxy_color = Color.GREEN if proxy_stats.get('cliproxy_enabled') else Color.RED
        
        print(f' {proxy_color}{proxy_status}{Color.RESET} Proxy Pool: {Color.WHITE}{"Ready" if proxy_stats["total"] > 0 else "Default IP Only"}{Color.RESET}')
        print(f' {cliproxy_color}{cliproxy_status}{Color.RESET} Cliproxy: {Color.WHITE}{"Enabled" if proxy_stats.get("cliproxy_enabled") else "Disabled"}{Color.RESET}')
        
        # Check browser pilot
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
        """Check for stop input during bot operation"""
        while self.bot_running:
            try:
                # Check for stdin input without blocking
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
    
    def menu_main(self):
        self.welcome_screen()
        while True:
            self.show_header()
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}MAIN MENU - PROXY + AUTO NAME{Color.RESET}{Color.CYAN}                 ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Browser Pilot Setup             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Proxy Management                 {Color.CYAN}║{Color.RESET}
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
            if choice == '1': self.menu_browser()
            elif choice == '2': self.menu_proxy()
            elif choice == '3': self.menu_license()
            elif choice == '4': self.menu_folder()
            elif choice == '5': self.menu_start_bot()
            elif choice == '6': self.menu_status()
            elif choice == '7': self.menu_audio()
            elif choice == '8': self.menu_demo()
            elif choice == '9': self.menu_help()
            elif choice == '0': self.menu_exit(); break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_proxy(self):
        while True:
            self.show_header()
            proxy_stats = self.proxy_manager.get_proxy_stats()
            
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}PROXY MANAGEMENT{Color.RESET}{Color.CYAN}                              ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Total: {Color.WHITE}{proxy_stats['total']}{Color.RESET}  Current: {Color.WHITE}{proxy_stats.get('current', 'Default IP')}{Color.RESET}  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Country: {Color.WHITE}{proxy_stats.get('country', 'XX')}{Color.RESET}  History: {Color.WHITE}{proxy_stats['history_count']}{Color.RESET}        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Using Default IP: {Color.WHITE}{'Yes' if proxy_stats.get('using_default_ip') else 'No'}{Color.RESET}{Color.CYAN}        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Cliproxy: {Color.WHITE}{'Enabled' if proxy_stats.get('cliproxy_enabled') else 'Disabled'}{Color.RESET}{Color.CYAN}                {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Refresh Proxy Pool               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Set API Key (9proxy/webshare)   {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Test Proxy Connection            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} View Proxy History               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[5]{Color.RESET} Toggle Cliproxy                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                print(f'  {Color.CYAN}[*] Refreshing proxy pool...{Color.RESET}')
                count = self.proxy_manager.refresh_proxy_pool()
                if count > 0:
                    print(f'  {Color.GREEN}[+] Proxy pool refreshed! {count} proxies available{Color.RESET}')
                else:
                    print(f'  {Color.YELLOW}[!] No proxies found. Will use default IP.{Color.RESET}')
                press_enter()
            elif choice == '2':
                api_key = input(f'  {Color.CYAN}Enter 9proxy/webshare API key: {Color.RESET}').strip()
                if api_key:
                    self.license.set_proxy_api_key(api_key)
                    self.proxy_manager.api_key = api_key
                    print(f'  {Color.GREEN}[+] API key saved!{Color.RESET}')
                press_enter()
            elif choice == '3':
                proxy = input(f'  {Color.CYAN}Enter proxy to test (http://ip:port): {Color.RESET}').strip()
                if proxy:
                    try:
                        test_proxies = {'http': proxy, 'https': proxy}
                        response = requests.get('http://ip-api.com/json', proxies=test_proxies, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            print(f'  {Color.GREEN}[+] Proxy working!{Color.RESET}')
                            print(f'  {Color.DIM}IP: {data.get("query")} | Country: {data.get("countryCode")}{Color.RESET}')
                        else:
                            print(f'  {Color.RED}[-] Proxy not working{Color.RESET}')
                    except Exception as e:
                        print(f'  {Color.RED}[-] Proxy test failed: {e}{Color.RESET}')
                press_enter()
            elif choice == '4':
                history = self.proxy_manager.proxy_history[-10:] if self.proxy_manager.proxy_history else []
                if history:
                    print(f'\n  {Color.CYAN}Last {len(history)} proxy uses:{Color.RESET}')
                    for item in history:
                        print(f'    {Color.DIM}{item["phone"]} → {item["country"]}: {item["proxy"]}{Color.RESET}')
                else:
                    print(f'\n  {Color.DIM}No proxy history yet{Color.RESET}')
                press_enter()
            elif choice == '5':
                self.proxy_manager.cliproxy_enabled = not self.proxy_manager.cliproxy_enabled
                print(f'  {Color.GREEN}[+] Cliproxy {"Enabled" if self.proxy_manager.cliproxy_enabled else "Disabled"}{Color.RESET}')
                press_enter()
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
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
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
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
                    if valid: self.audio.speak_license_verified()
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
                # Select/Connect folder - check if exists
                folder_path = self.data_dir
                if os.path.exists(folder_path):
                    print(f'\n  {Color.GREEN}[+] Folder found: {folder_path}{Color.RESET}')
                    self.audio.speak_folder_found()
                    # Check for numbers.txt
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
                # View folder contents - show files and count
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
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_start_bot(self):
        self.show_header()
        
        # Check if folder exists
        folder_path = self.data_dir
        folder_exists = os.path.exists(folder_path)
        
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}START BOT - PROXY + AUTO NAME{Color.RESET}{Color.CYAN}                     ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Numbers: {len(load_file_lines(os.path.join(self.data_dir, "numbers.txt")))}                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.DIM}{self.license.get_license_key() or "Not set"}{Color.RESET}{Color.CYAN}             ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Browser: {Color.DIM}{"● Ready" if self.browser_manager.browser_available else "○ Not installed"}{Color.RESET}{Color.CYAN}    ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Proxy Pool: {Color.DIM}{self.proxy_manager.get_proxy_stats()["total"]} proxies{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Cliproxy: {Color.DIM}{"Enabled" if self.proxy_manager.cliproxy_enabled else "Disabled"}{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Auto Name: {Color.DIM}{"ON (Country based)"}{Color.RESET}{Color.CYAN}                 ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  OTP Retry: {Color.DIM}{FB_CONFIG["MAX_OTP_RETRIES"]} times{Color.RESET}{Color.CYAN}                   ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  IP Rotation: {Color.DIM}{"ON" if FB_CONFIG["ROTATE_IP"] else "OFF"}{Color.RESET}{Color.CYAN}                 ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Folder Status: {Color.DIM}{"✓ Exists" if folder_exists else "✗ Not found"}{Color.RESET}{Color.CYAN}        ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        
        if not folder_exists:
            print(f'\n{Color.RED}[-] Data folder not found! Please set correct folder path in Data Folder menu.{Color.RESET}')
            self.audio.speak_folder_not_found()
            press_enter()
            return
        
        if not self.license.get_license_key():
            print(f'\n{Color.RED}[-] No license key set! Please set license first.{Color.RESET}')
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
        
        print(f'\n{Color.YELLOW}[!] Press 0 and Enter to stop the bot and return to main menu{Color.RESET}')
        print(f'\n{Color.YELLOW}[!] Press Ctrl+C to stop the bot anytime{Color.RESET}')
        
        # Start stop listener thread
        self.bot_running = True
        stop_thread = threading.Thread(target=self.check_stop_input, daemon=True)
        stop_thread.start()
        
        self.bot = FacebookBot(self.data_dir, self.license.get_license_key(), self.audio)
        self.audio.speak_bot_starting()
        self.bot.run_bot(workers)
        
        self.bot_running = False
        
        # Wait for stop thread to finish
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
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Current Proxy: {Color.WHITE}{proxy_stats.get("current", "Default IP")}{Color.RESET}{Color.CYAN}          ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Proxy Country: {Color.WHITE}{proxy_stats.get("country", "XX")}{Color.RESET}{Color.CYAN}            ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Using Default IP: {Color.WHITE}{'Yes' if proxy_stats.get('using_default_ip') else 'No'}{Color.RESET}{Color.CYAN}      ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Cliproxy: {Color.WHITE}{'Enabled' if proxy_stats.get('cliproxy_enabled') else 'Disabled'}{Color.RESET}{Color.CYAN}        ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Auto Name: {Color.WHITE}{"Enabled (Country based)"}{Color.RESET}{Color.CYAN}         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} License: {Color.WHITE}{"Active" if self.license.get_license_key() else "None"}{Color.RESET}{Color.CYAN}                  ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Data Dir: {Color.WHITE}{self.data_dir}{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {self.audio.get_status()}{Color.CYAN}         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Automation: {Color.WHITE}{"Running" if self.bot and self.bot.running else "Idle"}{Color.RESET}{Color.CYAN}          ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} OTP Retry: {Color.WHITE}{FB_CONFIG["MAX_OTP_RETRIES"]} times{Color.RESET}{Color.CYAN}                 ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} IP Rotation: {Color.WHITE}{"Enabled" if FB_CONFIG["ROTATE_IP"] else "Disabled"}{Color.RESET}{Color.CYAN}         ║{Color.RESET}
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
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
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
        elif choice == '0': pass
        else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_help(self):
        self.show_header()
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}HELP - PROXY + AUTO NAME{Color.RESET}{Color.CYAN}                        ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [?] {Color.WHITE}How to Use{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  1. Install Browser Pilot (Option 1)               {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  2. Set API Key for 9proxy (Option 2)              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  3. Refresh Proxy Pool (Option 2)                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  4. Set up data folder (Option 4)                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  5. Add phone numbers to numbers.txt              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  6. Enter license key (Option 3)                   {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  7. Start the bot (Option 5)                      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [#] {Color.WHITE}Features{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Automatic proxy rotation per number            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Country detection from phone number            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Auto-generates local names per country         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Matches proxy country with number country      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Uses default IP if proxy fails                 {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Cliproxy SOCKS5 support with dynamic region    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - 150+ countries supported                       {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Uses termux-browser-pilot                      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Real Firefox/Chromium browser                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Human-like typing & clicks                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - OTP Retry: 3 times                             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Voice feedback for folder operations           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Stop bot with '0' key                          {Color.CYAN}║{Color.RESET}
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