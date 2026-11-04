#!/usr/bin/env python3
"""
Ridol Instagram Automation Tool v24.1
Pure Instagram Automation — CDP Real Click + content.js Full Scanner + Stealth

No proxy / No training / No credit / No Flask server.

Core scanning ported 1:1 from content.js:
  - collectAllRootsAndElements (shadow DOM + closed shadow + iframe nested)
  - findButtonDeep (5 strategies: clickable+exact, aria/title/value,
                    any-exact, TreeWalker text nodes, loose fallback)
  - pickDeepest, climbToClickable, isVisible, normText, elText
  - findResendItemInPopup (targeted resend finder — matches "Resend confirmation code"
                           or "Resend Bay Otp Code", excludes "Change mobile number"
                           and "Confirm by email")
  - setNativeValue (React-compatible typing)
  - enhancedSyntheticClick, touchAndKeyClick
  - blockVirtualKeyboard / hard block / clear inputs
  - State machine + resend limit (max 3)

Click strategy (4 layers, like content.js findAndClick):
  1) synthetic events
  2) direct .click()
  3) touch + keyboard events
  4) CDP trusted realClick (Input.dispatchMouseEvent)

Stealth:
  - WebRTC leak block (flags + JS kill)
  - navigator.webdriver hide
  - languages / plugins / userAgentData / WebGL vendor spoof
  - Random UA + AutomationControlled disabled
"""

import os
import sys
import time
import re
import random
import json
import subprocess
from datetime import datetime

# ==================== CONFIG ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.json')
ERROR_DIR = os.path.join(SCRIPT_DIR, 'Bot_Errors')
APP_VERSION = 'v24.1'

IG_SIGNUP_URL = "https://www.instagram.com/accounts/emailsignup/"
MAX_RESEND = 3


# ==================== COLORS ====================
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


def log_info(m):    print(f"{Color.CYAN}[IG ℹ️] {m}{Color.RESET}")
def log_success(m): print(f"{Color.GREEN}[IG ✅] {m}{Color.RESET}")
def log_warn(m):    print(f"{Color.YELLOW}[IG ⚠️] {m}{Color.RESET}")
def log_error(m):   print(f"{Color.RED}[IG ❌] {m}{Color.RESET}")


# ==================== DEPS ====================
try:
    import openpyxl
