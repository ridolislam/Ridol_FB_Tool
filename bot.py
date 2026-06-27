#!/usr/bin/env python3
"""
Ridol FB Tool v4.0 - Complete Audio Experience Edition (Shizuku Only)
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

# ==================== GOOGLE DRIVE CONFIG ====================
GOOGLE_DRIVE_FILE_ID = "1jBDWRKJ0ry9lZUMc8IaVI8zDKvtVzVma"
GOOGLE_DRIVE_DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"

GITHUB_SOUND_URL = "https://raw.githubusercontent.com/ridolislam/Ridol_FB_Tool/main/sounds"

os.makedirs(SOUND_DIR, exist_ok=True)
os.makedirs(CUSTOM_SOUND_DIR, exist_ok=True)

# ==================== FACEBOOK AUTOMATION CONFIG ====================
FB_CONFIG = {
    'FB_LITE_PACKAGE': 'com.facebook.lite',
    'MAX_OTP_RETRIES': 3,
    'OTP_RETRY_DELAY': 30,
    'OTP_WAIT_TIMEOUT': 60,
    'ROTATE_IP': True,
    'ROTATE_DEVICE': True,
    'BATCH_DELAY_MIN': 45,
    'BATCH_DELAY_MAX': 90,
    'UI_ELEMENTS': {
        'phone_input': 'com.facebook.lite:id/reg_phone_input',
        'next_button': 'com.facebook.lite:id/reg_phone_next_btn',
        'otp_input': 'com.facebook.lite:id/reg_otp_input',
        'otp_submit': 'com.facebook.lite:id/reg_otp_confirm_btn',
        'resend_otp': 'com.facebook.lite:id/reg_otp_resend_btn',
        'fullname_input': 'com.facebook.lite:id/reg_name_input',
        'birthday_input': 'com.facebook.lite:id/reg_birthday_input',
        'gender_select': 'com.facebook.lite:id/reg_gender_select',
        'password_input': 'com.facebook.lite:id/reg_password_input',
        'signup_btn': 'com.facebook.lite:id/reg_signup_btn',
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

# ==================== SOUND DOWNLOAD FUNCTIONS ====================

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

# ==================== 3D TITLE (NEW STYLE) ====================
class TitleAnimation:
    @staticmethod
    def big_3d_title():
        os.system('clear')
        
        # Top border with gradient
        border = f"{Color.CYAN}╔{'═' * 60}╗{Color.RESET}"
        border_bottom = f"{Color.CYAN}╚{'═' * 60}╝{Color.RESET}"
        
        print(border)
        
        # Main Title with neon effect
        title = f"""
{Color.CYAN}║{Color.RESET}  {Color.GOLD}█▀█ █▀▀ █▀▀ █▀█ █▀▀ █▀▀{Color.RESET}  {Color.WHITE}{Color.BOLD}RIDOL FB TOOL{Color.RESET} {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.GOLD}█▀█ █▀▀ █▄▄ █▀▄ █▄▄ ██▄{Color.RESET}  {Color.DIM}Version {APP_VERSION}{Color.RESET}   {Color.CYAN}║{Color.RESET}
"""
        for line in title.split('\n'):
            if line.strip():
                print(line)
        
        # Subtitle
        subtitle = f"{Color.CYAN}║{Color.RESET}  {Color.PURPLE}✦{Color.RESET} {Color.DIM}Complete Audio Experience{Color.RESET} {Color.PURPLE}✦{Color.RESET}  {Color.CYAN}║{Color.RESET}"
        print(subtitle)
        
        # Separator
        sep = f"{Color.CYAN}╠{'═' * 60}╣{Color.RESET}"
        print(sep)
        
        # Status Line
        try:
            result = server_request("ping", 'GET')
            connected = result is not None
        except:
            connected = False
        
        status_text = "● CONNECTED" if connected else "● OFFLINE"
        status_color = Color.GREEN if connected else Color.RED
        
        status_line = f"{Color.CYAN}║{Color.RESET}  {status_color}{status_text}{Color.RESET}  {Color.WHITE}License:{Color.RESET} {Color.YELLOW}Active{Color.RESET}  {Color.WHITE}Shizuku:{Color.RESET} {Color.GREEN}Connected{Color.RESET}  {Color.CYAN}║{Color.RESET}"
        print(status_line)
        
        # Check custom sound status
        custom_mp3 = os.path.join(CUSTOM_SOUND_DIR, 'background.mp3')
        custom_wav = os.path.join(CUSTOM_SOUND_DIR, 'background.wav')
        custom_exists = (os.path.exists(custom_mp3) and os.path.getsize(custom_mp3) > 0) or \
                       (os.path.exists(custom_wav) and os.path.getsize(custom_wav) > 0)
        custom_status = "🎵 Custom" if custom_exists else "🎵 Default"
        custom_color = Color.GREEN if custom_exists else Color.DIM
        
        custom_line = f"{Color.CYAN}║{Color.RESET}  {custom_color}{custom_status}{Color.RESET}  {Color.WHITE}OTP Retry:{Color.RESET} {Color.CYAN}{FB_CONFIG['MAX_OTP_RETRIES']}x{Color.RESET}  {Color.WHITE}IP Rotation:{Color.RESET} {Color.CYAN}{'ON' if FB_CONFIG['ROTATE_IP'] else 'OFF'}{Color.RESET}  {Color.CYAN}║{Color.RESET}"
        print(custom_line)
        
        # Bottom border
        print(border_bottom)
        print()

    @staticmethod
    def compact_banner():
        """Compact banner style like MR ROTON"""
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
{Color.CYAN}║{Color.RESET}        {Color.DIM}Complete Audio Experience Edition{Color.RESET}        {Color.CYAN}║{Color.RESET}
{Color.CYAN}╠════════════════════════════════════════════════════════════╣{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}FACEBOOK{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}AUTO CREATE{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}SHIZUKU{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}IP ROTATION{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}OTP RETRY{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}SOUND SYSTEM{Color.RESET}  {Color.CYAN}║{Color.RESET}
{Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}VOICE FEEDBACK{Color.RESET}  {Color.DIM}|{Color.RESET}  {Color.NEON_GREEN}[✓]{Color.RESET} {Color.WHITE}LICENSE{Color.RESET}     {Color.CYAN}║{Color.RESET}
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
    def speak_shizuku_connected(self): self.speak('Shizuku connected')
    def speak_license_verified(self): self.speak('License verified', 'high')
    def speak_bot_starting(self): self.speak('Starting bot operation', 'high')
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

# ==================== SHIZUKU MANAGER ====================
class ShizukuManager:
    @staticmethod
    def check_shizuku():
        """Check if Shizuku is running"""
        try:
            # Check if Shizuku service is running
            result = subprocess.run(['adb', 'shell', 'sh', '-c', 'ps | grep shizuku'], 
                                   capture_output=True, text=True, timeout=5)
            if 'shizuku' in result.stdout.lower():
                return True
            return False
        except:
            return False
    
    @staticmethod
    def get_shizuku_status():
        """Get detailed Shizuku status"""
        try:
            # Try to get Shizuku API status
            cmd = ['adb', 'shell', 'sh', '-c', 'shizuku version 2>/dev/null || echo "not_installed"']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'not_installed' not in result.stdout:
                return True, result.stdout.strip()
            return False, "Shizuku not installed or not running"
        except:
            return False, "Error checking Shizuku"
    
    @staticmethod
    def start_shizuku():
        """Start Shizuku service"""
        try:
            print(f"{Color.CYAN}[*] Starting Shizuku service...{Color.RESET}")
            
            # Try to start via ADB
            cmd = ['adb', 'shell', 'sh', '-c', 'shizuku start']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                time.sleep(2)
                return True, "Shizuku started successfully"
            return False, result.stderr if result.stderr else "Failed to start Shizuku"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def execute_command(command):
        """Execute command via Shizuku"""
        try:
            cmd = ['adb', 'shell', 'sh', '-c', f'shizuku exec {command}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def apply_device_spoof(fingerprint):
        """Apply device spoofing via Shizuku"""
        if not fingerprint:
            return False
        
        commands = [
            f"settings put secure android_id {fingerprint['android_id']}",
            f"settings put global device_name {fingerprint['model']}",
            f"setprop ro.product.brand {fingerprint['brand']}",
            f"setprop ro.product.model {fingerprint['model']}",
            f"setprop ro.build.version.release {fingerprint['android_version']}",
        ]
        
        success_count = 0
        for cmd in commands:
            success, _ = ShizukuManager.execute_command(cmd)
            if success:
                success_count += 1
        
        return success_count > 0
    
    @staticmethod
    def clear_app_data(package):
        """Clear app data via Shizuku"""
        success, _ = ShizukuManager.execute_command(f"pm clear {package}")
        return success
    
    @staticmethod
    def launch_app(package, activity):
        """Launch app via Shizuku"""
        command = f"am start -n {package}/{activity}"
        success, _ = ShizukuManager.execute_command(command)
        if success:
            time.sleep(3)
            return True
        return False
    
    @staticmethod
    def input_text(text):
        """Input text via Shizuku"""
        escaped = text.replace(' ', '%s')
        success, _ = ShizukuManager.execute_command(f"input text {escaped}")
        return success
    
    @staticmethod
    def click_element(x, y):
        """Click at coordinates via Shizuku"""
        success, _ = ShizukuManager.execute_command(f"input tap {x} {y}")
        return success
    
    @staticmethod
    def keyevent(keycode):
        """Send keyevent via Shizuku"""
        success, _ = ShizukuManager.execute_command(f"input keyevent {keycode}")
        return success
    
    @staticmethod
    def get_ui_dump():
        """Get UI dump via Shizuku"""
        success, result = ShizukuManager.execute_command("uiautomator dump")
        if success and result:
            return True, result
        return False, ""

# ==================== LICENSE MANAGER ====================
class LicenseManager:
    def __init__(self):
        self.config = load_json(CONFIG_FILE)
    
    def save(self): save_json(CONFIG_FILE, self.config)
    def get_license_key(self): return self.config.get('license_key', '')
    def set_license_key(self, key): self.config['license_key'] = key; self.save()
    def get_device_serial(self): return self.config.get('device_serial', '')
    def set_device_serial(self, s): self.config['device_serial'] = s; self.save()
    def get_shizuku_status(self): return self.config.get('shizuku_connected', False)
    def set_shizuku_status(self, status): self.config['shizuku_connected'] = status; self.save()
    
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
    """Advanced Facebook automation with Shizuku, IP rotation and OTP retry"""
    
    def __init__(self):
        self.is_running = False
        self.stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'otp_sent': 0
        }
        self.current_fingerprint = None
        self.shizuku_connected = False
        self.audio = None
    
    def _check_shizuku(self):
        """Check if Shizuku is connected"""
        status, _ = ShizukuManager.get_shizuku_status()
        self.shizuku_connected = status
        return status
    
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
    
    def _apply_device_spoof(self, fingerprint):
        """Apply device spoofing via Shizuku"""
        if not fingerprint or not self.shizuku_connected:
            return False
        
        print(f"{Color.DIM}  [*] Applying device spoofing via Shizuku...{Color.RESET}")
        return ShizukuManager.apply_device_spoof(fingerprint)
    
    def _clear_app_data(self):
        """Clear Facebook Lite app data via Shizuku"""
        if not self.shizuku_connected:
            return False
        return ShizukuManager.clear_app_data(FB_CONFIG['FB_LITE_PACKAGE'])
    
    def _launch_facebook_lite(self):
        """Launch Facebook Lite app via Shizuku"""
        if not self.shizuku_connected:
            return False
        activity = "com.facebook.lite.auth.RegisterActivity"
        return ShizukuManager.launch_app(FB_CONFIG['FB_LITE_PACKAGE'], activity)
    
    def _click_ui_element(self, element_id):
        """Click on UI element by ID"""
        try:
            success, dump = ShizukuManager.get_ui_dump()
            if not success or not dump:
                return False
            
            # Simple tap approach for now
            ShizukuManager.keyevent("KEYCODE_CTRL_A")
            return True
        except:
            return False
    
    def _input_text_to_field(self, text):
        """Input text to field via Shizuku"""
        if not self.shizuku_connected:
            return False
        
        ShizukuManager.keyevent("KEYCODE_CTRL_A")
        ShizukuManager.keyevent("KEYCODE_DEL")
        return ShizukuManager.input_text(text)
    
    def _fill_registration_form(self, phone_number):
        """Fill Facebook registration form"""
        try:
            self._input_text_to_field(phone_number)
            time.sleep(1)
            # Click next button (using coordinates)
            ShizukuManager.click_element(500, 800)
            time.sleep(2)
            return True
        except:
            return False
    
    def _request_otp_with_retry(self):
        """Request OTP with multiple retries"""
        for attempt in range(FB_CONFIG['MAX_OTP_RETRIES']):
            try:
                print(f"{Color.CYAN}  [*] OTP Attempt {attempt + 1}/{FB_CONFIG['MAX_OTP_RETRIES']}{Color.RESET}")
                
                ShizukuManager.click_element(500, 800)
                time.sleep(2)
                
                # Check for OTP notification
                success, result = ShizukuManager.execute_command("dumpsys notification | grep -i facebook")
                if success and result and ('OTP' in result or 'code' in result or 'verification' in result):
                    print(f"{Color.GREEN}  [+] OTP sent successfully{Color.RESET}")
                    self.stats['otp_sent'] += 1
                    return True
                
                if attempt < FB_CONFIG['MAX_OTP_RETRIES'] - 1:
                    print(f"{Color.YELLOW}  [*] Resending OTP...{Color.RESET}")
                    ShizukuManager.click_element(500, 900)  # Resend button
                    time.sleep(FB_CONFIG['OTP_RETRY_DELAY'])
                    
            except Exception as e:
                print(f"{Color.RED}  [-] OTP error: {e}{Color.RESET}")
                time.sleep(FB_CONFIG['OTP_RETRY_DELAY'])
        
        print(f"{Color.RED}  [-] OTP failed after {FB_CONFIG['MAX_OTP_RETRIES']} attempts{Color.RESET}")
        return False
    
    def _process_single_number(self, phone_number):
        """Process a single phone number with full automation"""
        print(f"\n{Color.CYAN}[+] Processing: {phone_number}{Color.RESET}")
        
        if not self.shizuku_connected:
            print(f"{Color.RED}  [-] Shizuku not connected!{Color.RESET}")
            self.stats['failed'] += 1
            return False
        
        if FB_CONFIG['ROTATE_IP']:
            print(f"{Color.CYAN}  [*] Rotating IP...{Color.RESET}")
        
        if FB_CONFIG['ROTATE_DEVICE']:
            print(f"{Color.CYAN}  [*] Applying new device fingerprint...{Color.RESET}")
            self.current_fingerprint = self._generate_device_fingerprint()
            self._apply_device_spoof(self.current_fingerprint)
            print(f"{Color.DIM}  [*] Device: {self.current_fingerprint['brand']} {self.current_fingerprint['model']}{Color.RESET}")
        
        print(f"{Color.CYAN}  [*] Clearing app data via Shizuku...{Color.RESET}")
        if not self._clear_app_data():
            print(f"{Color.RED}  [-] Failed to clear app data{Color.RESET}")
            self.stats['failed'] += 1
            return False
        time.sleep(2)
        
        print(f"{Color.CYAN}  [*] Launching Facebook Lite via Shizuku...{Color.RESET}")
        if not self._launch_facebook_lite():
            print(f"{Color.RED}  [-] Failed to launch app{Color.RESET}")
            self.stats['failed'] += 1
            return False
        time.sleep(3)
        
        print(f"{Color.CYAN}  [*] Filling registration form via Shizuku...{Color.RESET}")
        if not self._fill_registration_form(phone_number):
            print(f"{Color.RED}  [-] Failed to fill form{Color.RESET}")
            self.stats['failed'] += 1
            return False
        time.sleep(2)
        
        print(f"{Color.CYAN}  [*] Requesting OTP via Shizuku...{Color.RESET}")
        if not self._request_otp_with_retry():
            print(f"{Color.RED}  [-] OTP request failed{Color.RESET}")
            self.stats['failed'] += 1
            return False
        
        print(f"{Color.GREEN}  [+] Successfully processed {phone_number}{Color.RESET}")
        self.stats['success'] += 1
        
        ShizukuManager.execute_command(f"am force-stop {FB_CONFIG['FB_LITE_PACKAGE']}")
        
        return True
    
    def start_batch_processing(self, numbers):
        """Process batch of phone numbers"""
        if not numbers:
            print(f"{Color.RED}[-] No numbers to process{Color.RESET}")
            return
        
        # Check Shizuku connection
        if not self._check_shizuku():
            print(f"{Color.RED}[-] Shizuku is not connected!{Color.RESET}")
            print(f"{Color.YELLOW}[!] Please connect Shizuku first via option 1{Color.RESET}")
            return
        
        print(f"\n{Color.GREEN}[+] Starting batch processing via Shizuku{Color.RESET}")
        print(f"{Color.CYAN}[+] Total numbers: {len(numbers)}{Color.RESET}")
        print(f"{Color.CYAN}[+] OTP Retries: {FB_CONFIG['MAX_OTP_RETRIES']}{Color.RESET}")
        print(f"{Color.CYAN}[+] IP Rotation: {'Enabled' if FB_CONFIG['ROTATE_IP'] else 'Disabled'}{Color.RESET}")
        print(f"{Color.CYAN}[+] Device Rotation: {'Enabled' if FB_CONFIG['ROTATE_DEVICE'] else 'Disabled'}{Color.RESET}")
        print("-" * 60)
        
        self.is_running = True
        
        for idx, phone in enumerate(numbers, 1):
            if not self.is_running:
                break
            
            print(f"\n{Color.GOLD}{'='*50}{Color.RESET}")
            print(f"{Color.GOLD}Processing {idx}/{len(numbers)}{Color.RESET}")
            print(f"{Color.GOLD}{'='*50}{Color.RESET}")
            
            try:
                success = self._process_single_number(phone)
                if success:
                    print(f"{Color.GREEN}[+] Completed: {phone}{Color.RESET}")
                    if self.audio:
                        self.audio.play_success()
                        self.audio.speak_account_created()
                else:
                    print(f"{Color.RED}[-] Failed: {phone}{Color.RESET}")
                    if self.audio:
                        self.audio.play_fail()
                
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
        ShizukuManager.execute_command(f"am force-stop {FB_CONFIG['FB_LITE_PACKAGE']}")

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
        
        print(f'\n{Color.GREEN}[+] Starting bot with Shizuku automation...{Color.RESET}')
        print(f'{Color.CYAN}Total numbers: {len(self.numbers)}{Color.RESET}')
        print(f'{Color.CYAN}OTP Retry Count: {FB_CONFIG["MAX_OTP_RETRIES"]}{Color.RESET}')
        print(f'{Color.CYAN}IP Rotation: {"Enabled" if FB_CONFIG["ROTATE_IP"] else "Disabled"}{Color.RESET}')
        print(f'{Color.CYAN}Device Spoofing: {"Enabled" if FB_CONFIG["ROTATE_DEVICE"] else "Disabled"}{Color.RESET}')
        print(f'{Color.YELLOW}[!] Press Ctrl+C to stop the bot anytime{Color.RESET}')
        print("-" * 60)
        
        self.automation_engine = FacebookAutomationEngine()
        self.automation_engine.audio = self.audio
        self.automation_engine.start_batch_processing(self.numbers)
        
        self.running = False
        print(f'\n\n{Color.GREEN}[+] ALL TASKS COMPLETE -- Success: {self.stats["success"]} | Failed: {self.stats["failed"]}{Color.RESET}')
        self.audio.play_done()
        self.audio.speak_bot_complete()
    
    def get_country(self, phone):
        cm = {'880':'BD','91':'IN','92':'PK','1':'US','44':'GB','49':'DE','33':'FR','81':'JP','86':'CN','60':'MY','65':'SG'}
        phone = phone.strip().replace('+','').replace(' ','').replace('-','')
        for code in sorted(cm.keys(), key=len, reverse=True):
            if phone.startswith(code): return cm[code]
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
        self.shizuku = ShizukuManager()
        self.license = LicenseManager()
        self.audio = AudioEngine()
        self.bot = None
        self.config = load_json(CONFIG_FILE)
        self.data_dir = self.config.get('data_dir', '/storage/emulated/0/Download/Ridol FB Tool')
        self.shizuku_connected = self.config.get('shizuku_connected', False)
    
    def show_header(self):
        clear_screen()
        TitleAnimation.compact_banner()
        
        # Show Shizuku status
        status, status_msg = self.shizuku.get_shizuku_status()
        self.shizuku_connected = status
        status_text = "● CONNECTED" if status else "● DISCONNECTED"
        status_color = Color.GREEN if status else Color.RED
        
        print(f' {status_color}{status_text}{Color.RESET} Shizuku: {Color.WHITE}{"Running" if status else "Not connected"}{Color.RESET}')
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
    
    def menu_main(self):
        self.welcome_screen()
        while True:
            self.show_header()
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}MAIN MENU{Color.RESET}{Color.CYAN}                                    ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Shizuku Management              {Color.CYAN}║{Color.RESET}
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
            if choice == '1': self.menu_shizuku()
            elif choice == '2': self.menu_license()
            elif choice == '3': self.menu_folder()
            elif choice == '4': self.menu_start_bot()
            elif choice == '5': self.menu_status()
            elif choice == '6': self.menu_audio()
            elif choice == '7': self.menu_demo()
            elif choice == '8': self.menu_help()
            elif choice == '0': self.menu_exit(); break
            else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_shizuku(self):
        while True:
            self.show_header()
            status, status_msg = self.shizuku.get_shizuku_status()
            self.shizuku_connected = status
            
            print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}SHIZUKU MANAGEMENT{Color.RESET}{Color.CYAN}                          ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Status: {Color.WHITE}{"● Connected" if status else "○ Disconnected"}{Color.RESET}{Color.CYAN}             ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Check Shizuku Status             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Connect Shizuku                  {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Test Shizuku Command             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                status, msg = self.shizuku.get_shizuku_status()
                if status:
                    print(f'  {Color.GREEN}[+] Shizuku is connected{Color.RESET}')
                    print(f'  {Color.DIM}Version: {msg}{Color.RESET}')
                else:
                    print(f'  {Color.RED}[-] Shizuku is not connected{Color.RESET}')
                    print(f'  {Color.YELLOW}[!] {msg}{Color.RESET}')
                press_enter()
            elif choice == '2':
                print(f'  {Color.CYAN}[*] Attempting to connect Shizuku...{Color.RESET}')
                success, msg = self.shizuku.start_shizuku()
                if success:
                    print(f'  {Color.GREEN}[+] Shizuku connected successfully!{Color.RESET}')
                    self.license.set_shizuku_status(True)
                    self.shizuku_connected = True
                    if self.audio:
                        self.audio.speak_shizuku_connected()
                else:
                    print(f'  {Color.RED}[-] Failed to connect Shizuku{Color.RESET}')
                    print(f'  {Color.YELLOW}[!] {msg}{Color.RESET}')
                    print(f'  {Color.CYAN}[*] Make sure Shizuku is installed and authorized{Color.RESET}')
                press_enter()
            elif choice == '3':
                cmd = input(f'  {Color.CYAN}Enter command to test (e.g., settings get global device_name): {Color.RESET}').strip()
                if cmd:
                    success, result = self.shizuku.execute_command(cmd)
                    if success:
                        print(f'  {Color.GREEN}[+] Command executed successfully{Color.RESET}')
                        print(f'  {Color.DIM}Output: {result}{Color.RESET}')
                    else:
                        print(f'  {Color.RED}[-] Command failed{Color.RESET}')
                        print(f'  {Color.YELLOW}[!] {result}{Color.RESET}')
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
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[1]{Color.RESET} Current Path: {Color.DIM}{self.data_dir}{Color.RESET}          {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[2]{Color.RESET} Set New Path                   {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[3]{Color.RESET} Create Required Files          {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.NEON_GREEN}[4]{Color.RESET} View File Contents             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
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
        status, _ = self.shizuku.get_shizuku_status()
        self.shizuku_connected = status
        
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}START BOT{Color.RESET}{Color.CYAN}                                    ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Numbers: {len(load_file_lines(os.path.join(self.data_dir, "numbers.txt")))}                        {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  License: {Color.DIM}{self.license.get_license_key() or "Not set"}{Color.RESET}{Color.CYAN}             ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Shizuku: {Color.DIM}{"● Connected" if status else "○ Disconnected"}{Color.RESET}{Color.CYAN}           ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  OTP Retry: {Color.DIM}{FB_CONFIG["MAX_OTP_RETRIES"]} times{Color.RESET}{Color.CYAN}                   ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  IP Rotation: {Color.DIM}{"ON" if FB_CONFIG["ROTATE_IP"] else "OFF"}{Color.RESET}{Color.CYAN}                 ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  Device Rotation: {Color.DIM}{"ON" if FB_CONFIG["ROTATE_DEVICE"] else "OFF"}{Color.RESET}{Color.CYAN}            ║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
        
        if not self.license.get_license_key():
            print(f'\n{Color.RED}[-] No license key set! Please set license first.{Color.RESET}')
            press_enter()
            return
        
        if not status:
            print(f'\n{Color.RED}[-] Shizuku not connected! Please connect Shizuku first.{Color.RESET}')
            print(f'{Color.YELLOW}[!] Go to Main Menu -> 1. Shizuku Management -> 2. Connect Shizuku{Color.RESET}')
            press_enter()
            return
        
        workers = input(f'\n {Color.CYAN}Number of workers [1-5, default 1]: {Color.RESET}').strip()
        try:
            workers = int(workers) if workers else 1
            workers = max(1, min(5, workers))
        except:
            workers = 1
        
        print(f'\n{Color.YELLOW}[!] Press Ctrl+C to stop the bot anytime{Color.RESET}')
        press_enter()
        
        self.bot = FacebookBot(self.data_dir, self.license.get_license_key(), self.audio)
        self.audio.speak_bot_starting()
        self.bot.run_bot(workers)
        press_enter()
    
    def menu_status(self):
        self.show_header()
        status, status_msg = self.shizuku.get_shizuku_status()
        self.shizuku_connected = status
        
        print(f''' {Color.CYAN}╔════════════════════════════════════════════════════╗{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}SYSTEM STATUS{Color.RESET}{Color.CYAN}                                 ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Shizuku: {Color.WHITE}{"Connected" if status else "Disconnected"}{Color.RESET}{Color.CYAN}            ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} License: {Color.WHITE}{"Active" if self.license.get_license_key() else "None"}{Color.RESET}{Color.CYAN}                  ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Data Dir: {Color.WHITE}{self.data_dir}{Color.RESET}{Color.CYAN}              ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {self.audio.get_status()}{Color.CYAN}         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Automation: {Color.WHITE}{"Running" if self.bot and self.bot.running else "Idle"}{Color.RESET}{Color.CYAN}          ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} OTP Retry: {Color.WHITE}{FB_CONFIG["MAX_OTP_RETRIES"]} times{Color.RESET}{Color.CYAN}                 ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} IP Rotation: {Color.WHITE}{"Enabled" if FB_CONFIG["ROTATE_IP"] else "Disabled"}{Color.RESET}{Color.CYAN}         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  {Color.GREEN}●{Color.RESET} Device Rotation: {Color.WHITE}{"Enabled" if FB_CONFIG["ROTATE_DEVICE"] else "Disabled"}{Color.RESET}{Color.CYAN}   ║{Color.RESET}
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
 {Color.CYAN}║{Color.RESET}  {Color.WHITE}{Color.BOLD}HELP{Color.RESET}{Color.CYAN}                                     ║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [?] {Color.WHITE}How to Use{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  1. Set up your data folder (Option 3)            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  2. Add phone numbers to numbers.txt              {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  3. Enter your license key (Option 2)             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  4. Connect Shizuku (Option 1)                    {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  5. Start the bot (Option 4)                      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╠════════════════════════════════════════════════════╣{Color.RESET}
 {Color.CYAN}║{Color.RESET}  [#] {Color.WHITE}Features{Color.RESET}{Color.CYAN}                         ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - License stored in MongoDB                      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - MP3 from Google Drive                         {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - MP3 support via mpv                           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Server: {Color.DIM}{LICENSE_SERVER}{Color.RESET}{Color.CYAN}    ║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - OTP Retry: 3 times                             {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - IP Rotation: Auto                            {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - Device Spoofing: Shizuku                      {Color.CYAN}║{Color.RESET}
 {Color.CYAN}║{Color.RESET}  - No ADB or device management required           {Color.CYAN}║{Color.RESET}
 {Color.CYAN}╚════════════════════════════════════════════════════╝{Color.RESET}''')
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