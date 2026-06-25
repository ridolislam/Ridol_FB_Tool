#!/usr/bin/env python3
"""
Ridol FB Tool v4.0 - Complete Audio Experience Edition
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

# ==================== API CONNECTION MANAGER ====================
class APIManager:
    BASE_URL = LICENSE_SERVER
    API_VERSION = 'v1'
    
    @classmethod
    def get_endpoint(cls, path):
        return f'{cls.BASE_URL}/api/{cls.API_VERSION}/{path}'
    
    @classmethod
    def test_connection(cls):
        try:
            print(f'{Color.CYAN}[*] Testing API connection...{Color.RESET}')
            response = requests.get(cls.get_endpoint('ping'), timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f'{Color.GREEN}[+] API Server reachable! Version: {data.get("version", "unknown")}{Color.RESET}')
                return True, data
            else:
                print(f'{Color.RED}[-] API Server returned: {response.status_code}{Color.RESET}')
                return False, None
        except requests.exceptions.ConnectionError:
            print(f'{Color.RED}[-] Cannot connect to API server!{Color.RESET}')
            return False, None
        except requests.exceptions.Timeout:
            print(f'{Color.RED}[-] API connection timeout!{Color.RESET}')
            return False, None
        except Exception as e:
            print(f'{Color.RED}[-] API Error: {e}{Color.RESET}')
            return False, None
    
    @classmethod
    def get_server_status(cls):
        try:
            response = requests.get(cls.get_endpoint('status'), timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    @classmethod
    def verify_license(cls, license_key, device_serial=''):
        try:
            response = requests.post(
                cls.get_endpoint('license/verify'),
                json={'license_key': license_key, 'device_serial': device_serial},
                timeout=15
            )
            if response.status_code == 200:
                return response.json()
            return {'valid': False, 'message': 'Server error'}
        except:
            return {'valid': False, 'message': 'Connection failed'}
    
    @classmethod
    def check_sound_status(cls):
        try:
            response = requests.get(cls.get_endpoint('sound/status'), timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    @classmethod
    def download_sound(cls):
        try:
            status = cls.check_sound_status()
            if not status or not status.get('exists'):
                print(f'{Color.YELLOW}[!] No custom sound on server{Color.RESET}')
                return None
            
            print(f'{Color.CYAN}[*] Downloading sound from server...{Color.RESET}')
            
            # Try to download as MP3 first
            download_url = cls.get_endpoint('sound/download')
            response = requests.get(download_url, stream=True, timeout=30)
            
            if response.status_code != 200:
                print(f'{Color.RED}[-] Download failed: {response.status_code}{Color.RESET}')
                return None
            
            # Check content type to determine file extension
            content_type = response.headers.get('content-type', '')
            extension = '.mp3' if 'mp3' in content_type else '.wav'
            
            # Also check if URL ends with .mp3 or .wav
            if 'mp3' in download_url.lower():
                extension = '.mp3'
            elif 'wav' in download_url.lower():
                extension = '.wav'
            
            filepath = os.path.join(CUSTOM_SOUND_DIR, f'background{extension}')
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = int((downloaded / total_size) * 100)
                        print(f'\r{Color.CYAN}[*] Downloading: {progress}%{Color.RESET}', end='', flush=True)
            
            print(f'\n{Color.GREEN}[+] Sound downloaded successfully! ({extension}){Color.RESET}')
            return filepath
            
        except Exception as e:
            print(f'{Color.RED}[-] Download error: {e}{Color.RESET}')
            return None
    
    @classmethod
    def register_device(cls, device_serial, license_key=''):
        try:
            response = requests.post(
                cls.get_endpoint('device/register'),
                json={'device_serial': device_serial, 'license_key': license_key},
                timeout=15
            )
            if response.status_code == 200:
                return response.json()
            return {'success': False, 'message': 'Server error'}
        except:
            return {'success': False, 'message': 'Connection failed'}

# ==================== 3D TITLE ====================
class TitleAnimation:
    @staticmethod
    def big_3d_title():
        os.system('clear')
        
        border_top = f"{Color.CYAN}+{'-' * 70}+{Color.RESET}"
        border_bottom = f"{Color.CYAN}+{'-' * 70}+{Color.RESET}"
        
        print(border_top)
        print(f"{Color.CYAN}|{Color.RESET}{' ' * 70}{Color.CYAN}|{Color.RESET}")
        
        title_line1 = f"{Color.CYAN}|{Color.RESET}  {Color.GOLD}*{Color.RESET}  {Color.WHITE}{Color.BOLD}RIDOL FB TOOL{Color.RESET}  {Color.DIM}v4.0{Color.RESET}  {Color.GOLD}*{Color.RESET}  {Color.DIM}Termux Edition{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(title_line1)
        
        subtitle = f"{Color.CYAN}|{Color.RESET}  {Color.DIM}Complete Audio Experience{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(subtitle)
        
        print(f"{Color.CYAN}|{Color.RESET}{' ' * 70}{Color.CYAN}|{Color.RESET}")
        
        connected, _ = APIManager.test_connection()
        status_text = "API CONNECTED" if connected else "API OFFLINE"
        status_color = Color.GREEN if connected else Color.RED
        
        status_line = f"{Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} Device: {Color.WHITE}No device{Color.RESET}  {Color.GREEN}*{Color.RESET} License: {Color.YELLOW}No License{Color.RESET}  {status_color}Server: {status_text}{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(status_line)
        
        server_line = f"{Color.CYAN}|{Color.RESET}  {Color.CYAN}@ {Color.RESET}API URL: {Color.DIM}{APIManager.BASE_URL}/api/v1{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(server_line)
        
        print(border_bottom)
        print()
        time.sleep(0.5)

# ==================== AUDIO ENGINE (MP3 SUPPORT) ====================
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
    
    def _check_voice(self):
        try:
            subprocess.run(['espeak', '--help'], capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def _check_sound(self):
        # First check for mpv (supports MP3)
        try:
            subprocess.run(['mpv', '--version'], capture_output=True, timeout=2)
            return True
        except:
            pass
        
        # Fallback to sox (WAV only)
        try:
            subprocess.run(['play', '--help', '-q'], capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def play_sound(self, filename, gain='-5'):
        """Play a sound file (supports MP3, WAV, OGG via mpv)"""
        if not self.sound_available:
            return
        
        # Check multiple locations
        filepath = os.path.join(self.sound_dir, filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(self.custom_sound_dir, filename)
            if not os.path.exists(filepath):
                return
        
        # Try mpv first (supports MP3, WAV, OGG)
        try:
            subprocess.Popen(['mpv', '--no-video', '--really-quiet', '--volume=80', filepath],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except:
            pass
        
        # Fallback to play (WAV only)
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
    
    def download_background_sound(self):
        return APIManager.download_sound()
    
    def play_background_loop(self):
        if not self.sound_available:
            return
        
        # Try to download from server first
        custom_bg = os.path.join(self.custom_sound_dir, 'background.wav')
        custom_mp3 = os.path.join(self.custom_sound_dir, 'background.mp3')
        
        if not os.path.exists(custom_bg) and not os.path.exists(custom_mp3):
            self.download_background_sound()
            # Re-check after download
            custom_bg = os.path.join(self.custom_sound_dir, 'background.wav')
            custom_mp3 = os.path.join(self.custom_sound_dir, 'background.mp3')
        
        # Choose which file to play
        if os.path.exists(custom_mp3):
            bg_file = custom_mp3
            print(f'{Color.GREEN}[+] Playing custom MP3 sound{Color.RESET}')
        elif os.path.exists(custom_bg):
            bg_file = custom_bg
            print(f'{Color.GREEN}[+] Playing custom WAV sound{Color.RESET}')
        else:
            bg_file = os.path.join(self.sound_dir, 'binary_rain.wav')
            if not os.path.exists(bg_file):
                return
            print(f'{Color.DIM}[*] Playing default sound{Color.RESET}')
        
        self.background_file = bg_file
        self.bg_playing = True
        
        # Use mpv for background (supports MP3 and WAV)
        while self.bg_playing:
            try:
                subprocess.run(['mpv', '--no-video', '--really-quiet', '--volume=70', '--loop=inf', bg_file],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            except:
                # Fallback to play (WAV only)
                try:
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

# ==================== REST OF THE CODE ====================
# [ADBManager, LicenseManager, FacebookBot, Animation, MainMenu - same as before]

# ==================== MAIN ====================
if __name__ == '__main__':
    try:
        # Check for mpv
        try:
            subprocess.run(['mpv', '--version'], capture_output=True, check=True)
            print(f'{Color.GREEN}[+] mpv found - MP3 support enabled{Color.RESET}')
        except:
            print(f'{Color.YELLOW}[!] mpv not found - install: pkg install mpv{Color.RESET}')
            print(f'{Color.YELLOW}[!] Only WAV files will play{Color.RESET}')
        
        print(f'{Color.CYAN}[*] Initializing API Connection...{Color.RESET}')
        connected, _ = APIManager.test_connection()
        
        if connected:
            status = APIManager.get_server_status()
            if status:
                print(f'{Color.GREEN}[+] Server Status: {status.get("version")}{Color.RESET}')
                print(f'{Color.GREEN}[+] Licenses: {status.get("license_count", 0)}{Color.RESET}')
                print(f'{Color.GREEN}[+] Sound: {"Available" if status.get("sound_exists") else "Not available"}{Color.RESET}')
        else:
            print(f'{Color.YELLOW}[!] API Server offline. Some features may not work.{Color.RESET}')
        
        time.sleep(1)
        
        menu = MainMenu()
        menu.menu_main()
    except KeyboardInterrupt:
        print(f'\n\n{Color.YELLOW}[!] Interrupted by user{Color.RESET}')
        sys.exit(0)
    except Exception as e:
        print(f'\n{Color.RED}[-] Error: {e}{Color.RESET}')
        sys.exit(1)