except ImportError:
    print("[*] Installing openpyxl...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'openpyxl'], capture_output=True)
    import openpyxl


# ==================== COUNTRY ====================
def get_country_from_phone(phone_number):
    phone = str(phone_number).strip().replace('+', '').replace(' ', '').replace('-', '')
    codes = {
        '228': 'TG', '1': 'US', '44': 'GB', '91': 'IN', '92': 'PK',
        '880': 'BD', '62': 'ID', '60': 'MY', '65': 'SG', '63': 'PH',
        '66': 'TH', '84': 'VN', '81': 'JP', '82': 'KR', '49': 'DE',
        '33': 'FR', '39': 'IT', '7': 'RU', '55': 'BR'
    }
    for c in sorted(codes.keys(), key=len, reverse=True):
        if phone.startswith(c):
            return codes[c]
    return 'XX'


# ==================== CHROMEDRIVER ====================
def get_chromedriver_path():
    paths = [
        '/data/data/com.termux/files/usr/bin/chromedriver',
        '/data/data/com.termux/files/usr/lib/chromium/chromedriver',
        '/data/data/com.termux/files/usr/libexec/chromedriver',
        '/usr/bin/chromedriver',
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    try:
        r = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None

CHROMEDRIVER_PATH = get_chromedriver_path()


# ==================== EXCEL ====================
def read_numbers_from_excel(file_path):
    numbers = []
    try:
        if not os.path.exists(file_path):
            log_error(f"File not found: {file_path}")
            return []
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        log_info(f"Sheet: {sheet.title}")
        for row in sheet.iter_rows(values_only=True):
            num = row[1] if len(row) > 1 else None
            if num:
                s = str(num).strip()
                if 'E+' in s:
                    s = "{:.0f}".format(float(num))
                clean = re.sub(r'[^0-9]', '', s)
                if len(clean) >= 7:
                    numbers.append({'number': clean, 'country': get_country_from_phone(clean)})
        wb.close()
        log_success(f"Total numbers: {len(numbers)}")
        return numbers
    except Exception as e:
        log_error(f"Excel error: {e}")
        return []


# ==================== SCREENSHOT ====================
def take_error_screenshot(driver, phone):
    try:
        os.makedirs(ERROR_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(ERROR_DIR, f"error_{phone}_{ts}.png")
        driver.save_screenshot(path)
        log_warn(f"Screenshot: {path}")
        return path
    except Exception as e:
        log_error(f"Screenshot failed: {e}")
        return None


# =====================================================================
# ✅ JS HELPERS — content.js থেকে 1:1 port
# =====================================================================

# ---- SHARED SCANNER CORE ----
JS_SCANNER_CORE = r"""
function normText(s) {
    return String(s || '').replace(/[\u200B-\u200D\uFEFF\u00A0]/g, ' ').replace(/\s+/g, ' ').trim();
}
function elText(el) {
    try { return normText(el.innerText !== undefined && el.innerText !== '' ? el.innerText : el.textContent); }
    catch (e) { return ''; }
}
function isVisible(el) {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    const st = getComputedStyle(el);
    return st.visibility !== 'hidden' && st.display !== 'none';
}
function getAnyShadowRoot(el) {
    if (el.shadowRoot) return el.shadowRoot;
    try {
        if (typeof chrome !== 'undefined' && chrome.dom && chrome.dom.openOrClosedShadowRoot) {
            return chrome.dom.openOrClosedShadowRoot(el);
        }
    } catch (e) {}
    return null;
}
function collectAllRootsAndElements() {
    const roots = [document], seen = new Set([document]), elements = [];
    for (let i = 0; i < roots.length; i++) {
        let all;
        try { all = roots[i].querySelectorAll('*'); } catch (e) { continue; }
        for (const el of all) {
            elements.push(el);
            const sr = getAnyShadowRoot(el);
            if (sr && !seen.has(sr)) { seen.add(sr); roots.push(sr); }
            if (el.tagName === 'IFRAME' || el.tagName === 'FRAME') {
                try {
                    const d = el.contentDocument;
                    if (d && d.documentElement && !seen.has(d)) { seen.add(d); roots.push(d); }
                } catch (e) {}
            }
        }
    }
    return { roots, elements };
}
const CLICKABLE_SEL = 'button, [role="button"], a, input[type="button"], input[type="submit"], [role="link"], [tabindex], [onclick]';
function pickDeepest(list) {
    let best = null;
    for (const el of list) {
        if (!isVisible(el)) continue;
        if (!best || best.contains(el)) best = el;
        else if (!el.contains(best)) best = el;
    }
    return best;
}
function climbToClickable(el, exactRegex) {
    try {
        const c = el.closest(CLICKABLE_SEL);
        if (c && exactRegex.test(elText(c))) return c;
    } catch (e) {}
    let cur = el;
    for (let i = 0; i < 4 && cur; i++) {
        try { if (getComputedStyle(cur).cursor === 'pointer' && exactRegex.test(elText(cur))) return cur; } catch (e) {}
        cur = cur.parentElement;
    }
    return el;
}
"""


# ---- findButtonDeep: ৫টি strategy (content.js হুবহু) ----
JS_FIND_BUTTON_DEEP = JS_SCANNER_CORE + r"""
function findButtonDeep(exactRegex, looseRegex) {
    let ctx;
    try { ctx = collectAllRootsAndElements(); } catch (e) { return null; }
    const strategies = [
        () => pickDeepest(ctx.elements.filter(el => {
            try { return el.matches(CLICKABLE_SEL) && exactRegex.test(elText(el)); } catch (e) { return false; }
        })),
        () => {
            const found = ctx.elements.filter(el => ['aria-label', 'title', 'value'].some(a => {
                const v = normText(el.getAttribute && el.getAttribute(a));
                return v && exactRegex.test(v);
            }));
            const el = pickDeepest(found);
            return el ? climbToClickable(el, exactRegex) : null;
        },
        () => {
            const el = pickDeepest(ctx.elements.filter(e => exactRegex.test(elText(e))));
            return el ? climbToClickable(el, exactRegex) : null;
        },
        () => {
            const found = [];
            for (const root of ctx.roots) {
                try {
                    const doc = root.nodeType === 9 ? root : root.ownerDocument;
                    const walker = doc.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
                    let node;
                    while ((node = walker.nextNode())) {
                        if (exactRegex.test(normText(node.nodeValue)) && node.parentElement) found.push(node.parentElement);
                    }
                } catch (e) {}
            }
            const el = pickDeepest(found);
            return el ? climbToClickable(el, exactRegex) : null;
        },
        () => {
            if (!looseRegex) return null;
            const found = ctx.elements.filter(e => {
                const t = elText(e);
                return t.length < 60 && looseRegex.test(t);
            });
            const el = pickDeepest(found);
            return el ? climbToClickable(el, exactRegex) : null;
        },
    ];
    for (const strat of strategies) {
        try { const el = strat(); if (el && isVisible(el)) return el; } catch (e) {}
    }
    return null;
}
return findButtonDeep(
    new RegExp(arguments[0], arguments[2] || 'i'),
    arguments[1] ? new RegExp(arguments[1], arguments[2] || 'i') : null
);
"""


# ---- targeted resend finder (UPDATED for screenshot) ----
# "Resend confirmation code" অথবা "Resend Bay Otp Code" খুঁজবে
# "Change mobile number" এবং "Confirm by email" বাদ দেবে
JS_FIND_RESEND_ITEM = JS_SCANNER_CORE + r"""
var resendPattern = /resend (confirmation code|bay otp code)/i;
var changePattern = /change mobile number|confirm by email/i;
var ctx = collectAllRootsAndElements();
var candidates = [];
for (var el of ctx.elements) {
    if (!isVisible(el)) continue;
    var txt = elText(el);
    // শুধু Resend confirmation code বা Resend Bay Otp Code ম্যাচ করবে
    if (resendPattern.test(txt) && !changePattern.test(txt) && txt.length < 60) {
        candidates.push(el);
    }
}
if (candidates.length === 0) return null;
var target = pickDeepest(candidates);
if (!target) return null;
return climbToClickable(target, resendPattern);
"""


# ---- enhancedSyntheticClick ----
JS_SYNTHETIC_CLICK = r"""
function simulateClick(element) {
    if (!element) return false;
    try {
        var rect = element.getBoundingClientRect();
        var cx = rect.left + rect.width / 2;
        var cy = rect.top + rect.height / 2;
        var opts = { bubbles: true, cancelable: true, view: window, clientX: cx, clientY: cy, button: 0 };
        element.dispatchEvent(new PointerEvent('pointerdown', Object.assign({}, opts, { pointerType: 'touch', isPrimary: true })));
        element.dispatchEvent(new MouseEvent('mousedown', opts));
        element.dispatchEvent(new PointerEvent('pointerup', Object.assign({}, opts, { pointerType: 'touch', isPrimary: true })));
        element.dispatchEvent(new MouseEvent('mouseup', opts));
        element.dispatchEvent(new MouseEvent('click', opts));
        return true;
    } catch (e) { return false; }
}
return simulateClick(arguments[0]);
"""


# ---- touchAndKeyClick ----
JS_TOUCH_KEY_CLICK = r"""
function touchAndKeyClick(el) {
    if (!el) return false;
    try {
        var r = el.getBoundingClientRect();
        var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        try { el.focus({ preventScroll: true }); } catch (e) {}
        try {
            var t = new Touch({
                identifier: Date.now(), target: el,
                clientX: cx, clientY: cy, pageX: cx, pageY: cy, screenX: cx, screenY: cy
            });
            el.dispatchEvent(new TouchEvent('touchstart', { bubbles: true, cancelable: true, touches: [t], targetTouches: [t], changedTouches: [t] }));
            el.dispatchEvent(new TouchEvent('touchend', { bubbles: true, cancelable: true, touches: [], targetTouches: [], changedTouches: [t] }));
        } catch (e) {}
        for (var k of [{ key: 'Enter', code: 'Enter', keyCode: 13 }, { key: ' ', code: 'Space', keyCode: 32 }]) {
            el.dispatchEvent(new KeyboardEvent('keydown', Object.assign({}, k, { bubbles: true, cancelable: true })));
            el.dispatchEvent(new KeyboardEvent('keyup', Object.assign({}, k, { bubbles: true, cancelable: true })));
        }
        return true;
    } catch (e) { return false; }
}
return touchAndKeyClick(arguments[0]);
"""


# ---- setNativeValue ----
JS_SET_NATIVE_VALUE = r"""
function setNativeValue(input, text) {
    if (!input) return false;
    var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    try {
        input.focus({ preventScroll: true });
        setter.call(input, '');
        input.dispatchEvent(new Event('input', { bubbles: true }));
        for (var i = 0; i < text.length; i++) {
            var ch = text[i];
            setter.call(input, text.slice(0, i + 1));
            input.dispatchEvent(new InputEvent('input', { bubbles: true, data: ch, inputType: 'insertText' }));
        }
        input.dispatchEvent(new Event('change', { bubbles: true }));
        return input.value === text;
    } catch (err) { return false; }
}
return setNativeValue(arguments[0], arguments[1]);
"""


# ---- keyboard blocks / clear ----
JS_BLOCK_KEYBOARD = r"""
try {
    document.querySelectorAll('input, textarea').forEach(function (el) {
        try { el.blur(); } catch (e) {}
        if (el.getAttribute('inputmode') !== 'none') {
            el.setAttribute('inputmode', 'none');
            el.setAttribute('autocomplete', 'off');
        }
    });
    if (document.activeElement && document.activeElement !== document.body) {
        document.activeElement.blur();
    }
} catch (e) {}
return true;
"""


JS_HARD_BLOCK_KEYBOARD = r"""
try {
    document.querySelectorAll('input, textarea').forEach(function (el) {
        try { el.blur(); } catch (e) {}
        el.setAttribute('readonly', 'true');
    });
    if (document.activeElement && document.activeElement !== document.body) {
        document.activeElement.blur();
    }
} catch (e) {}
return true;
"""


JS_CLEAR_INPUTS = r"""
try {
    document.querySelectorAll('input, textarea').forEach(function (el) {
        try { el.blur(); } catch (e) {}
        var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
        if (setter && setter.set) {
            setter.set.call(el, '');
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    });
} catch (e) {}
return true;
"""


# ---- input finder ----
JS_FIND_PHONE_INPUT = r"""
function isVisible(el) {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    const st = getComputedStyle(el);
    return st.visibility !== 'hidden' && st.display !== 'none';
}
var ACCEPTED = ['text', 'tel', 'number'];
var allInputs = Array.from(document.querySelectorAll('input')).filter(function (el) {
    var t = (el.getAttribute('type') || 'text').toLowerCase();
    return ACCEPTED.indexOf(t) !== -1 && isVisible(el);
});
if (!allInputs.length) return null;
var phoneInput = allInputs.find(function (el) {
    var ph = (el.getAttribute('placeholder') || '').toLowerCase();
    var al = (el.getAttribute('aria-label') || '').toLowerCase();
    return ph.includes('mobile') || ph.includes('phone') || ph.includes('number') ||
           al.includes('mobile') || al.includes('phone') || al.includes('number');
}) || allInputs.find(function (el) {
    return (el.getAttribute('type') || '').toLowerCase() === 'tel';
}) || allInputs[0];
return phoneInput;
"""


# =====================================================================
# ✅ PYTHON WRAPPERS
# =====================================================================

def js_find_button(driver, exact_pattern, loose_pattern=None, flags='i'):
    try:
        return driver.execute_script(JS_FIND_BUTTON_DEEP, exact_pattern, loose_pattern or '', flags)
    except Exception as e:
        log_error(f"findButtonDeep error: {e}")
        return None


def js_find_resend_item(driver):
    try:
        return driver.execute_script(JS_FIND_RESEND_ITEM)
    except Exception:
        return None


def js_find_phone_input(driver):
    try:
        return driver.execute_script(JS_FIND_PHONE_INPUT)
    except Exception:
        return None


def js_synthetic_click(driver, element):
    try: return bool(driver.execute_script(JS_SYNTHETIC_CLICK, element))
    except Exception: return False


def js_touch_key_click(driver, element):
    try: return bool(driver.execute_script(JS_TOUCH_KEY_CLICK, element))
    except Exception: return False


def js_set_native_value(driver, element, text):
    try: return bool(driver.execute_script(JS_SET_NATIVE_VALUE, element, text))
    except Exception as e:
        log_error(f"setNativeValue error: {e}")
        return False


def js_block_keyboard(driver):
    try: driver.execute_script(JS_BLOCK_KEYBOARD)
    except Exception: pass


def js_hard_block_keyboard(driver):
    try: driver.execute_script(JS_HARD_BLOCK_KEYBOARD)
    except Exception: pass


def js_clear_inputs(driver):
    try: driver.execute_script(JS_CLEAR_INPUTS)
    except Exception: pass


def get_body_text(driver):
    try: return driver.execute_script("return document.body ? document.body.innerText : '';")
    except Exception: return ''


def get_abs_center(driver, element):
    """content.js getAbsRect — nested iframe offset সহ absolute center coordinate"""
    try:
        return driver.execute_script("""
            var el = arguments[0];
            var r = el.getBoundingClientRect();
            var x = r.left, y = r.top;
            var win = window;
            while (win && win.frameElement) {
                var fr = win.frameElement.getBoundingClientRect();
                x += fr.left + (win.frameElement.clientLeft || 0);
                y += fr.top + (win.frameElement.clientTop || 0);
                win = win.parent;
            }
            return { x: x + r.width / 2, y: y + r.height / 2 };
        """, element)
    except Exception:
        return None


# =====================================================================
# ✅ CDP REAL CLICK / TYPE
# =====================================================================

def cdp_real_click(driver, element):
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", element
        )
        time.sleep(0.4)
        coord = get_abs_center(driver, element)
        if not coord:
            return False
        x, y = coord['x'], coord['y']
        log_info(f"CDP Real Click at ({int(x)}, {int(y)})")

        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": "mouseMoved", "x": x, "y": y, "button": "none"
        })
        time.sleep(0.05)
        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": "mousePressed", "x": x, "y": y,
            "button": "left", "buttons": 1, "clickCount": 1
        })
        time.sleep(0.08)
        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": "mouseReleased", "x": x, "y": y,
            "button": "left", "buttons": 0, "clickCount": 1
        })
        return True
    except Exception as e:
        log_error(f"CDP click error: {e}")
        return False


