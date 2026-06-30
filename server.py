#!/usr/bin/env python3
"""
Ridol FB Tool - Professional License Server v10.2
Backend: Flask, Database: PostgreSQL (Render.com Optimized)
Author: Ridol Islam
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
from datetime import datetime, timedelta
import time
import logging

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURATION ====================
CLIPROXY_API_URL = "https://api.cliproxy.io/white/api"
PORT = int(os.environ.get('PORT', 10000))
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Cliproxy Residential Proxy Credentials
CLIPROXY_USER = os.environ.get('CLIPROXY_USER', 'duov1209972')
CLIPROXY_PASS = os.environ.get('CLIPROXY_PASS', 'Ridol123')

# ==================== DATABASE FUNCTIONS ====================

def get_db():
    """PostgreSQL ডাটাবেস কানেকশন"""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def init_db():
    """টেবিল তৈরি করা (যদি না থাকে)"""
    conn = get_db()
    if not conn: 
        print("❌ Could not connect to database")
        return
    try:
        c = conn.cursor()
        
        # Licenses Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                credits INTEGER DEFAULT 100,
                max_browsers INTEGER DEFAULT 1,
                created_at TEXT,
                expires_at TEXT,
                is_active INTEGER DEFAULT 1,
                used_credits INTEGER DEFAULT 0,
                user_id TEXT DEFAULT 'User',
                total_operations INTEGER DEFAULT 0,
                last_used TEXT
            )
        ''')
        
        # Usage Logs Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                id SERIAL PRIMARY KEY,
                license_key TEXT,
                action TEXT,
                ip_used TEXT,
                port_used INTEGER,
                country TEXT,
                timestamp TEXT,
                user_id TEXT,
                status TEXT,
                response_time INTEGER
            )
        ''')
        
        # Proxy Cache Table
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
        
        conn.commit()
        c.close()
        conn.close()
        print("✅ Database Initialized Successfully!")
    except Exception as e:
        print(f"❌ Init DB Error: {e}")

# অ্যাপ স্টার্ট হলে ডাটাবেস চেক করবে
with app.app_context():
    init_db()

# ==================== HELPERS ====================

def generate_key():
    """Generate unique license key"""
    prefix = "RIDOL"
    parts = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)]
    return f"{prefix}-{'-'.join(parts)}"

def validate_license(key):
    """Validate license and return details"""
    if not key: 
        return None
    key = key.upper()
    conn = get_db()
    if not conn:
        return None
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('''
            SELECT * FROM licenses 
            WHERE license_key = %s AND is_active = 1
        ''', (key,))
        res = c.fetchone()
        conn.close()
        
        if not res:
            return None
        
        # Check expiry
        if res.get('expires_at'):
            try:
                if datetime.fromisoformat(res['expires_at']) < datetime.now():
                    return None
            except:
                pass
        
        return res
    except Exception as e:
        print(f"❌ Validate error: {e}")
        return None

def deduct_credit(key):
    """Deduct 1 credit from license"""
    conn = get_db()
    if not conn:
        return False, 0
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT credits FROM licenses WHERE license_key = %s AND is_active = 1', (key,))
        res = c.fetchone()
        
        if not res or res['credits'] <= 0:
            conn.close()
            return False, 0
        
        new_credits = res['credits'] - 1
        c.execute('''
            UPDATE licenses 
            SET credits = %s, used_credits = used_credits + 1, 
                total_operations = total_operations + 1, last_used = %s
            WHERE license_key = %s
        ''', (new_credits, datetime.now().isoformat(), key))
        conn.commit()
        conn.close()
        return True, new_credits
    except Exception as e:
        print(f"❌ Deduct error: {e}")
        conn.close()
        return False, 0

def log_usage(license_key, action, ip, port, country, user_id, status, response_time):
    """Log API usage"""
    conn = get_db()
    if not conn:
        return
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO usage_logs 
            (license_key, action, ip_used, port_used, country, timestamp, user_id, status, response_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (license_key, action, ip, port, country, datetime.now().isoformat(), 
              user_id, status, response_time))
        conn.commit()
        conn.close()
    except:
        pass

# ==================== ADMIN PANEL UI ====================

ADMIN_UI = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ridol Admin Panel v10.2</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            background: #0a0e17; 
            color: #e0e0e0;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid #2a3a5c;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .header h1 { font-size: 24px; background: linear-gradient(90deg, #f7971e, #ffd200); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header .subtitle { color: #8899aa; font-size: 14px; }
        .box {
            background: #1a1a2e;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #2a3a5c;
            margin-bottom: 20px;
        }
        .box h2 { color: #f7971e; margin-bottom: 15px; font-size: 18px; border-bottom: 1px solid #2a3a5c; padding-bottom: 10px; }
        .form-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 10px;
            align-items: center;
        }
        .form-group label { min-width: 120px; color: #8899aa; }
        .form-group input {
            flex: 1;
            min-width: 200px;
            padding: 10px 15px;
            background: #0d1117;
            border: 1px solid #2a3a5c;
            border-radius: 8px;
            color: #e0e0e0;
            font-size: 14px;
            outline: none;
        }
        .form-group input:focus { border-color: #f7971e; }
        .btn {
            padding: 10px 25px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            color: white;
        }
        .btn-create { background: #00c853; }
        .btn-create:hover { background: #00e676; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { padding: 12px 15px; border-bottom: 1px solid #2a3a5c; text-align: left; }
        th { color: #f7971e; font-weight: bold; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        tr:hover { background: #0d1117; }
        .badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }
        .badge-active { background: #00c85320; color: #00c853; }
        code { background: #0d1117; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #f7971e; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #1a1a2e;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #2a3a5c;
            text-align: center;
        }
        .stat-card .number { font-size: 24px; font-weight: bold; color: #f7971e; }
        .stat-card .label { font-size: 11px; color: #8899aa; margin-top: 5px; }
        .copy-btn {
            background: #2a3a5c;
            border: none;
            color: #e0e0e0;
            padding: 2px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            margin-left: 5px;
        }
        .copy-btn:hover { background: #3a4a6c; }
        @media (max-width: 768px) {
            .header { flex-direction: column; text-align: center; gap: 10px; }
            .form-group { flex-direction: column; align-items: stretch; }
            .form-group label { min-width: auto; }
            table { font-size: 11px; }
            th, td { padding: 8px 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>⚡ Ridol FB Tool Admin</h1>
                <div class="subtitle">License & Credit Management System v10.2</div>
            </div>
            <div style="display:flex; gap:15px; align-items:center; flex-wrap:wrap;">
                <span style="padding:8px 16px; border-radius:20px; font-size:12px; font-weight:bold; background:#00c85320; color:#00c853; border:1px solid #00c85340;">● Server Online</span>
                <span id="serverTime" style="font-size:12px; color:#8899aa;"></span>
            </div>
        </div>

        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card"><div class="number">{{ total_licenses }}</div><div class="label">Total Licenses</div></div>
            <div class="stat-card"><div class="number">{{ total_credits }}</div><div class="label">Total Credits</div></div>
            <div class="stat-card"><div class="number">{{ active_users }}</div><div class="label">Active Users</div></div>
            <div class="stat-card"><div class="number">{{ total_logs }}</div><div class="label">Total Operations</div></div>
        </div>

        <!-- Create License -->
        <div class="box">
            <h2>📝 Create New License</h2>
            <form action="/admin/create" method="POST">
                <div class="form-group">
                    <label>Admin Password</label>
                    <input type="password" name="password" placeholder="Enter admin password" required>
                </div>
                <div class="form-group">
                    <label>Credits</label>
                    <input type="number" name="credits" value="100" min="1">
                </div>
                <div class="form-group">
                    <label>Max Browsers</label>
                    <input type="number" name="max_browsers" value="1" min="1">
                </div>
                <div class="form-group">
                    <label>Expiry (days)</label>
                    <input type="number" name="expiry_days" value="30" min="1">
                </div>
                <div class="form-group">
                    <label>User ID</label>
                    <input type="text" name="user_id" placeholder="Optional user identifier" value="User">
                </div>
                <button class="btn btn-create" type="submit">🚀 Create License</button>
            </form>
        </div>

        <!-- License List -->
        <div class="box">
            <h2>📋 License List</h2>
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>License Key</th>
                            <th>Credits</th>
                            <th>Used</th>
                            <th>Total Ops</th>
                            <th>Max Browsers</th>
                            <th>User ID</th>
                            <th>Status</th>
                            <th>Expires</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for l in licenses %}
                        <tr>
                            <td>
                                <code>{{ l.license_key }}</code>
                                <button class="copy-btn" onclick="copyKey('{{ l.license_key }}')">📋</button>
                            </td>
                            <td style="color:#00c853;font-weight:bold;">{{ l.credits }}</td>
                            <td style="color:#8899aa;">{{ l.used_credits or 0 }}</td>
                            <td style="color:#2979ff;">{{ l.total_operations or 0 }}</td>
                            <td>{{ l.max_browsers or 1 }}</td>
                            <td style="font-size:11px;">{{ l.user_id or '-' }}</td>
                            <td><span class="badge badge-active">Active</span></td>
                            <td style="font-size:11px;">{{ l.expires_at[:10] if l.expires_at else 'N/A' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function copyKey(key) {
            navigator.clipboard.writeText(key);
            alert('License key copied: ' + key);
        }
        
        function updateTime() {
            document.getElementById('serverTime').textContent = new Date().toLocaleString();
        }
        setInterval(updateTime, 1000);
        updateTime();
    </script>
</body>
</html>
'''

# ==================== API ROUTES ====================

@app.route('/')
def home():
    """Health check"""
    return jsonify({
        'status': 'online', 
        'service': 'Ridol FB Tool License Server',
        'version': '10.2',
        'database': 'connected',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/admin')
def admin_page():
    """Admin Panel"""
    conn = get_db()
    if not conn:
        return "Database not connected", 500
    
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT * FROM licenses ORDER BY created_at DESC')
        lics = c.fetchall()
        
        # Stats
        c.execute('SELECT COUNT(*) FROM licenses')
        total_licenses = c.fetchone()['count']
        
        c.execute('SELECT SUM(credits) FROM licenses WHERE is_active = 1')
        total_credits = c.fetchone()['sum'] or 0
        
        c.execute('SELECT COUNT(*) FROM licenses WHERE is_active = 1')
        active_users = c.fetchone()['count']
        
        c.execute('SELECT COUNT(*) FROM usage_logs')
        total_logs = c.fetchone()['count']
        
        conn.close()
        
        return render_template_string(ADMIN_UI, 
            licenses=lics,
            total_licenses=total_licenses,
            total_credits=total_credits,
            active_users=active_users,
            total_logs=total_logs
        )
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/admin/create', methods=['POST'])
def admin_create():
    """Create new license"""
    try:
        password = request.form.get('password')
        if password != ADMIN_PASSWORD:
            return "Wrong Password", 403
        
        key = generate_key()
        credits = int(request.form.get('credits', 100))
        max_browsers = int(request.form.get('max_browsers', 1))
        expiry_days = int(request.form.get('expiry_days', 30))
        user_id = request.form.get('user_id', 'User')
        
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        conn = get_db()
        if not conn:
            return "Database error", 500
        
        c = conn.cursor()
        c.execute('''
            INSERT INTO licenses (license_key, credits, max_browsers, created_at, expires_at, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (key, credits, max_browsers, created_at, expires_at, user_id))
        conn.commit()
        conn.close()
        
        return f"""
        <html>
        <body style="background:#0a0e17;color:white;font-family:sans-serif;padding:40px;text-align:center;">
            <h1 style="color:#00c853;">✅ License Created!</h1>
            <p style="font-size:20px;color:#f7971e;">{key}</p>
            <p>Credits: {credits} | User: {user_id} | Expires: {expires_at[:10]}</p>
            <a href="/admin" style="color:#f7971e;">⬅️ Back to Admin Panel</a>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {e}", 500

