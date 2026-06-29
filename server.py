#!/usr/bin/env python3
"""
Ridol FB Tool - License Server v8.5 (PostgreSQL Professional)
Fixed Proxy API with Multiple Fallback Sources
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import os
import re
import json
import random
import string
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
from datetime import datetime, timedelta
import time
import socket
import urllib.request

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURATION ====================
CLIPROXY_API_URL = os.environ.get('CLIPROXY_API_URL', '')
PORT = int(os.environ.get('PORT', 10000))
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
DATABASE_URL = os.environ.get('DATABASE_URL')

# ==================== DATABASE FUNCTIONS ====================

def get_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def init_db():
    print("🔄 Initializing PostgreSQL database...")
    conn = get_db()
    if not conn:
        print("❌ Could not connect to database")
        return False
    
    try:
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                credits INTEGER DEFAULT 100,
                max_browsers INTEGER DEFAULT 1,
                created_at TEXT,
                expires_at TEXT,
                is_active INTEGER DEFAULT 1,
                used_credits INTEGER DEFAULT 0,
                last_used TEXT,
                user_id TEXT,
                total_operations INTEGER DEFAULT 0
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                id SERIAL PRIMARY KEY,
                license_key TEXT,
                action TEXT,
                ip_used TEXT,
                country TEXT,
                timestamp TEXT,
                user_id TEXT,
                status TEXT,
                response_time INTEGER
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS proxy_cache (
                id SERIAL PRIMARY KEY,
                proxy_ip TEXT,
                proxy_port INTEGER,
                country TEXT,
                fetched_at TEXT,
                is_active INTEGER DEFAULT 1,
                used_count INTEGER DEFAULT 0,
                last_used TEXT
            )
        ''')
        
        c.execute('CREATE INDEX IF NOT EXISTS idx_license_key_pg ON licenses(license_key)')
        
        # Insert test license
        test_key = "RIDOL-TEST-0000-AAAA-BBBB"
        expires_at = (datetime.now() + timedelta(days=365)).isoformat()
        
        c.execute('''
            INSERT INTO licenses (license_key, credits, max_browsers, created_at, expires_at, is_active, user_id)
            VALUES (%s, %s, %s, %s, %s, 1, %s)
            ON CONFLICT (license_key) DO NOTHING
        ''', (test_key, 1000, 5, datetime.now().isoformat(), expires_at, 'TestUser'))
        
        conn.commit()
        c.close()
        conn.close()
        print("✅ Database initialized!")
        return True
    except Exception as e:
        print(f"❌ DB init error: {e}")
        return False

init_db()

# ==================== PROXY FETCH FUNCTIONS ====================

def fetch_proxy_cliproxy(country='Rand'):
    """Fetch proxy from Cliproxy API"""
    if not CLIPROXY_API_URL:
        return None
    
    try:
        url = f"{CLIPROXY_API_URL}?region={country}&num=1&time=10&format=n&type=txt"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            ip = resp.text.strip()
            if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
                return ip
    except:
        pass
    return None

def fetch_proxy_free_proxy():
    """Fetch proxy from free proxy list (fallback)"""
    try:
        # Try multiple free proxy sources
        sources = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
        ]
        
        for url in sources:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    lines = resp.text.strip().split('\n')
                    proxies = [l.strip() for l in lines if ':' in l]
                    if proxies:
                        proxy = random.choice(proxies)
                        ip = proxy.split(':')[0]
                        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
                            return ip
            except:
                continue
    except:
        pass
    return None

def fetch_proxy_mock():
    """Mock proxy for testing when no API available"""
    mock_ips = [
        "45.33.32.156", "45.33.32.157", "45.33.32.158",
        "192.241.198.203", "192.241.198.204", "192.241.198.205",
        "104.236.35.171", "104.236.35.172", "104.236.35.173"
    ]
    return random.choice(mock_ips)

def get_proxy_ip(country='Rand'):
    """Main proxy fetch function with multiple fallbacks"""
    
    # Try 1: Cliproxy API
    print(f"🔄 Trying Cliproxy API...")
    ip = fetch_proxy_cliproxy(country)
    if ip:
        print(f"✅ Got proxy from Cliproxy: {ip}")
        return ip
    
    # Try 2: Free proxy list
    print(f"🔄 Trying free proxy list...")
    ip = fetch_proxy_free_proxy()
    if ip:
        print(f"✅ Got proxy from free list: {ip}")
        return ip
    
    # Try 3: Mock proxy (for testing)
    print(f"⚠️ Using mock proxy (testing mode)...")
    ip = fetch_proxy_mock()
    print(f"✅ Using mock proxy: {ip}")
    return ip

# ==================== HELPER FUNCTIONS ====================

def generate_license():
    prefix = "RIDOL"
    parts = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)]
    return f"{prefix}-{'-'.join(parts)}"

def validate_license(license_key):
    if not license_key: return None
    license_key = license_key.strip().upper()
    
    conn = get_db()
    if not conn: return None
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT * FROM licenses WHERE license_key = %s AND is_active = 1', (license_key,))
        result = c.fetchone()
        conn.close()
        
        if not result: return None
        
        if result['expires_at']:
            try:
                expires = datetime.fromisoformat(result['expires_at'])
                if expires < datetime.now(): return None
            except: pass
        return dict(result)
    except Exception as e:
        print(f"❌ validate_license error: {e}")
        return None

def deduct_credit(license_key):
    conn = get_db()
    if not conn: return False, 0
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT credits, used_credits, total_operations FROM licenses WHERE license_key = %s', (license_key,))
        result = c.fetchone()
        
        if not result or result['credits'] <= 0:
            conn.close()
            return False, result['credits'] if result else 0
        
        new_credits = result['credits'] - 1
        new_used = result['used_credits'] + 1
        new_total = (result['total_operations'] or 0) + 1
        
        c.execute('''
            UPDATE licenses 
            SET credits = %s, used_credits = %s, total_operations = %s, last_used = %s
            WHERE license_key = %s
        ''', (new_credits, new_used, new_total, datetime.now().isoformat(), license_key))
        
        conn.commit()
        conn.close()
        return True, new_credits
    except Exception as e:
        print(f"❌ deduct_credit error: {e}")
        return False, 0

# ==================== ADMIN TEMPLATE ====================

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ridol FB Tool - Admin Panel v8.5</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0e17; color: #e0e0e0; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 20px 30px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #2a3a5c; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
        .header h1 { font-size: 24px; background: linear-gradient(90deg, #f7971e, #ffd200); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: #1a1a2e; padding: 20px; border-radius: 10px; border: 1px solid #2a3a5c; text-align: center; }
        .stat-card .number { font-size: 28px; font-weight: bold; color: #f7971e; }
        .panel { background: #1a1a2e; border-radius: 12px; border: 1px solid #2a3a5c; padding: 20px; margin-bottom: 20px; }
        .form-group { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; align-items: center; }
        .form-group input { flex: 1; padding: 10px; background: #0d1117; border: 1px solid #2a3a5c; border-radius: 8px; color: #e0e0e0; }
        .btn { padding: 10px 25px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #f7971e, #ffd200); color: #1a1a2e; }
        .btn-success { background: #00c853; color: white; }
        .btn-danger { background: #ff1744; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #2a3a5c; font-size: 13px; }
        th { color: #f7971e; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; }
        .badge-active { background: #00c85320; color: #00c853; }
        .hidden { display: none; }
        .status-online { color: #00c853; }
        .status-offline { color: #ff1744; }
    </style>
</head>
<body>
    <div class="container">
        <div id="loginScreen" class="panel" style="max-width: 400px; margin: 100px auto;">
            <h2 style="text-align:center; color:#f7971e; margin-bottom:20px;">🔐 Admin Login</h2>
            <input type="password" id="adminPass" placeholder="Password" style="width:100%; padding:10px; margin-bottom:15px; background:#0d1117; border:1px solid #2a3a5c; color:white; border-radius:8px;">
            <button class="btn btn-primary" style="width:100%" onclick="adminLogin()">Login</button>
        </div>

        <div id="dashboardScreen" class="hidden">
            <div class="header">
                <h1>⚡ Ridol FB Tool Admin v8.5</h1>
                <div>
                    <span id="proxyStatus" style="margin-right:15px;">🔄 Proxy: Checking...</span>
                    <button class="btn btn-danger" onclick="adminLogout()">Logout</button>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card"><div class="number" id="totalLicenses">0</div><div>Licenses</div></div>
                <div class="stat-card"><div class="number" id="totalCredits">0</div><div>Credits</div></div>
                <div class="stat-card"><div class="number" id="totalLogs">0</div><div>Operations</div></div>
            </div>

            <div class="panel">
                <h2>📝 Create License</h2>
                <div class="form-group">
                    <input type="number" id="creditsInput" placeholder="Credits" value="100">
                    <input type="number" id="expiryDaysInput" placeholder="Days" value="30">
                    <input type="text" id="userIdInput" placeholder="User ID">
                    <button class="btn btn-success" onclick="createLicense()">Create</button>
                </div>
            </div>

            <div class="panel">
                <h2>📋 License List</h2>
                <div style="overflow-x:auto;">
                    <table>
                        <thead>
                            <tr><th>License Key</th><th>Credits</th><th>Used</th><th>User</th><th>Status</th><th>Action</th></tr>
                        </thead>
                        <tbody id="licenseTableBody"></tbody>
                    </table>
                </div>
            </div>

            <div class="panel">
                <h2>📊 Recent Logs</h2>
                <div style="overflow-x:auto;">
                    <table>
                        <thead>
                            <tr><th>License</th><th>Action</th><th>IP</th><th>Country</th><th>Time</th><th>Status</th></tr>
                        </thead>
                        <tbody id="logsTableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let token = localStorage.getItem('adminToken') || '';
        const headers = () => ({ 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token });

        function adminLogin() {
            const password = document.getElementById('adminPass').value;
            fetch('/admin/login', { method: 'POST', headers: headers(), body: JSON.stringify({ password }) })
            .then(r => r.json()).then(data => {
                if(data.success) { token = data.token; localStorage.setItem('adminToken', token); location.reload(); }
                else alert('Invalid Password');
            });
        }

        function adminLogout() { localStorage.removeItem('adminToken'); location.reload(); }

        function loadData() {
            if(!token) return;
            document.getElementById('loginScreen').classList.add('hidden');
            document.getElementById('dashboardScreen').classList.remove('hidden');

            fetch('/admin/stats', { headers: headers() }).then(r => r.json()).then(data => {
                document.getElementById('totalLicenses').textContent = data.stats.total_licenses;
                document.getElementById('totalCredits').textContent = data.stats.total_credits;
                document.getElementById('totalLogs').textContent = data.stats.total_logs;
            });

            fetch('/admin/list_licenses', { headers: headers() }).then(r => r.json()).then(data => {
                const tbody = document.getElementById('licenseTableBody');
                tbody.innerHTML = data.licenses.map(l => `
                    <tr>
                        <td>${l.license_key}</td>
                        <td style="color:#00c853">${l.credits}</td>
                        <td>${l.used_credits}</td>
                        <td>${l.user_id || '-'}</td>
                        <td><span class="badge badge-active">${l.is_active ? 'Active' : 'Revoked'}</span></td>
                        <td><button class="btn btn-danger" style="padding:4px 8px; font-size:10px;" onclick="revokeLicense('${l.license_key}')">Revoke</button></td>
                    </tr>
                `).join('');
            });

            fetch('/admin/logs', { headers: headers() }).then(r => r.json()).then(data => {
                const tbody = document.getElementById('logsTableBody');
                tbody.innerHTML = data.logs.map(l => `
                    <tr>
                        <td style="font-size:10px">${l.license_key ? l.license_key.substring(0,15) + '...' : '-'}</td>
                        <td>${l.action}</td>
                        <td>${l.ip_used}</td>
                        <td>${l.country}</td>
                        <td style="font-size:10px">${l.timestamp ? l.timestamp.substring(11,19) : '-'}</td>
                        <td><span class="${l.status === 'success' ? 'status-online' : 'status-offline'}">${l.status}</span></td>
                    </tr>
                `).join('');
            });

            // Check proxy status
            fetch('/admin/proxy_status', { headers: headers() }).then(r => r.json()).then(data => {
                document.getElementById('proxyStatus').innerHTML = data.available ? '✅ Proxy: Available' : '❌ Proxy: Unavailable';
            });
        }

        function createLicense() {
            const body = {
                credits: document.getElementById('creditsInput').value,
                expiry_days: document.getElementById('expiryDaysInput').value,
                user_id: document.getElementById('userIdInput').value
            };
            fetch('/admin/create_license', { method: 'POST', headers: headers(), body: JSON.stringify(body) })
            .then(r => r.json()).then(() => { alert('✅ Created!'); loadData(); });
        }

        function revokeLicense(key) {
            if(!confirm('Revoke ' + key + '?')) return;
            fetch('/admin/revoke_license', { method: 'POST', headers: headers(), body: JSON.stringify({ license_key: key }) })
            .then(() => loadData());
        }

        if(token) loadData();
    </script>
</body>
</html>
'''

# ==================== API ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        'status': 'online', 
        'database': 'PostgreSQL Connected', 
        'version': '8.5',
        'proxy_status': 'Check /admin/proxy_status'
    })

@app.route('/admin')
def admin_page():
    return render_template_string(ADMIN_TEMPLATE)

@app.route('/admin/proxy_status')
def proxy_status():
    """Check if proxy fetching is working"""
    ip = get_proxy_ip('Rand')
    return jsonify({'available': ip is not None, 'test_ip': ip})

@app.route('/api/license/verify', methods=['POST'])
@app.route('/api/verify', methods=['POST'])
def api_verify():
    data = request.get_json()
    license_key = data.get('license_key')
    license_data = validate_license(license_key)
    if not license_data:
        return jsonify({'valid': False, 'error': 'Invalid license'}), 401
    return jsonify({'valid': True, **license_data})

@app.route('/api/proxy/get', methods=['POST'])
@app.route('/api/get_ip', methods=['POST'])
def api_get_proxy():
    start_time = time.time()
    data = request.get_json()
    license_key = data.get('license_key', '').strip().upper()
    country = data.get('country', 'Rand').upper()
    
    print(f"📥 Proxy request: License={license_key[:10]}..., Country={country}")
    
    license_data = validate_license(license_key)
    if not license_data:
        print(f"❌ Invalid license: {license_key}")
        return jsonify({'success': False, 'error': 'Invalid license'}), 401
    
    if license_data['credits'] <= 0:
        print(f"❌ Insufficient credits: {license_data['credits']}")
        return jsonify({'success': False, 'error': 'Insufficient credits'}), 403
    
    # Get proxy IP with multiple fallbacks
    ip = get_proxy_ip(country)
    
    if not ip:
        print(f"❌ Could not fetch proxy for {country}")
        return jsonify({'success': False, 'error': 'No proxy available'}), 500
    
    # Deduct credit
    success, remaining = deduct_credit(license_key)
    
    if success:
        # Log usage
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute('''
                INSERT INTO usage_logs (license_key, action, ip_used, country, timestamp, user_id, status, response_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (license_key, 'get_proxy', ip, country, datetime.now().isoformat(), 
                  license_data.get('user_id'), 'success', int((time.time() - start_time) * 1000)))
            conn.commit()
            conn.close()
        except:
            pass
        
        print(f"✅ Proxy sent: {ip}, Remaining: {remaining}")
        return jsonify({
            'success': True, 
            'ip': ip, 
            'port': 3010, 
            'remaining_credits': remaining
        })
    else:
        print(f"❌ Credit deduction failed")
        return jsonify({'success': False, 'error': 'Credit deduction failed'}), 500

# ==================== ADMIN API ====================

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('password') == ADMIN_PASSWORD:
        return jsonify({'success': True, 'token': 'admin_token'})
    return jsonify({'success': False}), 401

@app.route('/admin/stats')
def admin_stats():
    if request.headers.get('Authorization') != 'Bearer admin_token': return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM licenses')
    l_count = c.fetchone()[0]
    c.execute('SELECT SUM(credits) FROM licenses')
    c_count = c.fetchone()[0] or 0
    c.execute('SELECT COUNT(*) FROM usage_logs')
    ops = c.fetchone()[0]
    conn.close()
    return jsonify({'success': True, 'stats': {'total_licenses': l_count, 'total_credits': c_count, 'total_logs': ops}})

@app.route('/admin/create_license', methods=['POST'])
def admin_create():
    if request.headers.get('Authorization') != 'Bearer admin_token': return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    key = generate_license()
    credits = int(data.get('credits', 100))
    expiry = (datetime.now() + timedelta(days=int(data.get('expiry_days', 30)))).isoformat()
    
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO licenses (license_key, credits, created_at, expires_at, user_id) VALUES (%s, %s, %s, %s, %s)',
              (key, credits, datetime.now().isoformat(), expiry, data.get('user_id')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'license_key': key})

@app.route('/admin/list_licenses')
def admin_list_lic():
    if request.headers.get('Authorization') != 'Bearer admin_token': return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute('SELECT * FROM licenses ORDER BY created_at DESC')
    res = c.fetchall()
    conn.close()
    return jsonify({'success': True, 'licenses': res})

@app.route('/admin/revoke_license', methods=['POST'])
def admin_revoke():
    if request.headers.get('Authorization') != 'Bearer admin_token': return jsonify({'error': 'Unauthorized'}), 401
    key = request.get_json().get('license_key')
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE licenses SET is_active = 0 WHERE license_key = %s', (key,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/logs')
def admin_logs():
    if request.headers.get('Authorization') != 'Bearer admin_token': return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute('SELECT * FROM usage_logs ORDER BY id DESC LIMIT 50')
    res = c.fetchall()
    conn.close()
    return jsonify({'success': True, 'logs': res})

if __name__ == '__main__':
    print("🚀 Starting Ridol FB Tool Server v8.5...")
    print(f"🔗 Database: {'Connected' if DATABASE_URL else 'Not Set'}")
    print(f"🌐 Proxy API: {'Configured' if CLIPROXY_API_URL else 'Using fallback'}")
    app.run(host='0.0.0.0', port=PORT)