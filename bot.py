#!/usr/bin/env python3
"""
Ridol SaaS Tool v20.0 - ChatGPT Account Creator
With Live Training Mode & Next Number Button
Author: Ridol Islam
"""

import os
import sys
import time
import json
import random
import threading
import subprocess
import zipfile
import requests
import re
import socket
from datetime import datetime
from flask import Flask, send_file, render_template_string, request, jsonify
from selenium.webdriver.chrome.service import Service

# ==================== FLASK APP FOR TRAINING ====================
MACRO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'robot_steps_chatgpt.json')
LIVE_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'liveview.png')
stream_app = Flask(__name__)
shared_driver = None
is_training_mode = False
training_complete = False
current_phone = ''
next_number_triggered = False
training_phone_list = []
training_phone_index = 0

# ==================== GET LOCAL IP ====================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

# ==================== TRAINING SERVER ROUTES ====================
@stream_app.route('/')
def index():
    global training_phone_list, training_phone_index, current_phone
    
    total = len(training_phone_list)
    current_idx = training_phone_index + 1 if training_phone_index < total else total
    phone_display = current_phone if current_phone else 'Not started'
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ridol Tool - ChatGPT Training</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: #0a0e17; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, sans-serif; padding: 20px; min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; }
            .header {
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #2a3a5c;
                margin-bottom: 20px;
                text-align: center;
            }
            .header h1 { color: #f7971e; font-size: 24px; }
            .header .subtitle { color: #8899aa; font-size: 14px; }
            .header .mode-label { 
                display: inline-block; 
                padding: 4px 15px; 
                border-radius: 20px; 
                font-size: 12px; 
                font-weight: bold;
                margin-top: 5px;
                background: #00c85320; color: #00c853; border: 1px solid #00c85340;
            }
            .phone-display {
                background: #0d1117;
                padding: 10px 20px;
                border-radius: 8px;
                margin: 10px 0;
                border: 1px solid #2a3a5c;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
            }
            .phone-display .phone { color: #ffd200; font-weight: bold; font-size: 18px; }
            .phone-display .progress { color: #8899aa; font-size: 14px; }
            .instructions {
                background: #1a1a2e;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #2a3a5c;
                margin-bottom: 20px;
            }
            .instructions h3 { color: #f7971e; margin-bottom: 10px; }
            .instructions li { padding: 8px 0; color: #b0b0b0; border-bottom: 1px solid #1a1a2e; list-style: none; }
            .instructions li:last-child { border-bottom: none; }
            .instructions .step-num { color: #f7971e; font-weight: bold; display: inline-block; width: 25px; }
            #screen { 
                width: 100%; max-width: 600px; border: 2px solid #f7971e; cursor: crosshair; border-radius: 8px;
                display: block; margin: 0 auto;
            }
            .controls {
                background: #1a1a2e;
                padding: 15px;
                border-radius: 12px;
                border: 1px solid #2a3a5c;
                margin: 15px 0;
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
            }
            .controls button {
                padding: 10px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 14px;
            }
            .btn-save { background: #00c853; color: white; }
            .btn-save:hover { background: #00e676; transform: scale(1.02); }
            .btn-next { background: #f7971e; color: #1a1a2e; }
            .btn-next:hover { background: #ffd200; transform: scale(1.02); }
            .btn-clear { background: #ff1744; color: white; }
            .btn-clear:hover { background: #ff5252; transform: scale(1.02); }
            .btn-refresh { background: #2979ff; color: white; }
            .btn-refresh:hover { background: #448aff; transform: scale(1.02); }
            .status-bar {
                background: #0d1117;
                padding: 12px 20px;
                border-radius: 8px;
                margin: 10px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                border: 1px solid #2a3a5c;
            }
            .status-bar .count { color: #f7971e; font-weight: bold; font-size: 18px; }
            .status-bar .label { color: #8899aa; }
            .info-text { color: #8899aa; font-size: 12px; text-align: center; padding: 10px; }
            .highlight { color: #ffd200; }
            .next-number-section {
                background: #0d1117;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                border: 1px solid #2a3a5c;
                text-align: center;
            }
            .next-number-section .info { color: #8899aa; font-size: 13px; margin-bottom: 10px; }
            @media (max-width: 600px) {
                .header h1 { font-size: 18px; }
                .controls { flex-direction: column; align-items: stretch; }
                .controls button { width: 100%; }
                #screen { max-width: 100%; }
                .phone-display { flex-direction: column; text-align: center; gap: 5px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 ChatGPT Training Mode</h1>
                <div class="subtitle">Teach the bot how to create ChatGPT accounts</div>
                <div class="mode-label">📌 ChatGPT Signup Training</div>
            </div>

            <div class="phone-display">
                <span class="phone">📱 Current: {{ phone }}</span>
                <span class="progress">Progress: {{ current_index }}/{{ total }}</span>
            </div>

            <div class="instructions">
                <h3>📋 Instructions:</h3>
                <ul>
                    <li><span class="step-num">1.</span> Open ChatGPT login page</li>
                    <li><span class="step-num">2.</span> Click "Continue with phone"</li>
                    <li><span class="step-num">3.</span> Enter phone number (without country code)</li>
                    <li><span class="step-num">4.</span> Click Continue</li>
                    <li><span class="step-num">5.</span> Click <span class="highlight">"Save & Next"</span> when done</li>
                </ul>
            </div>

            <div class="status-bar">
                <span class="label">📌 Steps Recorded:</span>
                <span class="count" id="stepCount">0</span>
            </div>

            <div class="controls">
                <button class="btn-save" onclick="saveAndNext()">✅ Save & Next</button>
                <button class="btn-refresh" onclick="location.reload()">🔄 Refresh</button>
                <button class="btn-clear" onclick="clearSteps()">🗑️ Clear</button>
            </div>

            <div class="next-number-section">
                <div class="info">💡 After completing training, click "Save & Next"</div>
                <button class="btn-next" onclick="saveAndNext()">➡️ Save & Next Number</button>
            </div>

            <img id="screen" src="/stream" onclick="sendClick(event)" alt="Live View">

            <p class="info-text">
                💡 Click on any <span class="highlight">button or input field</span> to record it.
                <br>🔄 Screen updates every 1 second.
            </p>
        </div>

        <script>
            let stepCount = 0;
            
            function updateStepCount() {
                fetch('/step_count')
                    .then(r => r.json())
                    .then(data => {
                        stepCount = data.count;
                        document.getElementById('stepCount').textContent = stepCount;
                    })
                    .catch(() => {});
            }
            
            setInterval(updateStepCount, 1000);
            
            function sendClick(event) {
                let img = document.getElementById('screen');
                let rect = img.getBoundingClientRect();
                let x = (event.clientX - rect.left) / rect.width;
                let y = (event.clientY - rect.top) / rect.height;
                
                fetch('/remote_click', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({x: x, y: y})
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        updateStepCount();
                        img.style.borderColor = '#00c853';
                        setTimeout(() => img.style.borderColor = '#f7971e', 300);
                    }
                })
                .catch(() => {});
            }
            
            function saveAndNext() {
                if (stepCount === 0) {
                    alert('⚠️ Please record at least one step first!');
                    return;
                }
                if (confirm('✅ Save steps and go to next number?')) {
                    fetch('/save_and_next', { method: 'POST' })
                        .then(() => {
                            alert('✅ Steps saved! Moving to next number...');
                            window.location.reload();
                        });
                }
            }
            
            function clearSteps() {
                if (confirm('🗑️ Clear all recorded steps?')) {
                    fetch('/clear_steps', { method: 'POST' })
                        .then(() => updateStepCount());
                }
            }
            
            setInterval(function(){
                document.getElementById('screen').src = '/stream?' + new Date().getTime();
            }, 1000);
        </script>
    </body>
    </html>
    """, 
    phone=current_phone if current_phone else 'Not started',
    current_index=training_phone_index + 1 if training_phone_index < len(training_phone_list) else len(training_phone_list),
    total=len(training_phone_list) if training_phone_list else 1
    )

@stream_app.route('/stream')
def stream():
    return send_file(LIVE_IMG, mimetype='image/png') if os.path.exists(LIVE_IMG) else "Loading..."

@stream_app.route('/remote_click', methods=['POST'])
def remote_click():
    global shared_driver
    if shared_driver:
        try:
            data = request.json
            size = shared_driver.get_window_size()
            real_x = int(data['x'] * size['width'])
            real_y = int(data['y'] * size['height'])
            
            element = shared_driver.execute_script(f"return document.elementFromPoint({real_x}, {real_y});")
            if element:
                element_id = element.get_attribute('id')
                element_name = element.get_attribute('name')
                element_class = element.get_attribute('class')
                tag = element.tag_name
                
                if element_id:
                    selector = f"#{element_id}"
                elif element_name:
                    selector = f"[name='{element_name}']"
                elif element_class:
                    classes = element_class.split()
                    if classes:
                        selector = f".{classes[0]}"
                    else:
                        selector = tag
                else:
                    selector = tag
                
                steps = []
                if os.path.exists(MACRO_FILE):
                    with open(MACRO_FILE, 'r') as f:
                        steps = json.load(f)
                
                steps.append({
                    'action': 'click',
                    'selector': selector,
                    'tag': tag,
                    'timestamp': time.time()
                })
                
                with open(MACRO_FILE, 'w') as f:
                    json.dump(steps, f, indent=2)
                
                shared_driver.execute_script("arguments[0].click();", element)
                
                return jsonify({'success': True, 'selector': selector, 'count': len(steps)})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False})

@stream_app.route('/step_count')
def step_count():
    if os.path.exists(MACRO_FILE):
        try:
            with open(MACRO_FILE, 'r') as f:
                steps = json.load(f)
                return jsonify({'count': len(steps)})
        except:
            return jsonify({'count': 0})
    return jsonify({'count': 0})

@stream_app.route('/save_and_next', methods=['POST'])
def save_and_next():
    global is_training_mode, training_complete, next_number_triggered
    is_training_mode = False
    training_complete = True
    next_number_triggered = True
    return jsonify({'success': True})

@stream_app.route('/clear_steps', methods=['POST'])
def clear_steps():
    if os.path.exists(MACRO_FILE):
        os.remove(MACRO_FILE)
    return jsonify({'success': True})

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
APP_VERSION = 'v20.0'

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
    ORANGE = '\033[38;5;208m'

# ==================== COUNTRY FUNCTIONS ====================
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

# ==================== SCREENSHOT & ERROR LOGIC ====================
def take_error_screenshot(driver, phone, excel_path):
    try:
        base_dir = os.path.dirname(excel_path)
        screenshot_dir = os.path.join(base_dir, 'Bot_Errors')
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"error_{phone}_{timestamp}.png"
        file_path = os.path.join(screenshot_dir, file_name)
        driver.save_screenshot(file_path)
        print(f"{Color.YELLOW}[!] Screenshot saved to: {file_path}{Color.RESET}")
        return file_path
    except Exception as e:
        print(f"{Color.RED}[-] Screenshot failed: {e}{Color.RESET}")
        return None

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
        
        for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
            number_val = row[1] if len(row) > 1 else None
            
            if number_val:
                number_str = str(number_val).strip()
                if 'E+' in number_str:
                    number_str = "{:.0f}".format(float(number_val))
                clean_number = re.sub(r'[^0-9]', '', number_str)
                
                if len(clean_number) >= 7:
                    numbers.append({
                        'number': clean_number,
                        'country': get_country_from_phone(clean_number)
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

# ==================== TRAINING MODE EXECUTOR ====================
def execute_training_mode(driver, phone_number, excel_path, phone_list, current_index):
    global is_training_mode, training_complete, next_number_triggered, current_phone
    global training_phone_list, training_phone_index
    
    current_phone = phone_number
    training_phone_list = phone_list
    training_phone_index = current_index
    
    print(f"{Color.GOLD}{'='*55}{Color.RESET}")
    print(f"{Color.GOLD}[!] 🎯 TRAINING MODE ACTIVATED!{Color.RESET}")
    print(f"{Color.CYAN}[*] 🌐 Live View URL: http://{LOCAL_IP}:5000{Color.RESET}")
    print(f"{Color.CYAN}[*] 📱 Current Number: {phone_number}{Color.RESET}")
    print(f"{Color.YELLOW}[*] 📋 Perform the ChatGPT signup process manually{Color.RESET}")
    print(f"{Color.YELLOW}[*] 🖱️ Every click you make will be recorded{Color.RESET}")
    print(f"{Color.YELLOW}[*] ✅ Click 'Save & Next' when done{Color.RESET}")
    print(f"{Color.GOLD}{'='*55}{Color.RESET}")
    
    is_training_mode = True
    training_complete = False
    next_number_triggered = False
    
    if not any(t.name == 'FlaskServer' for t in threading.enumerate()):
        threading.Thread(target=lambda: stream_app.run(host='0.0.0.0', port=5000, threaded=True, debug=False), 
                        name='FlaskServer', daemon=True).start()
        time.sleep(2)
    
    while is_training_mode and not training_complete and not next_number_triggered:
        driver.save_screenshot(LIVE_IMG)
        time.sleep(1)
    
    print(f"{Color.GREEN}[+] Training complete! Steps saved.{Color.RESET}")
    
    if os.path.exists(MACRO_FILE):
        with open(MACRO_FILE, 'r') as f:
            steps = json.load(f)
        if steps:
            print(f"{Color.CYAN}[*] Executing {len(steps)} recorded steps...{Color.RESET}")
            for step in steps:
                try:
                    if step['action'] == 'click':
                        from selenium.webdriver.support.ui import WebDriverWait
                        from selenium.webdriver.support import expected_conditions as EC
                        from selenium.webdriver.common.by import By
                        element = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, step['selector']))
                        )
                        element.click()
                        print(f"{Color.GREEN}[✓] Executed: {step['selector']}{Color.RESET}")
                        time.sleep(1)
                except Exception as e:
                    print(f"{Color.YELLOW}[!] Step failed: {e}{Color.RESET}")
            print(f"{Color.GREEN}[+] Macro playback complete!{Color.RESET}")
            return True
        else:
            print(f"{Color.RED}[-] No steps recorded!{Color.RESET}")
            return False
    else:
        print(f"{Color.RED}[-] No steps recorded!{Color.RESET}")
        return False

# ==================== CHATGPT SIGNUP SENDER ====================
def chatgpt_signup_sender(driver, phone_number, excel_path, training_mode=False, phone_list=None, current_index=0):
    global shared_driver
    shared_driver = driver
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        
        print(f"{Color.CYAN}[*] ChatGPT Signup: {phone_number}{Color.RESET}")
        
        # ChatGPT Login URL
        driver.get("https://chatgpt.com/auth/login")
        time.sleep(3)
        
        if training_mode:
            return execute_training_mode(driver, phone_number, excel_path, phone_list, current_index)
        else:
            # Normal Mode - Auto
            try:
                print(f"{Color.CYAN}[*] Looking for phone input...{Color.RESET}")
                
                # Click on phone option if available
                try:
                    phone_option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Phone')]"))
                    )
                    phone_option.click()
                    time.sleep(1)
                except:
                    pass
                
                # Find phone input
                phone_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "phone_number"))
                )
                phone_input.clear()
                phone_input.send_keys(phone_number)
                time.sleep(1)
                
                print(f"{Color.GREEN}[✓] Phone entered: {phone_number}{Color.RESET}")
                
                # Click Continue
                continue_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
                )
                continue_btn.click()
                time.sleep(2)
                
                print(f"{Color.GREEN}[+] Continue clicked! OTP sent to: {phone_number}{Color.RESET}")
                return True
                
            except Exception as e:
                print(f"{Color.RED}[-] Error: {e}{Color.RESET}")
                take_error_screenshot(driver, phone_number, excel_path)
                return False
            
    except Exception as e:
        print(f"{Color.RED}[-] Crash: {e}{Color.RESET}")
        take_error_screenshot(driver, phone_number, excel_path)
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
        print(f"         {Color.PINK}ChatGPT Account Creator{Color.RESET}")
        
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

    def run_chatgpt_creator(self):
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
        
        print(f"\n{Color.CYAN}Select Mode:{Color.RESET}")
        print(f"  {Color.GREEN}[1]{Color.RESET} Normal Mode (Auto ChatGPT Signup)")
        print(f"  {Color.GOLD}[2]{Color.RESET} Training Mode (Record & Playback)")
        mode_choice = input(f"\n{Color.BOLD}Enter choice: {Color.RESET}").strip()
        training_mode = (mode_choice == '2')
        
        if training_mode:
            if not any(t.name == 'FlaskServer' for t in threading.enumerate()):
                threading.Thread(target=lambda: stream_app.run(host='0.0.0.0', port=5000, threaded=True, debug=False), 
                                name='FlaskServer', daemon=True).start()
                time.sleep(2)
            print(f"\n{Color.GREEN}[+] Training server started!{Color.RESET}")
            print(f"{Color.CYAN}[+] URL: http://{LOCAL_IP}:5000{Color.RESET}")
            print(f"{Color.YELLOW}[!] Open this URL in your browser{Color.RESET}")
            print(f"{Color.YELLOW}[!] Complete the ChatGPT signup process manually{Color.RESET}")
            print(f"{Color.YELLOW}[!] Click 'Save & Next' when done{Color.RESET}")
            time.sleep(3)
        
        print(f"\n{Color.GREEN}[+] Starting ChatGPT Account Creator...{Color.RESET}")
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
            
            print(f"\n{Color.GOLD}{'='*50}{Color.RESET}")
            print(f"{Color.GOLD}[{idx}/{len(numbers_data)}] Phone: {phone} | Country: {country}{Color.RESET}")
            print(f"{Color.GOLD}{'='*50}{Color.RESET}")
            
            proxy_data = self.core.get_proxy_and_deduct(country)
            if not proxy_data:
                print(f"{Color.RED}[✗] No proxy! Credits: {self.core.credits}{Color.RESET}")
                no_proxy_count += 1
                failed_count += 1
                continue

            browser = StealthBrowser(proxy_data)
            if browser.start():
                success = chatgpt_signup_sender(browser.driver, phone, self.core.excel_file, training_mode, numbers_data, idx-1)
                if success:
                    success_count += 1
                    print(f"{Color.GREEN}[✓] Success: {phone}{Color.RESET}")
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
            print(f"  {Color.CYAN}│{Color.RESET}   MAIN MENU                           {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}├──────────────────────────────────────────┤{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Start ChatGPT Creator              {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Data Folder Setup                  {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[3]{Color.RESET} License Management                 {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Install Dependencies               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")

            choice = input(f"\n{Color.BOLD} Enter choice: {Color.RESET}").strip()
            
            if choice == '1': self.run_chatgpt_creator()
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
                subprocess.run("pkg update -y && pkg install -y tur-repo python chromium chromedriver && pip install --upgrade pip && pip install selenium requests openpyxl flask flask-cors", shell=True)
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