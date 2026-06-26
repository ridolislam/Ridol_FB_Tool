#!/usr/bin/env python3
"""
Ridol FB Tool v4.0 - Shizuku Automation Edition
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
APP_VERSION = 'v4.0'

os.makedirs(SOUND_DIR, exist_ok=True)
os.makedirs(CUSTOM_SOUND_DIR, exist_ok=True)

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

# ==================== SHIZUKU API ====================

class ShizukuAPI:
    """Shizuku API for Android automation - Complete"""
    
    SHIZUKU_PACKAGE = "moe.shizuku.privileged.api"
    
    @staticmethod
    def check_shizuku():
        """Check if Shizuku is running"""
        try:
            result = subprocess.run(['adb', 'shell', 'ps', '|', 'grep', ShizukuAPI.SHIZUKU_PACKAGE], 
                                   capture_output=True, text=True)
            return ShizukuAPI.SHIZUKU_PACKAGE in result.stdout
        except:
            return False
    
    @staticmethod
    def start_shizuku():
        """Start Shizuku server"""
        try:
            print(f"{Color.CYAN}[*] Starting Shizuku...{Color.RESET}")
            cmd = f"adb shell am startservice -n {ShizukuAPI.SHIZUKU_PACKAGE}/.BinderService"
            subprocess.run(cmd, shell=True, capture_output=True)
            time.sleep(2)
            return ShizukuAPI.check_shizuku()
        except Exception as e:
            print(f"{Color.RED}[-] Shizuku start error: {e}{Color.RESET}")
            return False
    
    @staticmethod
    def shell_command(command):
        """Execute shell command via Shizuku"""
        try:
            cmd = f"adb shell {command}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            print(f"{Color.RED}[-] Shell error: {e}{Color.RESET}")
            return None
    
    @staticmethod
    def tap(x, y):
        """Tap at coordinates"""
        return ShizukuAPI.shell_command(f"input tap {x} {y}")
    
    @staticmethod
    def swipe(x1, y1, x2, y2, duration=200):
        """Swipe from (x1,y1) to (x2,y2)"""
        return ShizukuAPI.shell_command(f"input swipe {x1} {y1} {x2} {y2} {duration}")
    
    @staticmethod
    def text(text):
        """Type text"""
        text = text.replace("'", "\\'").replace('"', '\\"')
        return ShizukuAPI.shell_command(f"input text '{text}'")
    
    @staticmethod
    def keyevent(keycode):
        """Send key event"""
        return ShizukuAPI.shell_command(f"input keyevent {keycode}")
    
    @staticmethod
    def open_app(package_name):
        """Open app by package name"""
        return ShizukuAPI.shell_command(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
    
    @staticmethod
    def close_app(package_name):
        """Close app by package name"""
        return ShizukuAPI.shell_command(f"am force-stop {package_name}")
    
    @staticmethod
    def clear_app_data(package_name):
        """Clear app data to simulate new device"""
        return ShizukuAPI.shell_command(f"pm clear {package_name}")
    
    @staticmethod
    def get_current_app():
        """Get current foreground app"""
        result = ShizukuAPI.shell_command("dumpsys window | grep mCurrentFocus")
        if result:
            try:
                return result.split('/')[0].split(' ')[-1]
            except:
                pass
        return None
    
    @staticmethod
    def wait_for_app(package_name, timeout=10):
        """Wait for app to appear"""
        start = time.time()
        while time.time() - start < timeout:
            current = ShizukuAPI.get_current_app()
            if current and package_name in current:
                return True
            time.sleep(0.5)
        return False
    
    @staticmethod
    def get_screen_size():
        """Get screen size"""
        result = ShizukuAPI.shell_command("wm size")
        if result:
            try:
                return result.split(':')[-1].strip()
            except:
                pass
        return "1080x1920"
    
    @staticmethod
    def set_device_id(android_id):
        """Change Android ID using Shizuku"""
        return ShizukuAPI.shell_command(f"settings put secure android_id {android_id}")
    
    @staticmethod
    def get_device_id():
        """Get current Android ID"""
        return ShizukuAPI.shell_command("settings get secure android_id")
    
    @staticmethod
    def toggle_wifi(on=True):
        """Toggle WiFi on/off"""
        state = "enable" if on else "disable"
        return ShizukuAPI.shell_command(f"svc wifi {state}")
    
    @staticmethod
    def get_ip():
        """Get current IP address"""
        result = ShizukuAPI.shell_command("ip route get 1 | awk '{print $NF;exit}'")
        if result:
            return result
        return None
    
    @staticmethod
    def get_ui_dump():
        """Get UI hierarchy dump"""
        return ShizukuAPI.shell_command("uiautomator dump /sdcard/ui.xml && cat /sdcard/ui.xml")

# ==================== PROXY MANAGER ====================

class ProxyManager:
    """Proxy rotation management"""
    
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.load_proxies()
    
    def load_proxies(self):
        """Load proxies from file"""
        proxy_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proxies.txt')
        if os.path.exists(proxy_file):
            try:
                with open(proxy_file, 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except:
                pass
        
        if not self.proxies:
            self.proxies = [
                "http://proxy1.example.com:8080",
                "http://proxy2.example.com:8080",
                "http://proxy3.example.com:8080",
                "http://proxy4.example.com:8080",
                "http://proxy5.example.com:8080"
            ]
    
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index % len(self.proxies)]
        self.current_index += 1
        return proxy

# ==================== DEVICE SPOOFER ====================

class DeviceSpoofer:
    """Device ID and fingerprint spoofing"""
    
    @staticmethod
    def generate_random_device_id():
        """Generate random Android ID"""
        import random
        import string
        return ''.join(random.choices(string.hexdigits, k=16)).lower()
    
    @staticmethod
    def spoof_device():
        """Spoof device using Shizuku"""
        try:
            new_id = DeviceSpoofer.generate_random_device_id()
            result = ShizukuAPI.set_device_id(new_id)
            if result is not None:
                print(f"{Color.GREEN}[+] Device ID changed to: {new_id}{Color.RESET}")
                return new_id
            return None
        except Exception as e:
            print(f"{Color.RED}[-] Device spoof error: {e}{Color.RESET}")
            return None
    
    @staticmethod
    def reset_app(package_name):
        """Clear app data"""
        result = ShizukuAPI.clear_app_data(package_name)
        if result is not None:
            print(f"{Color.GREEN}[+] App data cleared: {package_name}{Color.RESET}")
            return True
        return False

# ==================== SERVER API ====================

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

# ==================== GITHUB SOUND DOWNLOAD ====================

GITHUB_SOUND_URL = "https://raw.githubusercontent.com/ridolislam/Ridol_FB_Tool/main/sounds"
GITHUB_CUSTOM_SOUND_URL = "https://raw.githubusercontent.com/ridolislam/Ridol_FB_Tool/main/custom_sounds"

def download_sound_from_github(filename, is_custom=False):
    """Download sound file from GitHub"""
    if is_custom:
        url = f"{GITHUB_CUSTOM_SOUND_URL}/{filename}"
        filepath = os.path.join(CUSTOM_SOUND_DIR, filename)
    else:
        url = f"{GITHUB_SOUND_URL}/{filename}"
        filepath = os.path.join(SOUND_DIR, filename)
    
    try:
        print(f"{Color.CYAN}[*] Downloading {filename}...{Color.RESET}")
        response = requests.get(url, stream=True, timeout=30)
        
        if response.status_code != 200:
            print(f"{Color.YELLOW}[!] {filename} not found (404){Color.RESET}")
            return None
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"{Color.GREEN}[+] Downloaded: {filename}{Color.RESET}")
        return filepath
    except Exception as e:
        print(f"{Color.RED}[-] Download error: {e}{Color.RESET}")
        return None

def download_all_sounds():
    """Download all default sound files"""
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
            download_sound_from_github(sound, is_custom=False)
        else:
            print(f"{Color.DIM}[*] {sound} already exists{Color.RESET}")

def download_custom_background():
    """Download custom background MP3"""
    custom_mp3 = os.path.join(CUSTOM_SOUND_DIR, 'background.mp3')
    custom_wav = os.path.join(CUSTOM_SOUND_DIR, 'background.wav')
    
    if os.path.exists(custom_mp3) or os.path.exists(custom_wav):
        print(f"{Color.DIM}[*] Custom background sound already exists{Color.RESET}")
        return True
    
    print(f"{Color.CYAN}[*] Checking for custom background...{Color.RESET}")
    
    result = download_sound_from_github('background.mp3', is_custom=True)
    if result:
        return True
    
    result = download_sound_from_github('background.wav', is_custom=True)
    if result:
        return True
    
    print(f"{Color.YELLOW}[!] No custom background found{Color.RESET}")
    return False

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
                if filename.endswith('.mp3'):
                    download_sound_from_github(filename, is_custom=True)
                else:
                    download_sound_from_github(filename, is_custom=False)
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
        
        if os.path.exists(custom_mp3):
            bg_file = custom_mp3
            print(f"{Color.GREEN}[+] Playing custom MP3 background{Color.RESET}")
        elif os.path.exists(custom_wav):
            bg_file = custom_wav
            print(f"{Color.GREEN}[+] Playing custom WAV background{Color.RESET}")
        else:
            bg_file = default_bg
            if not os.path.exists(bg_file):
                download_sound_from_github('binary_rain.wav', is_custom=False)
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
    def speak_device_connected(self): self.speak('Device connected')
    def speak_license_verified(self): self.speak('License verified', 'high')
    def speak_bot_starting(self): self.speak('Starting automation', 'high')
    def speak_bot_complete(self): self.speak('All tasks completed', 'high')
    def speak_goodbye(self): self.speak('Goodbye, stay secure', 'high')
    def speak_account_created(self): self.speak('Account created')
    
    def get_status(self):
        bg_status = 'Playing' if self.bg_playing else 'Stopped'
        if self.background_file:
            bg_status += f' ({os.path.basename(self.background_file)})'
        return f""" {Color.GREEN}*{Color.RESET} Voice: {'Active' if self.voice_available else 'Not available'}
 {Color.GREEN}*{Color.RESET} Sound: {'Active' if self.sound_available else 'Not available'}
 {Color.GREEN}*{Color.RESET} Background: {bg_status}"""

# ==================== 3D TITLE ====================

class TitleAnimation:
    @staticmethod
    def big_3d_title():
        os.system('clear')
        
        border_top = f"{Color.CYAN}+{'-' * 70}+{Color.RESET}"
        border_bottom = f"{Color.CYAN}+{'-' * 70}+{Color.RESET}"
        
        print(border_top)
        print(f"{Color.CYAN}|{Color.RESET}{' ' * 70}{Color.CYAN}|{Color.RESET}")
        
        title_line1 = f"{Color.CYAN}|{Color.RESET}  {Color.GOLD}*{Color.RESET}  {Color.WHITE}{Color.BOLD}RIDOL FB TOOL{Color.RESET}  {Color.DIM}v4.0{Color.RESET}  {Color.GOLD}*{Color.RESET}  {Color.DIM}Shizuku Auto{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(title_line1)
        
        subtitle = f"{Color.CYAN}|{Color.RESET}  {Color.DIM}Facebook Automation{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(subtitle)
        
        print(f"{Color.CYAN}|{Color.RESET}{' ' * 70}{Color.CYAN}|{Color.RESET}")
        
        shizuku_running = ShizukuAPI.check_shizuku()
        status_text = "SHIZUKU RUNNING" if shizuku_running else "SHIZUKU STOPPED"
        status_color = Color.GREEN if shizuku_running else Color.RED
        
        status_line = f"{Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} Device: {Color.WHITE}No device{Color.RESET}  {Color.GREEN}*{Color.RESET} License: {Color.YELLOW}No License{Color.RESET}  {status_color}{status_text}{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(status_line)
        
        shizuku_line = f"{Color.CYAN}|{Color.RESET}  {Color.CYAN}🤖{Color.RESET} Automation: {Color.DIM}Facebook{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(shizuku_line)
        
        print(border_bottom)
        print()
        time.sleep(0.5)

# ==================== FACEBOOK AUTOMATION ====================

class FacebookAutomation:
    """Facebook automation using Shizuku"""
    
    FACEBOOK_PACKAGE = "com.facebook.katana"
    FACEBOOK_LITE_PACKAGE = "com.facebook.lite"
    
    DEFAULT_COORDS = {
        "create_account_button": (540, 300),
        "email_phone_field": (540, 500),
        "continue_button": (540, 800),
        "name_first": (300, 400),
        "name_last": (780, 400),
        "birthday_month": (300, 550),
        "birthday_day": (540, 550),
        "birthday_year": (780, 550),
        "gender_male": (300, 700),
        "gender_female": (780, 700),
        "sign_up_button": (540, 900),
        "resend_otp": (540, 700)
    }
    
    def __init__(self):
        self.screen_width = 1080
        self.screen_height = 1920
        self.coords = self.DEFAULT_COORDS.copy()
        self.proxy_manager = ProxyManager()
        self.device_spoofer = DeviceSpoofer()
        self._update_coords()
    
    def _update_coords(self):
        size = ShizukuAPI.get_screen_size()
        if size:
            try:
                w, h = size.split('x')
                self.screen_width = int(w)
                self.screen_height = int(h)
                
                scale_x = self.screen_width / 1080
                scale_y = self.screen_height / 1920
                
                for key, (x, y) in self.DEFAULT_COORDS.items():
                    self.coords[key] = (int(x * scale_x), int(y * scale_y))
            except:
                pass
    
    def _tap(self, x, y):
        for attempt in range(3):
            result = ShizukuAPI.tap(x, y)
            if result is not None:
                return True
            time.sleep(0.5)
        return False
    
    def _type_text(self, text, field_coords=None):
        if field_coords:
            x, y = field_coords
            self._tap(x, y)
            time.sleep(0.5)
        
        ShizukuAPI.keyevent(123)
        time.sleep(0.3)
        ShizukuAPI.keyevent(112)
        time.sleep(0.3)
        return ShizukuAPI.text(text)
    
    def _change_ip(self):
        """Change IP using proxy rotation"""
        proxy = self.proxy_manager.get_next_proxy()
        if proxy:
            print(f"{Color.CYAN}[*] Using proxy: {proxy}{Color.RESET}")
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            return proxy
        
        print(f"{Color.CYAN}[*] Toggling WiFi for new IP...{Color.RESET}")
        ShizukuAPI.toggle_wifi(False)
        time.sleep(2)
        ShizukuAPI.toggle_wifi(True)
        time.sleep(3)
        
        new_ip = ShizukuAPI.get_ip()
        print(f"{Color.CYAN}[*] New IP: {new_ip}{Color.RESET}")
        return new_ip
    
    def _prepare_new_device(self):
        """Prepare new device (clear data + new ID + new IP)"""
        print(f"{Color.CYAN}[*] Preparing new device...{Color.RESET}")
        
        ShizukuAPI.close_app(self.FACEBOOK_PACKAGE)
        ShizukuAPI.close_app(self.FACEBOOK_LITE_PACKAGE)
        time.sleep(2)
        
        DeviceSpoofer.reset_app(self.FACEBOOK_PACKAGE)
        DeviceSpoofer.reset_app(self.FACEBOOK_LITE_PACKAGE)
        time.sleep(2)
        
        new_id = DeviceSpoofer.spoof_device()
        self._change_ip()
        return new_id
    
    def open_facebook(self):
        print(f"{Color.CYAN}[*] Opening Facebook...{Color.RESET}")
        
        ShizukuAPI.open_app(self.FACEBOOK_PACKAGE)
        time.sleep(3)
        
        if ShizukuAPI.wait_for_app(self.FACEBOOK_PACKAGE, 5):
            print(f"{Color.GREEN}[+] Facebook opened{Color.RESET}")
            return True
        
        ShizukuAPI.open_app(self.FACEBOOK_LITE_PACKAGE)
        time.sleep(3)
        
        if ShizukuAPI.wait_for_app(self.FACEBOOK_LITE_PACKAGE, 5):
            print(f"{Color.GREEN}[+] Facebook Lite opened{Color.RESET}")
            return True
        
        print(f"{Color.RED}[-] Could not open Facebook{Color.RESET}")
        return False
    
    def close_facebook(self):
        ShizukuAPI.close_app(self.FACEBOOK_PACKAGE)
        ShizukuAPI.close_app(self.FACEBOOK_LITE_PACKAGE)
        time.sleep(1)
    
    def click_create_account(self):
        print(f"{Color.CYAN}[*] Clicking Create Account...{Color.RESET}")
        x, y = self.coords["create_account_button"]
        self._tap(x, y)
        time.sleep(2)
        return True
    
    def enter_phone_number(self, phone_number):
        print(f"{Color.CYAN}[*] Entering phone: {phone_number}{Color.RESET}")
        x, y = self.coords["email_phone_field"]
        self._type_text(phone_number, (x, y))
        time.sleep(1)
        return True
    
    def click_continue(self):
        print(f"{Color.CYAN}[*] Clicking Continue...{Color.RESET}")
        x, y = self.coords["continue_button"]
        self._tap(x, y)
        time.sleep(3)
        return True
    
    def fill_name(self, first_name, last_name):
        print(f"{Color.CYAN}[*] Filling name: {first_name} {last_name}{Color.RESET}")
        
        x, y = self.coords["name_first"]
        self._type_text(first_name, (x, y))
        time.sleep(0.5)
        
        x, y = self.coords["name_last"]
        self._type_text(last_name, (x, y))
        time.sleep(0.5)
        return True
    
    def select_birthday(self, month=1, day=1, year=2000):
        print(f"{Color.CYAN}[*] Birthday: {month}/{day}/{year}{Color.RESET}")
        
        x, y = self.coords["birthday_month"]
        self._tap(x, y)
        time.sleep(0.5)
        for _ in range(month):
            ShizukuAPI.keyevent(20)
            time.sleep(0.1)
        ShizukuAPI.keyevent(66)
        time.sleep(0.5)
        
        x, y = self.coords["birthday_day"]
        self._tap(x, y)
        time.sleep(0.5)
        for _ in range(day):
            ShizukuAPI.keyevent(20)
            time.sleep(0.1)
        ShizukuAPI.keyevent(66)
        time.sleep(0.5)
        
        x, y = self.coords["birthday_year"]
        self._tap(x, y)
        time.sleep(0.5)
        for _ in range(year - 2000 + 1):
            ShizukuAPI.keyevent(20)
            time.sleep(0.05)
        ShizukuAPI.keyevent(66)
        time.sleep(0.5)
        return True
    
    def select_gender(self, gender='male'):
        print(f"{Color.CYAN}[*] Gender: {gender}{Color.RESET}")
        if gender.lower() == 'male':
            x, y = self.coords["gender_male"]
        else:
            x, y = self.coords["gender_female"]
        self._tap(x, y)
        time.sleep(1)
        return True
    
    def click_sign_up(self):
        print(f"{Color.CYAN}[*] Clicking Sign Up...{Color.RESET}")
        x, y = self.coords["sign_up_button"]
        self._tap(x, y)
        time.sleep(3)
        return True
    
    def click_resend_otp(self):
        print(f"{Color.CYAN}[*] Clicking Resend OTP...{Color.RESET}")
        x, y = self.coords["resend_otp"]
        self._tap(x, y)
        time.sleep(3)
        return True
    
    def automate_account_creation(self, phone_number, first_name="John", last_name="Doe", 
                                   gender="male", month=1, day=1, year=2000):
        """Complete account creation automation (OTP Entry removed)"""
        
        print(f"\n{Color.GOLD}{'='*60}{Color.RESET}")
        print(f"{Color.GOLD}▶ STARTING: {phone_number}{Color.RESET}")
        print(f"{Color.GOLD}{'='*60}{Color.RESET}\n")
        
        try:
            # 1. Prepare new device
            self._prepare_new_device()
            
            # 2. Open Facebook
            if not self.open_facebook():
                return False
            
            # 3. Click Create Account
            self.click_create_account()
            
            # 4. Enter phone number
            self.enter_phone_number(phone_number)
            
            # 5. Click Continue (sends OTP)
            self.click_continue()
            
            # 6. Wait for OTP screen
            time.sleep(random.randint(5, 8))
            
            # 7. Resend OTP 3 times (only send, no entry)
            for attempt in range(3):
                print(f"{Color.CYAN}[*] OTP attempt {attempt + 1}/3 (Resend only){Color.RESET}")
                self.click_resend_otp()
                time.sleep(random.randint(3, 5))
            
            print(f"{Color.GREEN}[+] OTP sent {3} times!{Color.RESET}")
            
            # 8. Fill name
            self.fill_name(first_name, last_name)
            
            # 9. Select birthday
            self.select_birthday(month, day, year)
            
            # 10. Select gender
            self.select_gender(gender)
            
            # 11. Click Sign Up
            self.click_sign_up()
            
            print(f"{Color.GREEN}[+] Account created successfully!{Color.RESET}")
            return True
            
        except Exception as e:
            print(f"{Color.RED}[-] Automation error: {e}{Color.RESET}")
            return False
        finally:
            self.close_facebook()

# ==================== ADB MANAGER ====================

class ADBManager:
    @staticmethod
    def check_adb():
        try:
            subprocess.run(['adb', 'version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    @staticmethod
    def start_server():
        try:
            subprocess.run(['adb', 'start-server'], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    @staticmethod
    def get_devices():
        try:
            result = subprocess.check_output(['adb', 'devices']).decode()
            return [l.split('\t')[0] for l in result.split('\n')[1:] if '\tdevice' in l]
        except:
            return []
    
    @staticmethod
    def connect_wifi(ip, port=5555):
        try:
            result = subprocess.run(['adb', 'connect', f'{ip}:{port}'], capture_output=True, text=True)
            if 'connected' in result.stdout.lower() or 'already' in result.stdout.lower():
                return True, result.stdout.strip()
            return False, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def disconnect_all():
        try:
            subprocess.run(['adb', 'disconnect'], capture_output=True)
            return True
        except:
            return False
    
    @staticmethod
    def get_device_id(serial=''):
        try:
            if serial:
                cmd = ['adb', '-s', serial, 'shell', 'settings', 'get', 'secure', 'android_id']
            else:
                cmd = ['adb', 'shell', 'settings', 'get', 'secure', 'android_id']
            result = subprocess.check_output(cmd, timeout=5).decode().strip()
            if result and result != 'null':
                return result
        except:
            pass
        return 'Unknown'

# ==================== LICENSE MANAGER ====================

class LicenseManager:
    def __init__(self):
        self.config = load_json(CONFIG_FILE)
    
    def save(self): save_json(CONFIG_FILE, self.config)
    def get_license_key(self): return self.config.get('license_key', '')
    def set_license_key(self, key): self.config['license_key'] = key; self.save()
    def get_device_serial(self): return self.config.get('device_serial', '')
    def set_device_serial(self, s): self.config['device_serial'] = s; self.save()
    
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
        print('    +--------------------------------------+')
        print('    |     Thank you for using Ridol FB Tool    |')
        print(f'    |     {Color.YELLOW}Stay Secure!{Color.CYAN}                      |')
        print('    +--------------------------------------+')
        print(f'{Color.RESET}')
        for i in range(3):
            print(f'\r{Color.DIM}Shutting down{"." * (i+1)}{" " * (3-i)}{Color.RESET}', end='', flush=True)
            time.sleep(0.5)
        print()

# ==================== MAIN MENU ====================

class MainMenu:
    def __init__(self):
        self.adb = ADBManager()
        self.license = LicenseManager()
        self.audio = AudioEngine()
        self.automation = FacebookAutomation()
        self.config = load_json(CONFIG_FILE)
        self.data_dir = self.config.get('data_dir', '/storage/emulated/0/Download/Ridol FB Tool')
    
    def show_header(self):
        clear_screen()
        TitleAnimation.big_3d_title()
        devices = self.adb.get_devices()
        print(f' {Color.GREEN}*{Color.RESET} Device: {Color.WHITE}{"connected" if devices else "No device"}{Color.RESET}')
        lic_key = self.license.get_license_key()
        print(f' {Color.GREEN}*{Color.RESET} License: {Color.DIM}{"Active" if lic_key else "No License"}{Color.RESET}')
        
        shizuku_running = ShizukuAPI.check_shizuku()
        status_color = Color.GREEN if shizuku_running else Color.RED
        status_text = "RUNNING" if shizuku_running else "STOPPED"
        print(f' {Color.CYAN}🤖{Color.RESET} Shizuku: {status_color}{status_text}{Color.RESET}\n')
    
    def welcome_screen(self):
        clear_screen()
        TitleAnimation.big_3d_title()
        self.audio.play_startup()
        self.audio.play_background()
        threading.Thread(target=self.audio.speak_welcome, daemon=True).start()
        time.sleep(1)
        clear_screen()
        TitleAnimation.big_3d_title()
        time.sleep(0.5)
    
    def menu_main(self):
        self.welcome_screen()
        while True:
            self.show_header()
            print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}MAIN MENU{Color.RESET}{Color.CYAN}                              |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Device Management              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[2]{Color.RESET} License Management              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Data Folder                     {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Start Automation                {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Status                           {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[6]{Color.RESET} Audio Settings                    {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[7]{Color.RESET} Shizuku Control                  {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[8]{Color.RESET} Demo                             {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[9]{Color.RESET} Help                              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1': self.menu_device()
            elif choice == '2': self.menu_license()
            elif choice == '3': self.menu_folder()
            elif choice == '4': self.menu_start_bot()
            elif choice == '5': self.menu_status()
            elif choice == '6': self.menu_audio()
            elif choice == '7': self.menu_shizuku()
            elif choice == '8': self.menu_demo()
            elif choice == '9': self.menu_help()
            elif choice == '0': self.menu_exit(); break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_device(self):
        while True:
            self.show_header()
            print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}DEVICE MANAGEMENT{Color.RESET}{Color.CYAN}                     |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Check ADB Status                {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[2]{Color.RESET} List Connected Devices           {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Connect WiFi Device              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Disconnect All                   {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Get Device ID                    {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                print(f'\n  {Color.GREEN}[+] ADB: {"Available" if self.adb.check_adb() else "Not found"}{Color.RESET}')
                press_enter()
            elif choice == '2':
                devices = self.adb.get_devices()
                if devices:
                    print(f'\n  {Color.GREEN}[+] Devices found:{Color.RESET}')
                    for d in devices: print(f'    - {d}')
                else:
                    print(f'\n  {Color.RED}[-] No devices connected{Color.RESET}')
                press_enter()
            elif choice == '3':
                ip = input(f'  {Color.CYAN}Enter device IP: {Color.RESET}').strip()
                if ip:
                    success, msg = self.adb.connect_wifi(ip)
                    if success:
                        print(f'  {Color.GREEN}[+] {msg}{Color.RESET}')
                        self.audio.speak_device_connected()
                    else:
                        print(f'  {Color.RED}[-] {msg}{Color.RESET}')
                press_enter()
            elif choice == '4':
                if self.adb.disconnect_all():
                    print(f'  {Color.GREEN}[+] All disconnected{Color.RESET}')
                else:
                    print(f'  {Color.RED}[-] Failed to disconnect{Color.RESET}')
                press_enter()
            elif choice == '5':
                serial = input(f'  {Color.CYAN}Enter device serial (or blank for default): {Color.RESET}').strip()
                device_id = self.adb.get_device_id(serial)
                print(f'  {Color.GREEN}[+] Device ID: {device_id}{Color.RESET}')
                press_enter()
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_license(self):
        while True:
            self.show_header()
            print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}LICENSE MANAGEMENT{Color.RESET}{Color.CYAN}                     |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[1]{Color.RESET} View Current License             {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Enter New License Key            {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Verify License (Server)          {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Register Device (Server)         {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Check Server Status              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
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
            print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}DATA FOLDER{Color.RESET}{Color.CYAN}                             |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Current Path: {Color.DIM}{self.data_dir}{Color.RESET}        {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Set New Path                   {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Create Required Files          {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} View File Contents             {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                print(f'\n  {Color.CYAN}Current Data Directory:{Color.RESET}')
                print(f'  {Color.DIM}{self.data_dir}{Color.RESET}')
                press_enter()
            elif choice == '2':
                new_path = input(f'  {Color.CYAN}Enter new data directory path: {Color.RESET}').strip()
                if new_path:
                    self.data_dir = new_path
                    self.config['data_dir'] = new_path
                    save_json(CONFIG_FILE, self.config)
                    print(f'  {Color.GREEN}[+] Data directory updated{Color.RESET}')
                press_enter()
            elif choice == '3':
                os.makedirs(self.data_dir, exist_ok=True)
                for fname in ['numbers.txt', 'names.txt', 'proxies.txt']:
                    fpath = os.path.join(self.data_dir, fname)
                    if not os.path.exists(fpath):
                        with open(fpath, 'w') as f:
                            f.write(f'# {fname} - Add your data here\n')
                print(f'  {Color.GREEN}[+] Required files created in {self.data_dir}{Color.RESET}')
                press_enter()
            elif choice == '4':
                files = ['numbers.txt', 'names.txt', 'proxies.txt']
                for fname in files:
                    fpath = os.path.join(self.data_dir, fname)
                    if os.path.exists(fpath):
                        print(f'\n  {Color.CYAN}--- {fname} ---{Color.RESET}')
                        with open(fpath, 'r') as f:
                            lines = f.readlines()[:10]
                            for line in lines:
                                print(f'    {line.strip()}')
                        if len(open(fpath).readlines()) > 10:
                            print(f'    {Color.DIM}... and more{Color.RESET}')
                press_enter()
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_start_bot(self):
        self.show_header()
        print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}START AUTOMATION{Color.RESET}{Color.CYAN}                      |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  Numbers: {len(load_file_lines(os.path.join(self.data_dir, "numbers.txt")))}                      {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  License: {Color.DIM}{self.license.get_license_key() or "Not set"}{Color.RESET}{Color.CYAN}           |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  Device: {Color.DIM}{self.license.get_device_serial() or "Not set"}{Color.RESET}{Color.CYAN}          |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  Shizuku: {Color.DIM}{"Running" if ShizukuAPI.check_shizuku() else "Stopped"}{Color.RESET}{Color.CYAN}   |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
        
        if not self.license.get_license_key():
            print(f'\n{Color.RED}[-] No license key set!{Color.RESET}')
            press_enter()
            return
        
        if not ShizukuAPI.check_shizuku():
            print(f'\n{Color.RED}[-] Shizuku not running! Start from Option 7{Color.RESET}')
            press_enter()
            return
        
        numbers = load_file_lines(os.path.join(self.data_dir, "numbers.txt"))
        if not numbers:
            print(f'\n{Color.RED}[-] No numbers found in numbers.txt{Color.RESET}')
            press_enter()
            return
        
        print(f'\n{Color.CYAN}Total numbers: {len(numbers)}{Color.RESET}')
        print(f'{Color.YELLOW}[!] Facebook must be installed{Color.RESET}')
        
        delay = input(f'\n {Color.CYAN}Delay between attempts [5-30, default 15]: {Color.RESET}').strip()
        try:
            delay = int(delay) if delay else 15
            delay = max(5, min(30, delay))
        except:
            delay = 15
        
        print(f'\n{Color.YELLOW}[!] Press Ctrl+C to stop anytime{Color.RESET}')
        press_enter()
        
        self.run_automation(delay)
        press_enter()
    
    def run_automation(self, delay=15):
        numbers = load_file_lines(os.path.join(self.data_dir, "numbers.txt"))
        names = load_file_lines(os.path.join(self.data_dir, "names.txt"))
        
        if not names:
            names = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "James", "Lisa"]
        
        print(f'\n{Color.GREEN}[+] Starting automation with delay: {delay}s{Color.RESET}\n')
        
        for idx, number in enumerate(numbers):
            print(f'{Color.CYAN}[{idx+1}/{len(numbers)}]{Color.RESET} Processing: {number}')
            
            first_name = random.choice(names)
            last_name = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis"])
            gender = random.choice(['male', 'female'])
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            year = random.randint(1980, 2005)
            
            success = self.automation.automate_account_creation(
                phone_number=number,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                month=month,
                day=day,
                year=year
            )
            
            if success:
                print(f'  {Color.GREEN}+ Success: {number}{Color.RESET}')
                self.audio.play_success()
                self.audio.speak_account_created()
            else:
                print(f'  {Color.RED}- Failed: {number}{Color.RESET}')
                self.audio.play_fail()
                self.audio.speak_otp_fail()
            
            if idx < len(numbers) - 1:
                wait_time = random.randint(delay-5, delay+5)
                print(f'  {Color.DIM}Waiting {wait_time}s...{Color.RESET}')
                for i in range(wait_time):
                    time.sleep(1)
                    if i % 5 == 0 and i > 0:
                        print(f'  {Color.DIM}   ... {wait_time - i}s remaining{Color.RESET}')
        
        print(f'\n{Color.GREEN}[+] ALL TASKS COMPLETE!{Color.RESET}')
        self.audio.play_done()
        self.audio.speak_bot_complete()
    
    def menu_shizuku(self):
        while True:
            self.show_header()
            print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}SHIZUKU CONTROL{Color.RESET}{Color.CYAN}                          |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Check Shizuku Status            {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Start Shizuku Server             {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Get Screen Size                  {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Get Current App                  {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Test Tap                        {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[6]{Color.RESET} Test Facebook Open               {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[7]{Color.RESET} Get Device ID                   {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                running = ShizukuAPI.check_shizuku()
                print(f'\n  {Color.GREEN}[+] Shizuku: {"RUNNING" if running else "STOPPED"}{Color.RESET}')
                press_enter()
            elif choice == '2':
                if ShizukuAPI.start_shizuku():
                    print(f'\n  {Color.GREEN}[+] Shizuku started!{Color.RESET}')
                else:
                    print(f'\n  {Color.RED}[-] Failed to start Shizuku{Color.RESET}')
                press_enter()
            elif choice == '3':
                size = ShizukuAPI.get_screen_size()
                print(f'\n  {Color.CYAN}Screen Size: {size}{Color.RESET}')
                press_enter()
            elif choice == '4':
                app = ShizukuAPI.get_current_app()
                print(f'\n  {Color.CYAN}Current App: {app}{Color.RESET}')
                press_enter()
            elif choice == '5':
                print(f'\n  {Color.CYAN}Testing tap...{Color.RESET}')
                size = ShizukuAPI.get_screen_size()
                if size:
                    try:
                        w, h = size.split('x')
                        ShizukuAPI.tap(int(w)//2, int(h)//2)
                        print(f'  {Color.GREEN}[+] Tap sent to ({int(w)//2}, {int(h)//2}){Color.RESET}')
                    except:
                        print(f'  {Color.RED}[-] Failed{Color.RESET}')
                press_enter()
            elif choice == '6':
                print(f'\n  {Color.CYAN}Opening Facebook...{Color.RESET}')
                ShizukuAPI.open_app("com.facebook.katana")
                time.sleep(2)
                app = ShizukuAPI.get_current_app()
                print(f'  {Color.GREEN}[+] Current app: {app}{Color.RESET}')
                press_enter()
            elif choice == '7':
                device_id = ShizukuAPI.get_device_id()
                print(f'\n  {Color.CYAN}Device ID: {device_id}{Color.RESET}')
                press_enter()
            elif choice == '0': break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_status(self):
        self.show_header()
        print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}SYSTEM STATUS{Color.RESET}{Color.CYAN}                           |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
        print(f''' {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} ADB: {Color.WHITE}{"Available" if self.adb.check_adb() else "Not found"}{Color.RESET}{Color.CYAN}             |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} Devices: {Color.WHITE}{len(self.adb.get_devices())}{Color.RESET}{Color.CYAN}                          |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} License: {Color.WHITE}{"Active" if self.license.get_license_key() else "None"}{Color.RESET}{Color.CYAN}                |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} Shizuku: {Color.WHITE}{"Running" if ShizukuAPI.check_shizuku() else "Stopped"}{Color.RESET}{Color.CYAN}         |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} Data Dir: {Color.WHITE}{self.data_dir}{Color.RESET}{Color.CYAN}            |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {self.audio.get_status()}{Color.CYAN}       |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
        
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
        
        press_enter()
    
    def menu_audio(self):
        while True:
            self.show_header()
            print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}AUDIO SETTINGS{Color.RESET}{Color.CYAN}                          |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Test Sound Effects              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Test Voice Feedback             {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Toggle Background Audio         {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Audio Status                    {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Re-download Sounds              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
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
                self.audio.speak('This is a voice test', 'high')
                print(f'  {Color.GREEN}[+] Voice test done{Color.RESET}')
                press_enter()
            elif choice == '3':
                if self.audio.bg_playing:
                    self.audio.stop_background_sound()
                    print(f'  {Color.YELLOW}[!] Background stopped{Color.RESET}')
                else:
                    self.audio.play_background()
                    print(f'  {Color.GREEN}[+] Background started{Color.RESET}')
                press_enter()
            elif choice == '4':
                print(f'\n{self.audio.get_status()}')
                press_enter()
            elif choice == '5':
                print(f'\n  {Color.CYAN}Re-downloading sounds...{Color.RESET}')
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
        print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}DEMO{Color.RESET}{Color.CYAN}                                    |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Matrix Rain Animation            {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Sound Effects Demo              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Voice Messages Demo             {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Progress Bar Demo               {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Typing Effect Demo              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
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
            Animation.typing('Typing effect demo!', 0.05, Color.GOLD)
            press_enter()
        elif choice == '0': pass
        else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_help(self):
        self.show_header()
        print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}HELP{Color.RESET}{Color.CYAN}                                   |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  [?] {Color.WHITE}How to Use{Color.RESET}{Color.CYAN}                       |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  1. Setup data folder (Option 3)                 {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  2. Add phone numbers to numbers.txt             {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  3. Enter license key (Option 2)                 {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  4. Start Shizuku (Option 7 → Option 2)          {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  5. Start Automation (Option 4)                  {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  [#] {Color.WHITE}Shizuku Setup{Color.RESET}{Color.CYAN}                    |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  1. Install Shizuku from Play Store              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  2. Enable USB Debugging                        {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  3. Run: adb shell sh /sdcard/Android/data/    {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}     moe.shizuku.privileged.api/start.sh        {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  4. Open Shizuku app and click Start            {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  5. Return to tool and start automation        {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  🔗 Server: {Color.DIM}{LICENSE_SERVER}{Color.RESET}{Color.CYAN}  |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
        press_enter()
    
    def menu_exit(self):
        self.audio.stop_background_sound()
        Animation.ending_animation()
        threading.Thread(target=self.audio.speak_goodbye, daemon=True).start()
        time.sleep(1)
        print(f'\n{Color.GREEN}Goodbye!{Color.RESET}')
        sys.exit(0)

# ==================== MAIN ====================
if __name__ == '__main__':
    try:
        print(f'{Color.CYAN}[*] Initializing Shizuku Automation...{Color.RESET}')
        
        if ShizukuAPI.check_shizuku():
            print(f'{Color.GREEN}[+] Shizuku is running!{Color.RESET}')
        else:
            print(f'{Color.YELLOW}[!] Shizuku not running. Start from menu.{Color.RESET}')
        
        time.sleep(1)
        
        menu = MainMenu()
        menu.menu_main()
    except KeyboardInterrupt:
        print(f'\n\n{Color.YELLOW}[!] Interrupted by user{Color.RESET}')
        sys.exit(0)
    except Exception as e:
        print(f'\n{Color.RED}[-] Error: {e}{Color.RESET}')
        sys.exit(1)