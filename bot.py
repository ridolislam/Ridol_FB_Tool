#!/usr/bin/env python3
"""
Ridol FB Tool v2.0 - Facebook Lite Account Creator
Features: Smart proxy rotation, country matching, user folder support
Authorization: Authorized security testing only
"""

import os, sys, time, random, json, re, subprocess, threading
import requests
from datetime import datetime

# ========== কনফিগারেশন ==========
LICENSE_SERVER = "https://ridol-fb-tool.onrender.com"
FB_PACKAGE = "com.facebook.lite"
APP_NAME = "Ridol FB Tool"

# ========== দেশের কোড ম্যাপিং (Phone → Country) ==========
COUNTRY_MAP = {
    "880": "BD",  # বাংলাদেশ
    "91": "IN",   # ভারত
    "92": "PK",   # পাকিস্তান
    "93": "AF",   # আফগানিস্তান
    "94": "LK",   # শ্রীলঙ্কা
    "95": "MM",   # মায়ানমার
    "977": "NP",  # নেপাল
    "975": "BT",  # ভুটান
    "976": "MN",  # মঙ্গোলিয়া
    "86": "CN",   # চীন
    "852": "HK",  # হংকং
    "81": "JP",   # জাপান
    "82": "KR",   # দক্ষিণ কোরিয়া
    "65": "SG",   # সিঙ্গাপুর
    "60": "MY",   # মালয়েশিয়া
    "62": "ID",   # ইন্দোনেশিয়া
    "63": "PH",   # ফিলিপাইন
    "66": "TH",   # থাইল্যান্ড
    "84": "VN",   # ভিয়েতনাম
    "1": "US",    # USA
    "44": "GB",   # UK
    "49": "DE",   # জার্মানি
    "33": "FR",   # ফ্রান্স
    "39": "IT",   # ইতালি
    "34": "ES",   # স্পেন
    "7": "RU",    # রাশিয়া
    "55": "BR",   # ব্রাজিল
    "52": "MX",   # মেক্সিকো
    "20": "EG",   # মিশর
    "27": "ZA",   # দক্ষিণ আফ্রিকা
    "61": "AU",   # অস্ট্রেলিয়া
    "234": "NG",  # নাইজেরিয়া
    "254": "KE",  # কেনিয়া
    "233": "GH",  # ঘানা
    "212": "MA",  # মরক্কো
}

def get_country_code(phone):
    """ফোন নাম্বার থেকে দেশের কোড বের করে"""
    phone = phone.strip().replace("+", "").replace(" ", "")
    # Longest prefix match
    matched = ""
    for code in sorted(COUNTRY_MAP.keys(), key=len, reverse=True):
        if phone.startswith(code):
            matched = code
            break
    if matched:
        return COUNTRY_MAP[matched], matched
    return "XX", ""  # Unknown

