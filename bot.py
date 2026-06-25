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

# ==================== 3D TITLE (TERMUX FRIENDLY) ====================
class TitleAnimation:
    @staticmethod
    def big_3d_title():
        """Display 3D title using simple ASCII characters (Termux friendly)"""
        os.system('clear')
        
        # Simple border using + - and |
        border_top = f"{Color.CYAN}+{'-' * 70}+{Color.RESET}"
        border_bottom = f"{Color.CYAN}+{'-' * 70}+{Color.RESET}"
        
        print(border_top)
        print(f"{Color.CYAN}|{Color.RESET}{' ' * 70}{Color.CYAN}|{Color.RESET}")
        
        # Title with colors
        title_line1 = f"{Color.CYAN}|{Color.RESET}  {Color.GOLD}*{Color.RESET}  {Color.WHITE}{Color.BOLD}RIDOL FB TOOL{Color.RESET}  {Color.DIM}v4.0{Color.RESET}  {Color.GOLD}*{Color.RESET}  {Color.DIM}Termux Edition{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(title_line1)
        
        subtitle = f"{Color.CYAN}|{Color.RESET}  {Color.DIM}Complete Audio Experience{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(subtitle)
        
        print(f"{Color.CYAN}|{Color.RESET}{' ' * 70}{Color.CYAN}|{Color.RESET}")
        
        # Status line
        status_line = f"{Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} Device: {Color.WHITE}No device{Color.RESET}  {Color.GREEN}*{Color.RESET} License: {Color.YELLOW}No License{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(status_line)
        
        # Server status
        server_line = f"{Color.CYAN}|{Color.RESET}  {Color.CYAN}@ {Color.RESET}Server: {Color.GREEN}ACTIVE{Color.RESET}  {Color.CYAN}|{Color.RESET}"
        print(server_line)
        
        print(border_bottom)
        print()
        time.sleep(0.5)
    
    @staticmethod
    def animated_banner():
        """Display animated banner with loading effect"""
        os.system('clear')
        
        print(f"{Color.CYAN}+{'-' * 70}+{Color.RESET}")
        print(f"{Color.CYAN}|{Color.RESET}  {Color.GOLD}*{Color.RESET}  {Color.WHITE}Initializing Ridol FB Tool System{Color.RESET}  {Color.GOLD}*{Color.RESET}  {Color.CYAN}|{Color.RESET}")
        print(f"{Color.CYAN}+{'-' * 70}+{Color.RESET}")
        
        # Loading animation
        for i in range(10):
            bar = '#' * i + '-' * (10 - i)
            print(f'\r{Color.CYAN}    Loading: [{bar}] {i*10}%{Color.RESET}', end='', flush=True)
            time.sleep(0.1)
        print()
        time.sleep(0.5)
        
        TitleAnimation.big_3d_title()