def cdp_real_type(driver, element, text):
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", element
        )
        time.sleep(0.3)
        coord = get_abs_center(driver, element)
        if not coord:
            return False
        x, y = coord['x'], coord['y']

        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": "mousePressed", "x": x, "y": y,
            "button": "left", "buttons": 1, "clickCount": 1
        })
        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": "mouseReleased", "x": x, "y": y,
            "button": "left", "buttons": 0, "clickCount": 1
        })
        time.sleep(0.2)

        log_info(f"CDP Real Type at ({int(x)}, {int(y)}) -> \"{text}\"")
        for ch in text:
            driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                "type": "char", "text": ch
            })
            time.sleep(0.04)
        return True
    except Exception as e:
        log_error(f"CDP type error: {e}")
        return False


# =====================================================================
# ✅ MULTI-LAYER CLICK — content.js findAndClick
# =====================================================================

def find_and_click(driver, exact_pattern, loose_pattern, success_fn, desc="button"):
    el = js_find_button(driver, exact_pattern, loose_pattern)
    if not el:
        log_warn(f"'{desc}' not found (scanner)")
        return False

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.3)
    except Exception:
        pass

    # 1: synthetic
    log_info(f"Click 1/4 ({desc}): synthetic events...")
    js_synthetic_click(driver, el)
    time.sleep(4)
    if success_fn():
        return True

    # 2: direct .click()
    log_warn(f"Click 2/4 ({desc}): direct .click()...")
    el = js_find_button(driver, exact_pattern, loose_pattern) or el
    try:
        el.click()
    except Exception:
        try: driver.execute_script("arguments[0].click();", el)
        except Exception: pass
    time.sleep(4)
    if success_fn():
        return True

    # 3: touch + keyboard
    log_warn(f"Click 3/4 ({desc}): touch + keyboard events...")
    el = js_find_button(driver, exact_pattern, loose_pattern) or el
    js_touch_key_click(driver, el)
    time.sleep(4)
    if success_fn():
        return True

    # 4: CDP trusted real click
    log_warn(f"Click 4/4 ({desc}): CDP real click (trusted)...")
    el = js_find_button(driver, exact_pattern, loose_pattern) or el
    cdp_real_click(driver, el)
    time.sleep(4)
    return success_fn()


