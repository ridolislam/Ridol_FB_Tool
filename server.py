#!/usr/bin/env python3
"""
Ridol FB Tool - License Server v9.0
Render.com Deployment Ready
Complete License & Credit Management System
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import logging
import os
import re
import json
import random
import string
import sqlite3
from datetime import datetime, timedelta
import time

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURATION ====================
CLIPROXY_API_URL = "https://api.cliproxy.io/white/api"
PORT = int(os.environ.get('PORT', 10000))
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
DB_PATH = 'licenses.db'

# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Licenses table
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
    
    try:
        c.execute('SELECT total_operations FROM licenses LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE licenses ADD COLUMN total_operations INTEGER DEFAULT 0')
    
    # Usage logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    
    # Proxy cache table
    c.execute('''
        CREATE TABLE IF NOT EXISTS proxy_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proxy_ip TEXT,
            proxy_port INTEGER,
            country TEXT,
            fetched_at TEXT,
            is_active INTEGER DEFAULT 1,
            used_count INTEGER DEFAULT 0,
            last_used TEXT
        )
    ''')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_license_key ON licenses(license_key)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_logs_license ON usage_logs(license_key)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_logs_time ON usage_logs(timestamp)')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== LICENSE FUNCTIONS ====================

def generate_license():
    """Generate a unique license key"""
    prefix = "RIDOL"
    parts = []
    for _ in range(4):
        part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        parts.append(part)
    return f"{prefix}-{'-'.join(parts)}"

def validate_license(license_key):
    """Check if license is valid and return details"""
    if not license_key:
        return None
    
    license_key = license_key.strip().upper()
    
    if not re.match(r'^RIDOL-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$', license_key):
        return None
    
    conn = get_db()
    if not conn:
        return None
    
    try:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM licenses 
            WHERE license_key = ? AND is_active = 1
        ''', (license_key,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return None
        
        if result['expires_at']:
            try:
                expires = datetime.fromisoformat(result['expires_at'])
                if expires < datetime.now():
                    return None
            except:
                pass
        
        return dict(result)
    except Exception as e:
        print(f"❌ validate_license error: {e}")
        return None

def deduct_credit(license_key):
    """Deduct 1 credit for each operation"""
    conn = get_db()
    if not conn:
        return False, 0
    
    try:
        c = conn.cursor()
        c.execute('SELECT credits, used_credits, total_operations FROM licenses WHERE license_key = ?', (license_key,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return False, 0
        
        if result['credits'] <= 0:
            conn.close()
            return False, result['credits']
        
        new_credits = result['credits'] - 1
        new_used = result['used_credits'] + 1
        new_total = result['total_operations'] + 1
        
        c.execute('''
            UPDATE licenses 
            SET credits = ?, used_credits = ?, total_operations = ?, last_used = ?
            WHERE license_key = ?
        ''', (new_credits, new_used, new_total, datetime.now().isoformat(), license_key))
        
        conn.commit()
        conn.close()
        return True, new_credits
    except Exception as e:
        print(f"❌ deduct_credit error: {e}")
        return False, 0

# ==================== ADMIN HTML TEMPLATE ====================

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ridol FB Tool - Admin Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e17;
            color: #e0e0e0;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
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
        .header .status { padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: bold; background: #00c85320; color: #00c853; border: 1px solid #00c85340; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #1a1a2e;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #2a3a5c;
            text-align: center;
        }
        .stat-card .number { font-size: 28px; font-weight: bold; color: #f7971e; }
        .stat-card .label { font-size: 12px; color: #8899aa; margin-top: 5px; }
        .panel {
            background: #1a1a2e;
            border-radius: 12px;
            border: 1px solid #2a3a5c;
            padding: 20px;
            margin-bottom: 20px;
        }
        .panel h2 { font-size: 18px; margin-bottom: 15px; color: #f7971e; border-bottom: 1px solid #2a3a5c; padding-bottom: 10px; }
        .form-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
            align-items: center;
        }
        .form-group label { min-width: 120px; color: #8899aa; font-size: 14px; }
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
            transition: border 0.3s;
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
        .btn-primary { background: linear-gradient(135deg, #f7971e, #ffd200); color: #1a1a2e; }
        .btn-primary:hover { transform: scale(1.02); opacity: 0.9; }
        .btn-success { background: #00c853; }
        .btn-success:hover { background: #00e676; }
        .btn-danger { background: #ff1744; }
        .btn-danger:hover { background: #ff5252; }
        .btn-info { background: #2979ff; }
        .btn-info:hover { background: #448aff; }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #2a3a5c;
        }
        th { color: #f7971e; font-weight: bold; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        tr:hover { background: #0d1117; }
        .badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }
        .badge-active { background: #00c85320; color: #00c853; }
        .badge-inactive { background: #ff174420; color: #ff1744; }
        .badge-expired { background: #ff910020; color: #ff9100; }
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            background: #1a1a2e;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid #2a3a5c;
        }
        .login-container h2 { text-align: center; margin-bottom: 30px; color: #f7971e; }
        .login-container input { width: 100%; margin-bottom: 15px; }
        .login-container .btn { width: 100%; }
        .alert {
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .alert-success { background: #00c85320; border: 1px solid #00c85340; color: #00c853; }
        .alert-error { background: #ff174420; border: 1px solid #ff174440; color: #ff1744; }
        .alert-info { background: #2979ff20; border: 1px solid #2979ff40; color: #2979ff; }
        .hidden { display: none; }
        .copy-btn {
            background: #2a3a5c;
            border: none;
            color: #e0e0e0;
            padding: 2px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
        }
        .copy-btn:hover { background: #3a4a6c; }
        @media (max-width: 768px) {
            .header { flex-direction: column; text-align: center; gap: 10px; }
            .form-group { flex-direction: column; align-items: stretch; }
            .form-group label { min-width: auto; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            table { font-size: 11px; }
            th, td { padding: 8px 10px; }
        }
        .db-status {
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            background: #00c85320;
            border: 1px solid #00c85340;
            color: #00c853;
        }
    </style>
</head>
<body>
    <div class="container" id="app">
        <!-- Login Screen -->
        <div id="loginScreen" class="login-container">
            <h2>🔐 Admin Login</h2>
            <div id="loginAlert" class="alert hidden"></div>
            <input type="password" id="adminPass" placeholder="Enter Admin Password" onkeydown="if(event.key==='Enter') adminLogin()">
            <button class="btn btn-primary" onclick="adminLogin()">Login</button>
            <p style="text-align:center;margin-top:15px;color:#8899aa;font-size:12px;">Default: admin123</p>
        </div>

        <!-- Dashboard -->
        <div id="dashboardScreen" class="hidden">
            <div class="header">
                <div>
                    <h1>⚡ Ridol FB Tool Admin</h1>
                    <div class="subtitle">License & Credit Management System</div>
                </div>
                <div style="display:flex; gap:15px; align-items:center; flex-wrap:wrap;">
                    <span class="status">● Server Online</span>
                    <span id="serverTime" style="font-size:12px; color:#8899aa;"></span>
                    <button class="btn btn-danger" onclick="adminLogout()" style="padding:6px 15px; font-size:12px;">Logout</button>
                </div>
            </div>

            <!-- Database Status -->
            <div id="dbStatus" class="db-status">✅ Database Connected</div>

            <!-- Stats -->
            <div class="stats-grid">
                <div class="stat-card"><div class="number" id="totalLicenses">0</div><div class="label">Total Licenses</div></div>
                <div class="stat-card"><div class="number" id="totalCredits">0</div><div class="label">Total Credits</div></div>
                <div class="stat-card"><div class="number" id="totalUsers">0</div><div class="label">Active Users</div></div>
                <div class="stat-card"><div class="number" id="totalLogs">0</div><div class="label">Total Operations</div></div>
            </div>

            <!-- Create License -->
            <div class="panel">
                <h2>📝 Create New License</h2>
                <div id="createAlert" class="alert hidden"></div>
                <div class="form-group">
                    <label>Credits</label>
                    <input type="number" id="creditsInput" value="100" min="1">
                </div>
                <div class="form-group">
                    <label>Max Browsers</label>
                    <input type="number" id="maxBrowsersInput" value="1" min="1">
                </div>
                <div class="form-group">
                    <label>Expiry (days)</label>
                    <input type="number" id="expiryDaysInput" value="30" min="1">
                </div>
                <div class="form-group">
                    <label>User ID</label>
                    <input type="text" id="userIdInput" placeholder="Optional user identifier">
                </div>
                <button class="btn btn-success" onclick="createLicense()">➕ Create License</button>
            </div>

            <!-- Add Credits -->
            <div class="panel">
                <h2>💰 Add Credits to License</h2>
                <div id="addAlert" class="alert hidden"></div>
                <div class="form-group">
                    <label>License Key</label>
                    <input type="text" id="addLicenseKey" placeholder="RIDOL-XXXX-XXXX-XXXX-XXXX">
                </div>
                <div class="form-group">
                    <label>Credits to Add</label>
                    <input type="number" id="addCreditsInput" value="100" min="1">
                </div>
                <button class="btn btn-info" onclick="addCredits()">➕ Add Credits</button>
            </div>

            <!-- License List -->
            <div class="panel">
                <h2>📋 License List <button class="btn btn-secondary" onclick="loadLicenses()" style="padding:4px 12px;font-size:12px;background:#2a3a5c;">🔄 Refresh</button></h2>
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
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="licenseTableBody">
                            <tr><td colspan="9" style="text-align:center; color:#8899aa;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Usage Logs -->
            <div class="panel">
                <h2>📊 Usage Logs <button class="btn btn-secondary" onclick="loadLogs()" style="padding:4px 12px;font-size:12px;background:#2a3a5c;">🔄 Refresh</button></h2>
                <div style="overflow-x:auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>License</th>
                                <th>Action</th>
                                <th>IP Used</th>
                                <th>Country</th>
                                <th>User ID</th>
                                <th>Status</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody id="logsTableBody">
                            <tr><td colspan="7" style="text-align:center; color:#8899aa;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let token = localStorage.getItem('adminToken') || '';

        function showAlert(id, message, type) {
            const el = document.getElementById(id);
            el.className = `alert alert-${type}`;
            el.textContent = message;
            el.classList.remove('hidden');
            setTimeout(() => el.classList.add('hidden'), 5000);
        }

        function formatDate(iso) {
            if (!iso) return 'N/A';
            try { return new Date(iso).toLocaleString(); } catch { return iso; }
        }

        function getStatusBadge(license) {
            if (!license.is_active) return '<span class="badge badge-inactive">Inactive</span>';
            if (license.expires_at) {
                const exp = new Date(license.expires_at);
                if (exp < new Date()) return '<span class="badge badge-expired">Expired</span>';
            }
            return '<span class="badge badge-active">Active</span>';
        }

        function copyKey(key) {
            navigator.clipboard.writeText(key);
            alert('License key copied: ' + key);
        }

        function adminLogin() {
            const pass = document.getElementById('adminPass').value;
            if (!pass) { showAlert('loginAlert', 'Please enter password', 'error'); return; }

            fetch('/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pass })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    token = data.token;
                    localStorage.setItem('adminToken', token);
                    showDashboard();
                } else {
                    showAlert('loginAlert', 'Invalid password', 'error');
                }
            })
            .catch(() => showAlert('loginAlert', 'Server error', 'error'));
        }

        function adminLogout() {
            token = '';
            localStorage.removeItem('adminToken');
            document.getElementById('dashboardScreen').classList.add('hidden');
            document.getElementById('loginScreen').classList.remove('hidden');
        }

        function showDashboard() {
            document.getElementById('loginScreen').classList.add('hidden');
            document.getElementById('dashboardScreen').classList.remove('hidden');
            loadStats();
            loadLicenses();
            loadLogs();
            setInterval(updateTime, 1000);
        }

        function updateTime() {
            document.getElementById('serverTime').textContent = new Date().toLocaleString();
        }

        function apiCall(endpoint, method, data) {
            return fetch(endpoint, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                },
                body: data ? JSON.stringify(data) : undefined
            }).then(r => r.json());
        }

        function loadStats() {
            apiCall('/admin/stats', 'GET')
                .then(data => {
                    if (data.success) {
                        document.getElementById('totalLicenses').textContent = data.stats.total_licenses || 0;
                        document.getElementById('totalCredits').textContent = data.stats.total_credits || 0;
                        document.getElementById('totalUsers').textContent = data.stats.active_users || 0;
                        document.getElementById('totalLogs').textContent = data.stats.total_logs || 0;
                    }
                })
                .catch(() => {});
        }

        function loadLicenses() {
            apiCall('/admin/list_licenses', 'GET')
                .then(data => {
                    const tbody = document.getElementById('licenseTableBody');
                    if (data.success && data.licenses && data.licenses.length) {
                        tbody.innerHTML = data.licenses.map(l => `
                            <tr>
                                <td><span style="font-family:monospace;font-size:12px;">${l.license_key}</span>
                                    <button class="copy-btn" onclick="copyKey('${l.license_key}')">📋</button>
                                </td>
                                <td style="color:#00c853;font-weight:bold;">${l.credits}</td>
                                <td style="color:#8899aa;">${l.used_credits || 0}</td>
                                <td style="color:#2979ff;">${l.total_operations || 0}</td>
                                <td>${l.max_browsers || 1}</td>
                                <td style="font-size:11px;">${l.user_id || '-'}</td>
                                <td>${getStatusBadge(l)}</td>
                                <td style="font-size:11px;">${formatDate(l.expires_at)}</td>
                                <td>
                                    <button class="btn btn-danger" style="padding:4px 10px;font-size:11px;" onclick="revokeLicense('${l.license_key}')">Revoke</button>
                                </td>
                            </tr>
                        `).join('');
                    } else {
                        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#8899aa;">No licenses found</td></tr>';
                    }
                })
                .catch(() => {});
        }

        function loadLogs() {
            apiCall('/admin/logs?limit=50', 'GET')
                .then(data => {
                    const tbody = document.getElementById('logsTableBody');
                    if (data.success && data.logs && data.logs.length) {
                        tbody.innerHTML = data.logs.map(l => `
                            <tr>
                                <td style="font-family:monospace;font-size:11px;">${l.license_key ? l.license_key.substring(0,20)+'...' : '-'}</td>
                                <td>${l.action || '-'}</td>
                                <td style="font-family:monospace;font-size:12px;">${l.ip_used || '-'}</td>
                                <td>${l.country || '-'}</td>
                                <td style="font-size:11px;">${l.user_id || '-'}</td>
                                <td>${l.status || 'Success'}</td>
                                <td style="font-size:11px;">${formatDate(l.timestamp)}</td>
                            </tr>
                        `).join('');
                    } else {
                        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#8899aa;">No logs found</td></tr>';
                    }
                })
                .catch(() => {});
        }

        function createLicense() {
            const credits = parseInt(document.getElementById('creditsInput').value);
            const max_browsers = parseInt(document.getElementById('maxBrowsersInput').value);
            const expiry_days = parseInt(document.getElementById('expiryDaysInput').value);
            const user_id = document.getElementById('userIdInput').value.trim();

            if (!credits || credits < 1) { showAlert('createAlert', 'Enter valid credits', 'error'); return; }

            apiCall('/admin/create_license', 'POST', { credits, max_browsers, expiry_days, user_id })
                .then(data => {
                    if (data.success) {
                        showAlert('createAlert', `✅ License created: ${data.license_key} (${data.credits} credits)`, 'success');
                        loadLicenses();
                        loadStats();
                        document.getElementById('userIdInput').value = '';
                    } else {
                        showAlert('createAlert', '❌ ' + (data.error || 'Failed to create license'), 'error');
                    }
                })
                .catch(() => showAlert('createAlert', 'Server error', 'error'));
        }

        function addCredits() {
            const license_key = document.getElementById('addLicenseKey').value.trim().toUpperCase();
            const credits = parseInt(document.getElementById('addCreditsInput').value);

            if (!license_key) { showAlert('addAlert', 'Enter license key', 'error'); return; }
            if (!credits || credits < 1) { showAlert('addAlert', 'Enter valid credits', 'error'); return; }

            apiCall('/admin/add_credits', 'POST', { license_key, credits })
                .then(data => {
                    if (data.success) {
                        showAlert('addAlert', `✅ Added ${data.added_credits} credits`, 'success');
                        loadLicenses();
                        loadStats();
                        document.getElementById('addLicenseKey').value = '';
                    } else {
                        showAlert('addAlert', '❌ ' + (data.error || 'Failed to add credits'), 'error');
                    }
                })
                .catch(() => showAlert('addAlert', 'Server error', 'error'));
        }

        function revokeLicense(license_key) {
            if (!confirm(`Revoke license ${license_key}?`)) return;

            apiCall('/admin/revoke_license', 'POST', { license_key })
                .then(data => {
                    if (data.success) {
                        showAlert('createAlert', `✅ License ${license_key} revoked`, 'info');
                        loadLicenses();
                        loadStats();
                    } else {
                        showAlert('createAlert', '❌ ' + (data.error || 'Failed to revoke'), 'error');
                    }
                })
                .catch(() => showAlert('createAlert', 'Server error', 'error'));
        }

        // Auto-login check
        if (token) {
            fetch('/admin/stats', {
                headers: { 'Authorization': 'Bearer ' + token }
            })
            .then(r => {
                if (r.status === 401) {
                    localStorage.removeItem('adminToken');
                    token = '';
                    return;
                }
                return r.json();
            })
            .then(data => {
                if (data && data.success) {
                    showDashboard();
                }
            })
            .catch(() => {});
        }

        // Refresh data periodically
        setInterval(() => {
            if (token) {
                loadStats();
                loadLicenses();
                loadLogs();
            }
        }, 30000);
    </script>
</body>
</html>
'''

# ==================== API ROUTES ====================

@app.route('/', methods=['GET'])
def home():
    """Health check"""
    db_exists = os.path.exists(DB_PATH)
    return jsonify({
        'status': 'online',
        'service': 'Ridol FB Tool License Server',
        'version': '9.0',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db_exists else 'not_initialized'
    })

@app.route('/admin', methods=['GET'])
def admin_panel():
    """Admin panel HTML"""
    return render_template_string(ADMIN_TEMPLATE)

# ==================== USER API ====================

@app.route('/api/license/verify', methods=['POST'])
def api_verify_license():
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
    Get IP from Cliproxy API and deduct credit
    Request: {"license_key": "RIDOL-XXXX-XXXX-XXXX-XXXX", "country": "BD"}
    Response: {"success": true, "ip": "103.xxx.xxx.xxx", "port": random_port, "remaining_credits": 999}
    """
    start_time = time.time()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        license_key = data.get('license_key', '').strip().upper()
        country = data.get('country', 'Rand').upper()
        
        if not license_key:
            return jsonify({'success': False, 'error': 'License key required'}), 400
        
        license_data = validate_license(license_key)
        if not license_data:
            return jsonify({'success': False, 'error': 'Invalid or expired license'}), 401
        
        if license_data['credits'] <= 0:
            return jsonify({
                'success': False,
                'error': 'Insufficient credits',
                'credits': 0
            }), 403
        
        # Fetch from Cliproxy
        api_url = f"{CLIPROXY_API_URL}?region={country}&num=1&time=10&format=n&type=txt"
        response = requests.get(api_url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Cliproxy API error: {response.status_code}'
            }), 500
        
        ip = response.text.strip()
        
        # Validate IP
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, ip):
            return jsonify({
                'success': False,
                'error': f'Invalid IP from Cliproxy: {ip}'
            }), 500
        
        # ============ FIX: Generate Random Port ============
        # Cliproxy থেকে Port না আসায় Random Port জেনারেট করুন
        port = random.randint(3000, 5000)
        # ==================================================
        
        # Deduct credit
        success, remaining = deduct_credit(license_key)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to deduct credit'
            }), 500
        
        # Log usage
        conn = get_db()
        if conn:
            try:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO usage_logs (license_key, action, ip_used, country, timestamp, user_id, status, response_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (license_key, 'get_proxy', ip, country, datetime.now().isoformat(),
                      license_data.get('user_id', ''), 'success', int((time.time() - start_time) * 1000)))
                conn.commit()
            except:
                pass
            finally:
                conn.close()
        
        return jsonify({
            'success': True,
            'ip': ip,
            'port': port,
            'country': country,
            'remaining_credits': remaining
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/license/status', methods=['POST'])
def api_get_status():
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

# ==================== ADMIN API ====================

@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if password == ADMIN_PASSWORD:
            return jsonify({'success': True, 'token': 'admin_token'})
        return jsonify({'success': False}), 401
    except:
        return jsonify({'success': False}), 401

@app.route('/admin/stats', methods=['GET'])
def admin_stats():
    try:
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM licenses')
        total_licenses = c.fetchone()[0]
        
        c.execute('SELECT SUM(credits) FROM licenses WHERE is_active = 1')
        total_credits = c.fetchone()[0] or 0
        
        c.execute('SELECT COUNT(*) FROM licenses WHERE is_active = 1')
        active_users = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM usage_logs')
        total_logs = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_licenses': total_licenses,
                'total_credits': total_credits,
                'active_users': active_users,
                'total_logs': total_logs
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/create_license', methods=['POST'])
def admin_create_license():
    try:
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        credits = int(data.get('credits', 100))
        max_browsers = int(data.get('max_browsers', 1))
        expiry_days = int(data.get('expiry_days', 30))
        user_id = data.get('user_id', '').strip()
        
        license_key = generate_license()
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        c = conn.cursor()
        c.execute('''
            INSERT INTO licenses (license_key, credits, max_browsers, created_at, expires_at, is_active, user_id)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', (license_key, credits, max_browsers, created_at, expires_at, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'license_key': license_key,
            'credits': credits,
            'max_browsers': max_browsers,
            'expires_at': expires_at,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/list_licenses', methods=['GET'])
def admin_list_licenses():
    try:
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        c = conn.cursor()
        c.execute('SELECT * FROM licenses ORDER BY created_at DESC')
        results = c.fetchall()
        conn.close()
        
        licenses = []
        for row in results:
            licenses.append(dict(row))
        
        return jsonify({'success': True, 'licenses': licenses})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/add_credits', methods=['POST'])
def admin_add_credits():
    try:
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        license_key = data.get('license_key', '').strip().upper()
        add_credits = int(data.get('credits', 0))
        
        if add_credits <= 0:
            return jsonify({'success': False, 'error': 'Invalid credit amount'}), 400
        
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        c = conn.cursor()
        c.execute('UPDATE licenses SET credits = credits + ? WHERE license_key = ? AND is_active = 1', 
                 (add_credits, license_key))
        
        if c.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'License not found or inactive'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'added_credits': add_credits})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/revoke_license', methods=['POST'])
def admin_revoke_license():
    try:
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        license_key = data.get('license_key', '').strip().upper()
        
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        c = conn.cursor()
        c.execute('UPDATE licenses SET is_active = 0 WHERE license_key = ?', (license_key,))
        
        if c.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'License not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/logs', methods=['GET'])
def admin_get_logs():
    try:
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        limit = request.args.get('limit', 50)
        
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        c = conn.cursor()
        c.execute('SELECT * FROM usage_logs ORDER BY id DESC LIMIT ?', (limit,))
        results = c.fetchall()
        conn.close()
        
        logs = []
        for row in results:
            logs.append(dict(row))
        
        return jsonify({'success': True, 'logs': logs})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    init_db()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    print("="*60)
    print("🚀 RIDOL FB TOOL - LICENSE SERVER v9.0")
    print("="*60)
    print(f"✅ Database: Connected")
    print(f"🔐 Admin Password: {ADMIN_PASSWORD}")
    print(f"📡 Port: {PORT}")
    print("="*60)
    print("🌐 Admin Panel: https://your-app.onrender.com/admin")
    print("="*60)
    app.run(host='0.0.0.0', port=PORT, debug=False)