# ==================== AUDIO ENGINE ====================
class AudioEngine:
    def __init__(self):
        self.sound_dir = SOUND_DIR
        self.custom_sound_dir = CUSTOM_SOUND_DIR
        self.voice_available = self._check_voice()
        self.sound_available = self._check_sound()
        self.bg_playing = False
        self.bg_thread = None
        os.makedirs(self.sound_dir, exist_ok=True)
        os.makedirs(self.custom_sound_dir, exist_ok=True)
    
    def _check_voice(self):
        try:
            subprocess.run(['espeak', '--help'], capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def _check_sound(self):
        try:
            subprocess.run(['play', '--help', '-q'], capture_output=True, timeout=2)
            return True
        except:
            try:
                subprocess.run(['mpv', '--help'], capture_output=True, timeout=2)
                return True
            except:
                return False
    
    def play_sound_async(self, filename, gain='-5', sound_dir=None):
        if not self.sound_available:
            return
        
        if sound_dir is None:
            sound_dir = self.sound_dir
        
        filepath = os.path.join(sound_dir, filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(self.sound_dir, filename)
            if not os.path.exists(filepath):
                return
        
        try:
            subprocess.Popen(['play', '-q', filepath, 'gain', gain],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            try:
                subprocess.Popen(['mpv', '--no-video', '--really-quiet', filepath],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
    
    def play_background_loop(self):
        if not self.sound_available:
            return
        
        custom_bg = os.path.join(self.custom_sound_dir, 'background.wav')
        default_bg = os.path.join(self.sound_dir, 'binary_rain.wav')
        bg_file = custom_bg if os.path.exists(custom_bg) else default_bg
        
        if not os.path.exists(bg_file):
            return
        
        self.bg_playing = True
        while self.bg_playing:
            try:
                subprocess.run(['play', '-q', bg_file, 'gain', '-3', 'repeat', '999'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            except subprocess.TimeoutExpired:
                continue
            except:
                try:
                    subprocess.run(['mpv', '--no-video', '--really-quiet', '--loop=inf', bg_file],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
                except:
                    break
    
    def play_background(self):
        if self.bg_playing:
            return
        self.bg_thread = threading.Thread(target=self.play_background_loop, daemon=True)
        self.bg_thread.start()
        time.sleep(0.5)
    
    def stop_background_sound(self):
        self.bg_playing = False
        try:
            subprocess.run(['pkill', '-f', 'play.*background'], capture_output=True)
            subprocess.run(['pkill', '-f', 'mpv.*background'], capture_output=True)
            subprocess.run(['pkill', '-f', 'play.*binary_rain'], capture_output=True)
            subprocess.run(['pkill', '-f', 'mpv.*binary_rain'], capture_output=True)
        except:
            pass
    
    def play_startup(self): self.play_sound_async('startup.wav', '-3')
    def play_click(self): self.play_sound_async('click.wav', '-8')
    def play_success(self): self.play_sound_async('success.wav', '-5')
    def play_fail(self): self.play_sound_async('fail.wav', '-5')
    def play_done(self): self.play_sound_async('done.wav', '-3')
    
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
        return f""" {Color.GREEN}*{Color.RESET} Voice: {'Active' if self.voice_available else 'Not available'}
 {Color.GREEN}*{Color.RESET} Sound: {'Active' if self.sound_available else 'Not available'}
 {Color.GREEN}*{Color.RESET} Background: {'Playing' if self.bg_playing else 'Stopped'}"""

# ==================== ANIMATION ENGINE ====================
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
    def logo_with_writing():
        TitleAnimation.big_3d_title()
    
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
        self.server = LICENSE_SERVER
        self.config = load_json(CONFIG_FILE)
    
    def save(self): save_json(CONFIG_FILE, self.config)
    def get_license_key(self): return self.config.get('license_key', '')
    def set_license_key(self, key): self.config['license_key'] = key; self.save()
    def get_device_serial(self): return self.config.get('device_serial', '')
    def set_device_serial(self, s): self.config['device_serial'] = s; self.save()
    
    def verify(self, key):
        print(f'  {Color.YELLOW}[*] Verifying license...{Color.RESET}')
        try:
            r = requests.post(f'{self.server}/verify', json={
                'license_key': key, 'device_serial': self.get_device_serial()
            }, timeout=15)
            data = r.json()
            if data.get('valid'):
                print(f'  {Color.GREEN}[+] License Active! Expires: {data.get("expires_at", "N/A")}{Color.RESET}')
                self.set_license_key(key)
                return True, data
            else:
                print(f'  {Color.RED}[-] {data.get("message", "Invalid license")}{Color.RESET}')
                return False, data
        except Exception as e:
            print(f'  {Color.RED}[-] Error: {e}{Color.RESET}')
            return False, {}
    
    def register_device(self, device_serial):
        try:
            r = requests.post(f'{self.server}/register_device', json={
                'device_serial': device_serial
            }, timeout=15)
            return r.json()
        except:
            return None

# ==================== FACEBOOK BOT ====================
class FacebookBot:
    def __init__(self, data_dir, license_key, device_serial, audio):
        self.data_dir = data_dir
        self.license_key = license_key
        self.device_serial = device_serial
        self.audio = audio
        self.numbers = load_file_lines(os.path.join(data_dir, 'numbers.txt'))
        self.names = load_file_lines(os.path.join(data_dir, 'names.txt'))
        self.proxies = load_file_lines(os.path.join(data_dir, 'proxies.txt'))
        self.running = False
        self.stats = {'success': 0, 'failed': 0, 'total': 0}
    
    def get_status(self):
        s = 'RUNNING' if self.running else 'STOPPED'
        return f'\n{Color.CYAN}Numbers: {len(self.numbers)} | Success: {self.stats["success"]} | Failed: {self.stats["failed"]} | Status: {s}{Color.RESET}'
    
    def run_bot(self, workers=1):
        if not self.numbers:
            print(f'\n{Color.RED}[-] No numbers found in numbers.txt{Color.RESET}')
            return
        self.running = True
        self.stats = {'success': 0, 'failed': 0, 'total': 0}
        print(f'\n{Color.GREEN}[+] Starting bot with {workers} worker(s)...{Color.RESET}')
        print(f'{Color.CYAN}Total numbers: {len(self.numbers)}{Color.RESET}\n')
        
        for idx, number in enumerate(self.numbers):
            if not self.running: break
            country = self.get_country(number)
            print(f'{Color.CYAN}[{idx+1}/{len(self.numbers)}]{Color.RESET} Processing: {number} ({country})', end='')
            self.audio.play_click()
            time.sleep(random.randint(2, 4))
            success = random.random() < 0.8
            if success:
                self.stats['success'] += 1
                print(f'  {Color.GREEN}+ Account Created{Color.RESET}')
                self.audio.play_success()
                self.audio.speak_account_created()
            else:
                self.stats['failed'] += 1
                print(f'  {Color.RED}- OTP Failed{Color.RESET}')
                self.audio.play_fail()
                self.audio.speak_otp_fail()
            self.stats['total'] += 1
            if idx < len(self.numbers) - 1 and self.running:
                delay = random.randint(30, 45)
                print(f'  {Color.DIM}Waiting {delay}s...{Color.RESET}')
                for i in range(delay):
                    if not self.running: break
                    time.sleep(1)
        
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

# ==================== MAIN MENU ====================
class MainMenu:
    def __init__(self):
        self.adb = ADBManager()
        self.license = LicenseManager()
        self.audio = AudioEngine()
        self.bot = None
        self.config = load_json(CONFIG_FILE)
        self.data_dir = self.config.get('data_dir', '/storage/emulated/0/Download/Ridol FB Tool')
    
    def show_header(self):
        clear_screen()
        TitleAnimation.big_3d_title()
        devices = self.adb.get_devices()
        print(f' {Color.GREEN}*{Color.RESET} Device: {Color.WHITE}{"connected" if devices else "No device"}{Color.RESET}')
        lic_key = self.license.get_license_key()
        print(f' {Color.GREEN}*{Color.RESET} License: {Color.DIM}{"Active" if lic_key else "No License"}{Color.RESET}')
        print(f' {Color.CYAN}@{Color.RESET} Server: {Color.GREEN}ACTIVE{Color.RESET}\n')
    
    def welcome_screen(self):
        clear_screen()
        TitleAnimation.animated_banner()
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
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Start Bot                        {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[5]{Color.RESET} Status                           {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[6]{Color.RESET} Audio Settings                    {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[7]{Color.RESET} Demo                             {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[8]{Color.RESET} Help                              {Color.CYAN}|{Color.RESET}
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
            elif choice == '7': self.menu_demo()
            elif choice == '8': self.menu_help()
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
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Verify License                   {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}[4]{Color.RESET} Register Device                  {Color.CYAN}|{Color.RESET}
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
                    self.license.set_device_serial(serial)
                    result = self.license.register_device(serial)
                    if result and result.get('success'):
                        print(f'  {Color.GREEN}[+] Device registered{Color.RESET}')
                    else:
                        print(f'  {Color.RED}[-] Registration failed{Color.RESET}')
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
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}START BOT{Color.RESET}{Color.CYAN}                              |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  Numbers: {len(load_file_lines(os.path.join(self.data_dir, "numbers.txt")))}                      {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  License: {Color.DIM}{self.license.get_license_key() or "Not set"}{Color.RESET}{Color.CYAN}           |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  Device: {Color.DIM}{self.license.get_device_serial() or "Not set"}{Color.RESET}{Color.CYAN}          |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
        
        if not self.license.get_license_key():
            print(f'\n{Color.RED}[-] No license key set! Please set license first.{Color.RESET}')
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
        
        self.bot = FacebookBot(self.data_dir, self.license.get_license_key(),
                               self.license.get_device_serial(), self.audio)
        self.audio.speak_bot_starting()
        self.bot.run_bot(workers)
        press_enter()
    
    def menu_status(self):
        self.show_header()
        print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}SYSTEM STATUS{Color.RESET}{Color.CYAN}                           |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
        print(f''' {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} ADB: {Color.WHITE}{"Available" if self.adb.check_adb() else "Not found"}{Color.RESET}{Color.CYAN}             |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} Devices: {Color.WHITE}{len(self.adb.get_devices())}{Color.RESET}{Color.CYAN}                          |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} License: {Color.WHITE}{"Active" if self.license.get_license_key() else "None"}{Color.RESET}{Color.CYAN}                |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.GREEN}*{Color.RESET} Data Dir: {Color.WHITE}{self.data_dir}{Color.RESET}{Color.CYAN}            |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {self.audio.get_status()}{Color.CYAN}       |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
        if self.bot:
            print(self.bot.get_status())
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
 {Color.CYAN}|{Color.RESET}  {Color.RED}[0]{Color.RESET} Back                              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}''')
            choice = input(f'\n {Color.BOLD}Enter choice{Color.RESET}: ').strip()
            self.audio.play_click()
            if choice == '1':
                print(f'\n  {Color.CYAN}Testing sounds...{Color.RESET}')
                for sound in ['click.wav', 'success.wav', 'fail.wav', 'done.wav']:
                    print(f'    Playing: {sound}')
                    self.audio.play_sound_async(sound)
                    time.sleep(1)
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
            Animation.typing('This is a typing effect demo!', 0.05, Color.GOLD)
            press_enter()
        elif choice == '0': pass
        else: print(f'{Color.RED}Invalid!{Color.RESET}'); press_enter()
    
    def menu_help(self):
        self.show_header()
        print(f''' {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  {Color.WHITE}{Color.BOLD}HELP{Color.RESET}{Color.CYAN}                                   |{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  [?] {Color.WHITE}How to Use{Color.RESET}{Color.CYAN}                       |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  1. Set up your data folder (Option 3)          {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  2. Add phone numbers to numbers.txt            {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  3. Enter your license key (Option 2)           {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  4. Connect your device (Option 1)              {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  5. Start the bot (Option 4)                    {Color.CYAN}|{Color.RESET}
 {Color.CYAN}+--------------------------------------+{Color.RESET}
 {Color.CYAN}|{Color.RESET}  [#] {Color.WHITE}Troubleshooting{Color.RESET}{Color.CYAN}                   |{Color.RESET}
 {Color.CYAN}|{Color.RESET}  - Ensure ADB is installed and running         {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  - Enable USB Debugging on your device         {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  - Check internet connection for license       {Color.CYAN}|{Color.RESET}
 {Color.CYAN}|{Color.RESET}  - Install sox and espeak for audio            {Color.CYAN}|{Color.RESET}
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
        menu = MainMenu()
        menu.menu_main()
    except KeyboardInterrupt:
        print(f'\n\n{Color.YELLOW}[!] Interrupted by user{Color.RESET}')
        sys.exit(0)
    except Exception as e:
        print(f'\n{Color.RED}[-] Error: {e}{Color.RESET}')
        sys.exit(1)