# =====================================================================
# ✅ BROWSER — Stealth + WebRTC block + CDP fingerprint spoof
# =====================================================================

class InstagramBrowser:
    def __init__(self):
        self.driver = None

    def start(self):
        if not CHROMEDRIVER_PATH:
            log_error("Chromedriver not found!")
            return False
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1200,900')

            # ===== STEALTH =====
            options.add_argument('--disable-webrtc')
            options.add_argument('--disable-rtc-smoothness-algorithm')
            options.add_argument('--force-fieldtrials=WebRTC-HideLocalIpsWithMdns/Enabled/')
            options.add_argument('--lang=en-US')
            options.add_argument('--timezone-offset=0')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')

            ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
            ]
            options.add_argument(f'user-agent={random.choice(ua_list)}')

            service = Service(CHROMEDRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=options)

            # ===== CDP FINGERPRINT SPOOF =====
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    window.RTCPeerConnection = undefined;
                    window.RTCSessionDescription = undefined;
                    window.RTCIceCandidate = undefined;
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => ({
                            length: 5,
                            item: function(i) { return this[i]; },
                            namedItem: function(name) { return null; }
                        })
                    });
                    Object.defineProperty(navigator, 'userAgentData', {get: () => undefined});
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) return 'Intel Inc.';
                        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                        return getParameter.call(this, parameter);
                    };
                """
            })

            log_success("Browser started (Stealth + WebRTC block + CDP spoof)")
            return True
        except Exception as e:
            log_error(f"Browser error: {e}")
            return False

    def stop(self):
        if self.driver:
            try: self.driver.quit()
            except Exception: pass


# =====================================================================
# ✅ STATE MACHINE
# =====================================================================

state = {
    'phone': None,
    'is_processing': False,
    'current_page_handled': '',
    'resend_count': 0,
    'next_number': False,
}


def reset_state(phone):
    state['phone'] = phone
    state['is_processing'] = False
    state['current_page_handled'] = ''
    state['resend_count'] = 0
    state['next_number'] = False


# =====================================================================
# ✅ PAGE HANDLERS
# =====================================================================

def handle_signup_page(driver):
    if state['current_page_handled'] == "SIGNUP" or state['is_processing']:
        return

    body = get_body_text(driver)
    for kw in ("Enter the confirmation code", "confirmation code",
               "Resend confirmation code", "I didn't get the code",
               "Code is too long", "Check that you entered it correctly"):
        if kw in body:
            return

    if "mobile number" not in body:
        return

    phone_input = js_find_phone_input(driver)
    if not phone_input:
        log_warn("Phone input not found. Waiting...")
        return

    state['is_processing'] = True
    state['current_page_handled'] = "SIGNUP"
    log_info("🎯 Signup Page Detected...")

    time.sleep(1)

    typed = js_set_native_value(driver, phone_input, state['phone'] or '')
    if not typed:
        log_warn("setNativeValue failed, using CDP real typing...")
        typed = cdp_real_type(driver, phone_input, state['phone'] or '')
    if typed:
        log_success(f"Typed: {state['phone']}")
    else:
        log_warn("Typing may have failed")

    time.sleep(0.8)

    ok = find_and_click(
        driver,
        r"^next$",
        r"next",
        lambda: "mobile number" not in get_body_text(driver),
        desc="Next"
    )
    if not ok:
        log_warn("'Next' click did not change the page")

    state['is_processing'] = False


def handle_device_nearby_popup(driver):
    if state['current_page_handled'] == "DEVICE_POPUP" or state['is_processing']:
        return

    body = get_body_text(driver)
    if "Make sure your device is nearby" not in body:
        return

    log_info("🎯 Device Nearby Popup Detected...")
    state['is_processing'] = True
    state['current_page_handled'] = "DEVICE_POPUP"

    time.sleep(2)
    ok = find_and_click(
        driver,
        r"^continue$",
        r"continue",
        lambda: "Make sure your device is nearby" not in get_body_text(driver),
        desc="Continue"
    )
    if not ok:
        log_warn("'Continue' click failed")

    state['is_processing'] = False


def handle_otp_page(driver):
    if state['current_page_handled'] == "OTP" or state['is_processing']:
        return

    body = get_body_text(driver)
    if "Enter the confirmation code" not in body and "confirmation code" not in body:
        return
    if "Resend confirmation code" in body or "Change mobile number" in body:
        return

    log_info("🎯 OTP Page Detected...")
    state['is_processing'] = True

    js_hard_block_keyboard(driver)

    if state['resend_count'] >= MAX_RESEND:
        log_warn(f"{MAX_RESEND} resend attempts reached. Moving to next number.")
        state['is_processing'] = False
        state['current_page_handled'] = "OTP_DONE"
        state['next_number'] = True
        return

    if state['resend_count'] == 0:
        state['current_page_handled'] = "OTP"
        time.sleep(2)
        js_clear_inputs(driver)

        clicked = find_and_click(
            driver,
            r"^i didn.?t get the code$",
            r"didn.?t get",
            lambda: "Resend confirmation code" in get_body_text(driver),
            desc="I didn't get the code"
        )

        if clicked:
            state['current_page_handled'] = "OTP_RESEND_POPUP"
        else:
            log_warn("'I didn't get the code' click failed.")
            state['current_page_handled'] = ''
    else:
        state['current_page_handled'] = "OTP_RESEND_POPUP"

    state['is_processing'] = False


def handle_resend_popup(driver):
    if state['current_page_handled'] != "OTP_RESEND_POPUP" or state['is_processing']:
        return

    body = get_body_text(driver)
    if "Resend confirmation code" not in body and "Change mobile number" not in body:
        return

    log_info("🎯 Resend Confirmation Popup Detected...")
    state['is_processing'] = True
    time.sleep(1.2)

    will_be = state['resend_count'] + 1
    log_info(f"Clicking Resend button ({will_be}/{MAX_RESEND})...")

    clicked = False

    # Targeted finder first (updated for "Resend confirmation code" / "Resend Bay Otp Code")
    resend_btn = js_find_resend_item(driver)
    if resend_btn:
        log_info("Popup item found via targeted scan")

        # 1) synthetic
        js_synthetic_click(driver, resend_btn)
        time.sleep(4)
        if "Resend confirmation code" not in get_body_text(driver) and "Resend Bay Otp Code" not in get_body_text(driver):
            clicked = True
        else:
            # 2) direct .click()
            try:
                resend_btn.click()
            except Exception:
                try: driver.execute_script("arguments[0].click();", resend_btn)
                except Exception: pass
            time.sleep(4)
            if "Resend confirmation code" not in get_body_text(driver) and "Resend Bay Otp Code" not in get_body_text(driver):
                clicked = True
            else:
                # 3) CDP real click
                cdp_real_click(driver, resend_btn)
                time.sleep(4)
                clicked = ("Resend confirmation code" not in get_body_text(driver) and 
                           "Resend Bay Otp Code" not in get_body_text(driver))

    if not clicked:
        log_warn("Targeted finder failed, falling back to findAndClick...")
        clicked = find_and_click(
            driver,
            r"^resend (confirmation code|bay otp code)$",
            r"resend (confirmation code|bay otp code)",
            lambda: "Resend confirmation code" not in get_body_text(driver) and "Resend Bay Otp Code" not in get_body_text(driver),
            desc="Resend (targeted fallback)"
        )

    if clicked:
        state['resend_count'] += 1
        if state['resend_count'] >= MAX_RESEND:
            log_warn(f"{MAX_RESEND} resend attempts completed. Moving to next number.")
            state['current_page_handled'] = "OTP_DONE"
            state['next_number'] = True
        else:
            state['current_page_handled'] = "OTP"
    else:
        log_warn("Resend click failed.")
        state['current_page_handled'] = "OTP"

    state['is_processing'] = False


# =====================================================================
# ✅ ROUTER + LOOP
# =====================================================================

def run_automation(driver):
    if state['is_processing']:
        return
    try:
        handle_resend_popup(driver)
        if state['is_processing']: return

        handle_otp_page(driver)
        if state['is_processing']: return

        handle_device_nearby_popup(driver)
        if state['is_processing']: return

        handle_signup_page(driver)
    except Exception as e:
        log_error(f"Automation error: {e}")
        state['is_processing'] = False


def process_phone(driver, phone):
    reset_state(phone)
    log_info(f"🚀 Automation started for {phone}")

    try:
        driver.get(IG_SIGNUP_URL)
        time.sleep(4)
    except Exception as e:
        log_error(f"Navigation error: {e}")
        return False

    last_body = ""
    stable_count = 0
    max_iterations = 120
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        if state['next_number']:
            log_success(f"Next number triggered after {state['resend_count']} resends")
            return True

        js_block_keyboard(driver)
        run_automation(driver)

        if state['next_number']:
            log_success(f"Next number triggered after {state['resend_count']} resends")
            return True

        body = get_body_text(driver)
        if body == last_body:
            stable_count += 1
        else:
            stable_count = 0
            last_body = body

        if stable_count >= 10:
            if "confirmation code" in body or "Resend confirmation code" in body or "Resend Bay Otp Code" in body:
                log_warn("Stuck on OTP page — no progress")
                return False
            log_success("Page stable — flow likely completed")
            return True

        time.sleep(2)

    log_warn("Max iterations reached")
    return False


# =====================================================================
# ✅ MAIN APP
# =====================================================================

class InstagramApp:
    def __init__(self):
        self.excel_file = self.load_config().get('excel_file', '')

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'excel_file': self.excel_file}, f, indent=2)

    def draw_ui(self):
        os.system('clear')
        print(f"""{Color.GOLD}
   ██████╗ ██╗██████╗  ██████╗ ██╗
   ██╔══██╗██║██╔══██╗██╔═══██╗██║
   ██████╔╝██║██║  ██║██║   ██║██║
   ██╔══██╗██║██║  ██║██║   ██║██║
   ██║  ██║██║██████╔╝╚██████╔╝███████╗
   ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝{Color.RESET}""")
        print(f"            {Color.WHITE}{Color.BOLD}INSTAGRAM AUTOMATION {APP_VERSION}{Color.RESET}")
        print(f"         {Color.PINK}CDP Real Click + content.js Scanner{Color.RESET}")
        print(f"  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
        br = f"{Color.GREEN}Ready{Color.RESET}" if CHROMEDRIVER_PATH else f"{Color.RED}Missing{Color.RESET}"
        print(f"  {Color.CYAN}│{Color.RESET}  Browser : {br}")
        print(f"  {Color.CYAN}│{Color.RESET}  Excel   : {Color.DIM}{self.excel_file or 'Not set'}{Color.RESET}")
        print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")
        if CHROMEDRIVER_PATH:
            print(f"  {Color.DIM}Chromedriver: {CHROMEDRIVER_PATH}{Color.RESET}")

    def run_instagram_creator(self):
        if not CHROMEDRIVER_PATH:
            log_error("Chromedriver not found! Run: pkg install chromedriver")
            time.sleep(2)
            return

        if not self.excel_file or not os.path.exists(self.excel_file):
            log_error(f"Excel file missing: {self.excel_file}")
            time.sleep(2)
            return

        log_info("Reading Excel...")
        numbers_data = read_numbers_from_excel(self.excel_file)
        if not numbers_data:
            log_error("No numbers found")
            time.sleep(2)
            return

        log_success(f"Found {len(numbers_data)} numbers")
        print("-" * 50)

        success_count = 0
        failed_count = 0

        for idx, data in enumerate(numbers_data, 1):
            phone = data['number']
            country = data['country']

            print(f"\n{Color.GOLD}{'='*50}{Color.RESET}")
            print(f"{Color.GOLD}[{idx}/{len(numbers_data)}] Phone: {phone} | Country: {country}{Color.RESET}")
            print(f"{Color.GOLD}{'='*50}{Color.RESET}")

            browser = InstagramBrowser()
            if not browser.start():
                failed_count += 1
                continue

            try:
                ok = process_phone(browser.driver, phone)
                if ok:
                    success_count += 1
                    log_success(f"Success: {phone}")
                else:
                    failed_count += 1
                    log_error(f"Failed: {phone}")
                    take_error_screenshot(browser.driver, phone)
            except Exception as e:
                log_error(f"Crash on {phone}: {e}")
                take_error_screenshot(browser.driver, phone)
                failed_count += 1
            finally:
                browser.stop()

        print("\n" + "=" * 50)
        print(f"{Color.GREEN}COMPLETE{Color.RESET}")
        print("=" * 50)
        print(f"Total:   {len(numbers_data)}")
        print(f"Success: {Color.GREEN}{success_count}{Color.RESET}")
        print(f"Failed:  {Color.RED}{failed_count}{Color.RESET}")
        print("=" * 50)
        input("\nPress Enter to continue...")

    def main_loop(self):
        while True:
            self.draw_ui()
            print(f"\n  {Color.CYAN}┌──────────────────────────────────────────┐{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}   MAIN MENU                           {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}├──────────────────────────────────────────┤{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[1]{Color.RESET} Start Instagram Automation         {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[2]{Color.RESET} Set Excel File                     {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.GREEN}[3]{Color.RESET} Install Dependencies               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}│{Color.RESET}  {Color.RED}[0]{Color.RESET} Exit                               {Color.CYAN}│{Color.RESET}")
            print(f"  {Color.CYAN}└──────────────────────────────────────────┘{Color.RESET}")

            choice = input(f"\n{Color.BOLD} Enter choice: {Color.RESET}").strip()

            if choice == '1':
                self.run_instagram_creator()
            elif choice == '2':
                path = input(f"\n{Color.CYAN} Excel file path: {Color.RESET}").strip().strip('"').strip("'")
                if path and os.path.exists(path):
                    self.excel_file = path
                    self.save_config()
                    log_success(f"Saved: {path}")
                else:
                    log_error(f"File not found: {path}")
                time.sleep(2)
            elif choice == '3':
                log_info("Installing dependencies...")
                subprocess.run(
                    "pkg update -y && pkg install -y tur-repo python chromium chromedriver "
                    "&& pip install --upgrade pip && pip install selenium openpyxl",
                    shell=True
                )
                global CHROMEDRIVER_PATH
                CHROMEDRIVER_PATH = get_chromedriver_path()
                if CHROMEDRIVER_PATH:
                    log_success(f"Found: {CHROMEDRIVER_PATH}")
                else:
                    log_error("Not found! Try: pkg install chromedriver")
                input("\nPress Enter...")
            elif choice == '0':
                print(f"\n{Color.GREEN}Goodbye!{Color.RESET}")
                sys.exit()


if __name__ == '__main__':
    try:
        InstagramApp().main_loop()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}[!] Interrupted{Color.RESET}")
        sys.exit()