# ========== ADB কন্ট্রোলার ==========
class ADB:
    @staticmethod
    def tap(x, y):
        subprocess.run(["adb", "shell", "input", "tap", str(int(x)), str(int(y))], capture_output=True)
    
    @staticmethod
    def swipe(x1, y1, x2, y2, ms=300):
        subprocess.run(["adb", "shell", "input", "swipe", str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(ms)], capture_output=True)
    
    @staticmethod
    def text(text):
        safe = text.replace(" ", "%s")
        subprocess.run(["adb", "shell", "input", "text", safe], capture_output=True)
    
    @staticmethod
    def keyevent(key):
        subprocess.run(["adb", "shell", "input", "keyevent", str(key)], capture_output=True)
    
    @staticmethod
    def open_app(package):
        subprocess.run(["adb", "shell", "monkey", "-p", package, "1"], capture_output=True)
        time.sleep(4)
    
    @staticmethod
    def close_app(package):
        subprocess.run(["adb", "shell", "am", "force-stop", package], capture_output=True)
    
    @staticmethod
    def is_installed(package):
        r = subprocess.run(["adb", "shell", "pm", "list", "packages", package], capture_output=True, text=True)
        return package in r.stdout
    
    @staticmethod
    def read_sms():
        try:
            r = subprocess.check_output(["adb", "shell", "content", "query",
                "--uri", "content://sms/inbox",
                "--projection", "body,address,date",
                "--sort", "date DESC", "--limit", "5"]).decode()
            return r
        except: return ""
    
    @staticmethod
    def extract_otp(text):
        patterns = [
            r'(\d{4,6})',
            r'OTP[:\s]*(\d{4,6})',
            r'code[:\s]*(\d{4,6})',
            r'(\d{4,6})\s*is\s*your',
            r'verification\s*code[:\s]*(\d{4,6})',
            r'(\d{4,6})\s+is\s+your\s+Facebook'
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m: return m.group(1)
        return None

# ========== অন্যান্য ইউটিলিটি ==========
def get_device_id():
    try:
        return subprocess.check_output(["adb", "shell", "settings", "get", "secure", "android_id"]).decode().strip()
    except: return "UNKNOWN"

def get_public_ip():
    try: return requests.get("https://api.ipify.org", timeout=5).text
    except: return "0.0.0.0"

# ========== Proxy Manager ==========
class ProxyManager:
    """Rotating proxy with country matching"""
    def __init__(self, proxy_file):
        self.proxies = []  # [(url, country), ...]
        self.current_idx = -1
        self.load_proxies(proxy_file)
    
    def load_proxies(self, path):
        """proxies.txt ফরম্যাট: proxy_url:COUNTRY_CODE
        Example: http://user:pass@1.2.3.4:8080:BD
        """
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.rsplit(':', 1)
                        if len(parts) == 2 and len(parts[1]) == 2:
                            self.proxies.append((parts[0], parts[1].upper()))
                        else:
                            self.proxies.append((line, "XX"))  # Unknown country
            print(f"[✓] Loaded {len(self.proxies)} proxies")
        except:
            print("[!] No proxy file found")
    
    def get_proxy_for_country(self, country_code):
        """দেশ অনুযায়ী প্রোক্সি সিলেক্ট"""
        matched = [p for p in self.proxies if p[1] == country_code]
        if matched:
            return random.choice(matched)[0]
        # Fallback: random proxy
        if self.proxies:
            return random.choice(self.proxies)[0]
        return None
    
    def set_device_proxy(self, proxy_url, device_ip="192.168.1.1"):
        """ADB দিয়ে device proxy সেট"""
        if not proxy_url:
            return False
        try:
            # Parse proxy
            match = re.match(r'http://(.*?):(.*?)@(.*?):(\d+)', proxy_url)
            if not match:
                # Direct proxy: http://host:port
                match2 = re.match(r'http://(.*?):(\d+)', proxy_url)
                if match2:
                    host, port = match2.group(1), match2.group(2)
                    subprocess.run(["adb", "shell", "settings", "put", "global", "http_proxy", f"{host}:{port}"], capture_output=True)
                    return True
                return False
            
            user, pwd, host, port = match.group(1), match.group(2), match.group(3), match.group(4)
            # Android doesn't support authenticated proxies natively via settings
            # Use proxy app or iptables redirect. For now, set HTTP proxy only
            subprocess.run(["adb", "shell", "settings", "put", "global", "http_proxy", f"{host}:{port}"], capture_output=True)
            print(f"    [Proxy] Set: {host}:{port}")
            return True
        except:
            return False
    
    def clear_device_proxy(self):
        try:
            subprocess.run(["adb", "shell", "settings", "put", "global", "http_proxy", ":0"], capture_output=True)
        except:
            pass
    
    def rotate(self):
        """র‍্যান্ডম প্রোক্সি সিলেক্ট"""
        if not self.proxies:
            return None
        self.current_idx = (self.current_idx + 1) % len(self.proxies)
        return self.proxies[self.current_idx][0]

# ========== Facebook Bot ==========
class FacebookBot:
    def __init__(self, data_dir):
        self.adb = ADB()
        self.data_dir = data_dir
        self.numbers = self.load_file(os.path.join(data_dir, "numbers.txt"))
        self.names = self.load_file(os.path.join(data_dir, "names.txt"))
        proxy_file = os.path.join(data_dir, "proxies.txt")
        self.proxy_manager = ProxyManager(proxy_file)
        self.device_id = get_device_id()
        
        # Screen resolution check
        self.get_screen_size()
        
        # Default coords (1080x2400)
        self.coords = {}
        self.calc_coords()
    
    def get_screen_size(self):
        """ডায়নামিক স্ক্রিন রেজুলেশন ডিটেক্ট"""
        try:
            r = subprocess.check_output(["adb", "shell", "wm", "size"]).decode().strip()
            match = re.search(r'(\d+)x(\d+)', r)
            if match:
                self.screen_w = int(match.group(1))
                self.screen_h = int(match.group(2))
            else:
                self.screen_w, self.screen_h = 1080, 2400
        except:
            self.screen_w, self.screen_h = 1080, 2400
        print(f"[*] Screen: {self.screen_w}x{self.screen_h}")
    
    def calc_coords(self):
        """রেজুলেশন অনুযায়ী কোঅর্ডিনেট অ্যাডজাস্ট"""
        w, h = self.screen_w, self.screen_h
        self.coords = {
            "create_account": (w//2, int(h*0.88)),
            "first_name": (int(w*0.25), int(h*0.22)),
            "last_name": (int(w*0.25), int(h*0.30)),
            "phone": (int(w*0.25), int(h*0.38)),
            "sign_up": (w//2, int(h*0.75)),
            "otp_field": (w//2, int(h*0.45)),
            "confirm_otp": (w//2, int(h*0.55)),
            "next": (w//2, int(h*0.85)),
            "skip": (w//2, int(h*0.92)),
            "gender_male": (int(w*0.30), int(h*0.58)),
            "gender_female": (int(w*0.70), int(h*0.58)),
        }
    
    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except:
            return []
    
    def random_name(self):
        parts = random.choice(self.names).split()
        if len(parts) >= 2:
            return parts[0], " ".join(parts[1:])
        return parts[0], "User"
    
    def random_dob(self):
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        y = random.randint(1985, 2002)
        return m, d, y
    
    def create_account(self, phone_number, idx=0):
        """একটি ফেসবুক একাউন্ট তৈরি"""
        print(f"\n{'='*50}")
        print(f"[+] Account #{idx+1}")
        print(f"    Phone: {phone_number}")
        
        # Detect country
        country, prefix = get_country_code(phone_number)
        print(f"    Country: {country} (+{prefix})")
        
        # Set proxy for this country
        proxy = self.proxy_manager.get_proxy_for_country(country)
        if proxy:
            print(f"    Proxy: {proxy[:30]}...")
            self.proxy_manager.set_device_proxy(proxy)
        else:
            print(f"    Proxy: None (direct)")
            self.proxy_manager.clear_device_proxy()
        
        time.sleep(2)
        
        # Open Facebook Lite
        if not self.adb.is_installed(FB_PACKAGE):
            print("[-] Facebook Lite not installed!")
            return False
        
        print("    Opening Facebook Lite...")
        self.adb.open_app(FB_PACKAGE)
        time.sleep(4)
        
        # Click Create Account
        print("    Clicking Create Account...")
        self.adb.tap(*self.coords["create_account"])
        time.sleep(3)
        
        # First Name
        first, last = self.random_name()
        print(f"    Name: {first} {last}")
        self.adb.tap(*self.coords["first_name"])
        time.sleep(0.5)
        self.adb.text(first)
        time.sleep(0.5)
        
        # Last Name
        self.adb.tap(*self.coords["last_name"])
        time.sleep(0.5)
        self.adb.text(last)
        time.sleep(0.5)
        
        # Phone Number
        self.adb.tap(*self.coords["phone"])
        time.sleep(0.5)
        self.adb.text(phone_number)
        time.sleep(0.5)
        
        # DOB
        m, d, y = self.random_dob()
        print(f"    DOB: {m}/{d}/{y}")
        for val in [m, d, y]:
            self.adb.tap(*self.coords["phone"])
            time.sleep(0.3)
        
        # Gender
        gender = random.choice(["male", "female"])
        print(f"    Gender: {gender}")
        if gender == "male":
            self.adb.tap(*self.coords["gender_male"])
        else:
            self.adb.tap(*self.coords["gender_female"])
        time.sleep(1)
        
        # Scroll down
        self.adb.swipe(self.screen_w//2, int(self.screen_h*0.7), self.screen_w//2, int(self.screen_h*0.3), 500)
        time.sleep(1)
        
        # Sign Up
        print("    Signing up...")
        self.adb.tap(*self.coords["sign_up"])
        time.sleep(5)
        
        # Wait for OTP
        print("    Waiting for OTP...")
        otp = None
        for attempt in range(6):
            time.sleep(10)
            sms_data = self.adb.read_sms()
            if sms_data:
                otp = self.adb.extract_otp(sms_data)
                if otp:
                    print(f"    ✓ OTP: {otp}")
                    break
            print(f"    Waiting... ({attempt+1}/6)")
        
        if otp:
            # Enter OTP
            self.adb.tap(*self.coords["otp_field"])
            time.sleep(0.5)
            self.adb.text(otp)
            time.sleep(2)
            
            # Confirm
            self.adb.tap(*self.coords["confirm_otp"])
            time.sleep(3)
            
            # Skip
            for _ in range(2):
                self.adb.tap(*self.coords["skip"])
                time.sleep(2)
            
            print(f"    ✓ Account created successfully!")
            self.proxy_manager.clear_device_proxy()
            self.adb.close_app(FB_PACKAGE)
            return True
        else:
            print(f"    ✗ OTP not received")
            self.adb.close_app(FB_PACKAGE)
            return False
    
    def run(self):
        """বট চালান"""
        print(f"[*] Device ID: {self.device_id}")
        print(f"[*] Numbers: {len(self.numbers)}")
        print(f"[*] Names: {len(self.names)}")
        print(f"[*] Proxies: {len(self.proxy_manager.proxies)}")
        
        if not self.numbers:
            print("[-] No numbers found in numbers.txt!")
            return
        if not self.names:
            print("[-] No names found in names.txt!")
            return
        
        for idx, num in enumerate(self.numbers):
            try:
                self.create_account(num, idx)
                delay = random.randint(45, 90)
                print(f"    Waiting {delay}s...")
                time.sleep(delay)
            except KeyboardInterrupt:
                print("\n[!] Stopped by user")
                break
            except Exception as e:
                print(f"[-] Error: {e}")
                time.sleep(10)

# ========== License Manager ==========
class LicenseManager:
    def __init__(self):
        self.server = LICENSE_SERVER
        self.device_id = get_device_id()
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.config = self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {"license_key": "", "device_id": self.device_id}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    
    def register_device(self):
        print(f"[*] Registering device: {self.device_id}")
        try:
            r = requests.post(f"{self.server}/register_device", json={"device_id": self.device_id}, timeout=10)
            return r.json()
        except Exception as e:
            print(f"[-] Server error: {e}")
            return None
    
    def verify_license(self, key):
        print(f"[*] Verifying license...")
        try:
            r = requests.post(f"{self.server}/verify", json={"license_key": key, "device_id": self.device_id}, timeout=10)
            data = r.json()
            if data.get("valid"):
                print(f"[✓] License valid until: {data.get('expires_at')}")
                self.config["license_key"] = key
                self.save_config()
                return True
            else:
                print(f"[-] {data.get('message', 'Invalid')}")
                return False
        except Exception as e:
            print(f"[-] Server error: {e}")
            return False

# ========== Main ==========
def main():
    print(f"""
    ╔══════════════════════════════╗
    ║     {Ridol FB Tool} v2.0         ║
    ║  Smart Proxy + Auto Country  ║
    ╚══════════════════════════════╝
    """)
    
    # Check ADB
    try:
        subprocess.run(["adb", "version"], capture_output=True, check=True)
        print("[✓] ADB available")
    except:
        print("[-] ADB not found! Run: pkg install android-tools")
        sys.exit(1)
    
    # Check device
    devices = subprocess.check_output(["adb", "devices"]).decode()
    if "device\n" not in devices:
        print("[-] No device connected! Enable USB Debugging")
        sys.exit(1)
    print("[✓] Device connected")
    
    # Get data folder from user
    print("\n[i] আপনার ফাইলগুলো রাখুন: Internal Storage/Download/Ridol FB Tool/")
    print("[i] সেখানে names.txt, numbers.txt, proxies.txt রাখুন")
    default_path = "/storage/emulated/0/Download/Ridol FB Tool"
    folder = input(f"\n📁 ফোল্ডার পাথ দিন (Enter = '{default_path}'): ").strip()
    if not folder:
        folder = default_path
    
    # Check folder exists
    if not os.path.isdir(folder):
        print(f"[!] ফোল্ডার নেই: {folder}")
        create = input("ফোল্ডার তৈরি করবেন? (Y/n): ").strip().lower()
        if create != 'n':
            os.makedirs(folder, exist_ok=True)
            print(f"[✓] Created: {folder}")
            # Create sample files
            for fname, content in [
                ("numbers.txt", "# প্রতি লাইনে একটি ফোন নাম্বার\n+88017XXXXXXXX\n+88018XXXXXXXX\n"),
                ("names.txt", "John Doe\nJane Smith\n"),
                ("proxies.txt", "# http://user:pass@host:port:COUNTRY_CODE\n# Example:\n# http://user:pass@1.2.3.4:8080:BD\n# http://user:pass@5.6.7.8:3128:US\n")
            ]:
                fpath = os.path.join(folder, fname)
                if not os.path.exists(fpath):
                    with open(fpath, 'w') as f:
                        f.write(content)
                    print(f"  Created: {fname}")
        else:
            sys.exit(1)
    
    print(f"[✓] Using folder: {folder}")
    
    # License flow
    lm = LicenseManager()
    
    saved_key = lm.config.get("license_key", "")
    if saved_key:
        print(f"[*] Saved license found")
        if lm.verify_license(saved_key):
            pass
        else:
            saved_key = ""
    
    if not saved_key:
        reg = lm.register_device()
        if reg and reg.get("status") == "registered":
            print(f"[✓] Auto-registered: {reg.get('license_key')}")
            if lm.verify_license(reg.get("license_key")):
                pass
        else:
            print(f"\n[!] Device ID: {lm.device_id}")
            print("[!] Admin panel: " + LICENSE_SERVER + "/admin")
            key = input("\n🔑 Enter License Key: ").strip()
            if not lm.verify_license(key):
                print("[-] License verification failed!")
                sys.exit(1)
    
    # Start bot
    print("\n[*] Starting Facebook Bot...")
    bot = FacebookBot(folder)
    bot.run()

if __name__ == "__main__":
    main()