# ==================== USER API ====================

@app.route('/api/license/verify', methods=['POST'])
def api_verify_license():
    """Verify license and get user info"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'valid': False, 'error': 'No data provided'}), 400
        
        license_key = data.get('license_key', '').strip().upper()
        
        if not license_key:
            return jsonify({'valid': False, 'error': 'License key required'}), 400
        
        license_data = validate_license(license_key)
        
        if not license_data:
            return jsonify({'valid': False, 'error': 'Invalid or expired license'}), 401
        
        return jsonify({
            'valid': True,
            'credits': license_data['credits'],
            'max_browsers': license_data['max_browsers'],
            'expires_at': license_data['expires_at'],
            'used_credits': license_data['used_credits'],
            'total_operations': license_data.get('total_operations', 0),
            'user_id': license_data.get('user_id', '')
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

@app.route('/api/proxy/get', methods=['POST'])
def api_get_proxy():
    """
    Get Residential Proxy from Cliproxy API
    Cliproxy Residential Format:
    - IP: us2.cliproxy.io
    - Port: 3010
    - User: duov1209972-region-Rand-sid-XXXX
    - Pass: Ridol123
    
    Request: {"license_key": "RIDOL-XXXX", "country": "BD"}
    Response: {"success": true, "ip": "us2.cliproxy.io", "port": 3010, 
               "user": "duov1209972-region-Rand-sid-1234", "pass": "Ridol123",
               "remaining_credits": 999}
    """
    start_time = time.time()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        license_key = data.get('license_key', '').strip().upper()
        country = data.get('country', 'Rand')
        
        if not license_key:
            return jsonify({'success': False, 'error': 'License key required'}), 400
        
        # Validate license
        license_data = validate_license(license_key)
        if not license_data:
            return jsonify({'success': False, 'error': 'Invalid or expired license'}), 401
        
        # Check credits
        if license_data['credits'] <= 0:
            return jsonify({
                'success': False,
                'error': 'Insufficient credits',
                'credits': 0
            }), 403
        
        # Deduct credit
        success, remaining = deduct_credit(license_key)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to deduct credit'
            }), 500
        
        # Cliproxy Residential Proxy Configuration
        # Cliproxy Residential Proxy Format: 
        # user: duov1209972-region-{country}-sid-{random}
        # pass: Ridol123
        # host: {country}.cliproxy.io or us2.cliproxy.io
        
        # দেশ অনুযায়ী Subdomain
        country_sub = country.lower()
        if country_sub == 'us':
            host = "us2.cliproxy.io"
        elif country_sub == 'bd':
            host = "bd.cliproxy.io"
        elif country_sub == 'uk':
            host = "uk.cliproxy.io"
        elif country_sub == 'in':
            host = "in.cliproxy.io"
        else:
            host = "us2.cliproxy.io"  # Default
        
        # Random SID
        sid = random.randint(1000, 9999)
        
        # User format: duov1209972-region-{country}-sid-{sid}
        proxy_user = f"duov1209972-region-{country}-sid-{sid}"
        proxy_pass = "Ridol123"
        proxy_port = 3010
        
        # Log usage
        log_usage(
            license_key, 'proxy_fetch', host, proxy_port, country,
            license_data.get('user_id', ''), 'success',
            int((time.time() - start_time) * 1000)
        )
        
        return jsonify({
            'success': True,
            'ip': host,
            'port': proxy_port,
            'user': proxy_user,
            'pass': proxy_pass,
            'country': country,
            'remaining_credits': remaining
        })
        
    except Exception as e:
        print(f"[-] Proxy error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/license/status', methods=['POST'])
def api_get_status():
    """Get license status without deducting credit"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'valid': False, 'error': 'No data provided'}), 400
        
        license_key = data.get('license_key', '').strip().upper()
        
        if not license_key:
            return jsonify({'valid': False, 'error': 'License key required'}), 400
        
        license_data = validate_license(license_key)
        
        if not license_data:
            return jsonify({'valid': False, 'error': 'Invalid license'}), 401
        
        return jsonify({
            'valid': True,
            'credits': license_data['credits'],
            'max_browsers': license_data['max_browsers'],
            'used_credits': license_data['used_credits'],
            'total_operations': license_data.get('total_operations', 0),
            'expires_at': license_data['expires_at'],
            'user_id': license_data.get('user_id', '')
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("="*60)
    print("🚀 RIDOL FB TOOL - LICENSE SERVER v10.2")
    print("="*60)
    print(f"✅ Database: PostgreSQL")
    print(f"🔐 Admin Password: {ADMIN_PASSWORD}")
    print(f"📡 Port: {PORT}")
    print("="*60)
    print("🌐 Admin Panel: https://your-app.onrender.com/admin")
    print("="*60)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)