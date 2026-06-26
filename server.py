#!/usr/bin/env python3
"""
Ridol FB Tool License Server v4.0
Author: Ridol Islam
License: MIT
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
from flask_cors import CORS
import os
import sys
import json
import uuid
import requests
from datetime import datetime, timedelta
from functools import wraps
import logging

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

ADMIN_PASSWORD = 'Ridol123@'

# ==================== MONGODB CONNECTION ====================
MONGODB_URI = "mongodb+srv://ridoli310_db_user:2knTC9AMZDDUfeil@cluster0.hamwqgx.mongodb.net/?appName=Cluster0"

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("[-] pymongo not installed")

db = None
users_collection = None
devices_collection = None

if MONGO_AVAILABLE:
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
        db = client['ridol_fb_tool']
        users_collection = db['users']
        devices_collection = db['devices']
        client.admin.command('ping')
        print("[+] MongoDB Connected Successfully!")
    except Exception as e:
        print(f"[-] MongoDB Connection Error: {e}")
        db = None

# ==================== DATABASE FUNCTIONS ====================

def get_user(license_key):
    if users_collection:
        try:
            return users_collection.find_one({'license_key': license_key}, {'_id': 0})
        except:
            pass
    return None

def get_users():
    if users_collection:
        try:
            return list(users_collection.find({}, {'_id': 0}))
        except:
            pass
    return []

def get_devices():
    if devices_collection:
        try:
            return list(devices_collection.find({}, {'_id': 0}))
        except:
            pass
    return []

def save_user(user_data):
    if users_collection:
        try:
            if 'created_at' not in user_data:
                user_data['created_at'] = datetime.now().isoformat()
            users_collection.update_one(
                {'license_key': user_data['license_key']},
                {'$set': user_data},
                upsert=True
            )
            return True
        except:
            pass
    return False

def save_device(device_data):
    if devices_collection:
        try:
            if 'created_at' not in device_data:
                device_data['created_at'] = datetime.now().isoformat()
            devices_collection.update_one(
                {'device_serial': device_data['device_serial']},
                {'$set': device_data},
                upsert=True
            )
            return True
        except:
            pass
    return False

def delete_user(license_key):
    if users_collection:
        try:
            users_collection.delete_one({'license_key': license_key})
            return True
        except:
            pass
    return False

# ==================== LICENSE FUNCTIONS ====================

def generate_license_key():
    return f'RIDOL-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:8].upper()}'

def validate_license(key, device_serial):
    user = get_user(key)
    if not user:
        return {'valid': False, 'message': 'Invalid license key'}
    if user.get('banned', False):
        return {'valid': False, 'message': 'License is banned'}
    expires_str = user.get('expires_at', '')
    if expires_str:
        try:
            if datetime.now() > datetime.fromisoformat(expires_str):
                return {'valid': False, 'message': 'License has expired'}
        except:
            pass
    if device_serial:
        device_data = {
            'device_serial': device_serial,
            'license_key': key,
            'last_seen': datetime.now().isoformat()
        }
        save_device(device_data)
    return {
        'valid': True,
        'message': 'License active',
        'expires_at': user.get('expires_at', 'Never'),
        'device': device_serial
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def home():
    try:
        users = get_users()
        devices = get_devices()
        return jsonify({
            'server': 'Ridol FB Tool License Server',
            'version': '4.0',
            'status': 'online',
            'database': 'MongoDB' if db else 'Not Connected',
            'users': len(users),
            'devices': len(devices),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Home error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/ping')
def ping():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '4.0',
        'database': 'MongoDB' if db else 'Not Connected'
    })

@app.route('/api/v1/status')
def api_status():
    try:
        users = get_users()
        devices = get_devices()
        return jsonify({
            'status': 'online',
            'version': '4.0',
            'timestamp': datetime.now().isoformat(),
            'database': 'MongoDB' if db else 'Not Connected',
            'license_count': len(users),
            'device_count': len(devices)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    return jsonify(validate_license(data.get('license_key', ''), data.get('device_serial', '')))

@app.route('/register_device', methods=['POST'])
def register_device():
    data = request.json
    device_serial = data.get('device_serial', '')
    if device_serial:
        device_data = {
            'device_serial': device_serial,
            'license_key': data.get('license_key', ''),
            'last_seen': datetime.now().isoformat()
        }
        save_device(device_data)
        return jsonify({'success': True, 'device_serial': device_serial})
    return jsonify({'success': False, 'message': 'No device serial'})

# ==================== ADMIN ROUTES ====================

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template_string(LOGIN_HTML, error='❌ Incorrect password!')
    
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_panel'))
    
    return render_template_string(LOGIN_HTML, error=None)

@app.route('/admin/panel')
@login_required
def admin_panel():
    return render_template_string(ADMIN_HTML)

@app.route('/admin/data')
@login_required
def admin_data():
    try:
        users = get_users()
        devices = get_devices()
        now = datetime.now()
        total = len(users)
        active = 0
        expired = 0
        banned = 0
        
        for user in users:
            if user.get('banned', False):
                banned += 1
            elif user.get('expires_at', ''):
                try:
                    if now > datetime.fromisoformat(user['expires_at']):
                        expired += 1
                    else:
                        active += 1
                except:
                    active += 1
            else:
                active += 1
        
        return jsonify({
            'users': {u['license_key']: u for u in users},
            'devices': {d['device_serial']: d for d in devices},
            'total': total,
            'active': active,
            'expired': expired,
            'banned': banned,
            'device_count': len(devices)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/create', methods=['POST'])
@login_required
def admin_create():
    try:
        data = request.json
        days = int(data.get('days', 30))
        notes = data.get('notes', '').strip()
        
        if days < 1 or days > 365:
            return jsonify({'success': False, 'message': 'Days must be 1-365'})
        
        key = generate_license_key()
        expires = (datetime.now() + timedelta(days=days)).isoformat()
        
        user_data = {
            'license_key': key,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires,
            'banned': False,
            'notes': notes if notes else 'No notes',
            'device': ''
        }
        
        if save_user(user_data):
            return jsonify({
                'success': True,
                'message': f'✅ License created! Valid for {days} days.',
                'license_key': key,
                'expires_at': expires
            })
        return jsonify({'success': False, 'message': 'Failed to save to database'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/ban', methods=['POST'])
@login_required
def admin_ban():
    try:
        key = request.json.get('license_key', '')
        if not key:
            return jsonify({'success': False, 'message': 'No license key'})
        
        user = get_user(key)
        if not user:
            return jsonify({'success': False, 'message': 'License not found'})
        
        user['banned'] = True
        save_user(user)
        return jsonify({'success': True, 'message': '✅ License banned'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/unban', methods=['POST'])
@login_required
def admin_unban():
    try:
        key = request.json.get('license_key', '')
        if not key:
            return jsonify({'success': False, 'message': 'No license key'})
        
        user = get_user(key)
        if not user:
            return jsonify({'success': False, 'message': 'License not found'})
        
        user['banned'] = False
        save_user(user)
        return jsonify({'success': True, 'message': '✅ License unbanned'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/delete', methods=['POST'])
@login_required
def admin_delete():
    try:
        key = request.json.get('license_key', '')
        if not key:
            return jsonify({'success': False, 'message': 'No license key'})
        
        if delete_user(key):
            return jsonify({'success': True, 'message': '✅ License deleted'})
        return jsonify({'success': False, 'message': 'License not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/logout')
@login_required
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# ==================== HTML TEMPLATES ====================

LOGIN_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Admin Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: #0a0a1a; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .login-container { background: #111; padding: 40px; border-radius: 16px; border: 1px solid #1a1a2e; max-width: 420px; width: 100%; }
        .login-container h1 { color: #00ff88; text-align: center; font-size: 24px; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #666; font-size: 13px; margin-bottom: 30px; }
        .db-badge { background: #003311; color: #00ff88; padding: 2px 12px; border-radius: 12px; font-size: 10px; display: inline-block; text-align: center; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { color: #aaa; font-size: 13px; display: block; margin-bottom: 6px; }
        .form-group input { width: 100%; padding: 12px 16px; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
        .form-group input:focus { border-color: #00ff88; }
        .btn-login { width: 100%; padding: 14px; background: #00ff88; border: none; border-radius: 8px; color: #000; font-size: 16px; font-weight: bold; cursor: pointer; }
        .btn-login:hover { background: #00cc77; }
        .error-msg { background: rgba(255,68,68,0.1); border: 1px solid #ff4444; color: #ff4444; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; text-align: center; }
        .hint { text-align: center; color: #333; font-size: 12px; margin-top: 15px; }
        .hint span { background: #1a1a2e; padding: 2px 10px; border-radius: 4px; color: #666; }
        .footer { text-align: center; color: #333; font-size: 11px; margin-top: 20px; }
        .footer .brand { color: #00ff88; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔐 RIDOL FB TOOL</h1>
        <div class="subtitle">Admin Authentication • v4.0</div>
        <div style="text-align:center"><span class="db-badge">🍃 MongoDB</span></div>
        {% if error %}
        <div class="error-msg">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/admin">
            <div class="form-group">
                <label>🔑 Admin Password</label>
                <input type="password" name="password" placeholder="Enter admin password" required autofocus>
            </div>
            <button type="submit" class="btn-login">🚀 Access Panel</button>
        </form>
        <div class="hint"><span>🔑 Hint: Admin Password</span></div>
        <div class="footer"><span class="brand">RIDOL FB TOOL</span> • v4.0</div>
    </div>
</body>
</html>'''

ADMIN_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Admin Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: #0a0a1a; color: #fff; padding: 20px; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #111; border-radius: 12px; border: 1px solid #1a1a2e; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
        .header h1 { color: #00ff88; font-size: 20px; }
        .header .badge { background: #00ff88; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .header .db-badge { background: #003311; color: #00ff88; padding: 4px 12px; border-radius: 12px; font-size: 10px; border: 1px solid #00ff88; }
        .btn-logout { background: #ff4444; color: #fff; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; }
        .btn-logout:hover { background: #cc0000; }
        .card { background: #111; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #1a1a2e; }
        .card h2 { color: #00ff88; font-size: 16px; margin-bottom: 15px; }
        .flex { display: flex; gap: 15px; flex-wrap: wrap; }
        .flex-grow { flex: 1; min-width: 200px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { color: #aaa; font-size: 12px; display: block; margin-bottom: 5px; }
        .form-group input, .form-group select { width: 100%; padding: 10px 14px; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
        .form-group input:focus { border-color: #00ff88; }
        .btn { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 13px; }
        .btn:hover { transform: scale(1.02); }
        .btn-green { background: #00ff88; color: #000; }
        .btn-red { background: #ff4444; color: #fff; }
        .btn-blue { background: #4488ff; color: #fff; }
        .btn-orange { background: #ff8800; color: #fff; }
        .btn-purple { background: #aa44ff; color: #fff; }
        .btn-sm { padding: 6px 12px; font-size: 11px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; }
        .stat-box { text-align: center; padding: 15px; background: #1a1a2e; border-radius: 8px; }
        .stat-box .number { font-size: 28px; font-weight: bold; }
        .stat-box .label { color: #888; font-size: 11px; margin-top: 5px; }
        .table-wrapper { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #1a1a2e; font-size: 13px; }
        th { color: #00ff88; font-size: 11px; text-transform: uppercase; }
        td code { background: #1a1a2e; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
        .badge { padding: 2px 10px; border-radius: 20px; font-size: 11px; }
        .badge-active { background: #003311; color: #00ff88; }
        .badge-expired { background: #330000; color: #ff4444; }
        .badge-banned { background: #331100; color: #ff8800; }
        .msg { padding: 12px 16px; border-radius: 8px; margin: 10px 0; display: none; font-weight: bold; }
        .msg-success { background: #003311; color: #00ff88; border: 1px solid #00ff88; }
        .msg-error { background: #330000; color: #ff4444; border: 1px solid #ff4444; }
        .msg-info { background: #001133; color: #4488ff; border: 1px solid #4488ff; }
        .new-key-box { margin-top: 15px; padding: 20px; background: #1a1a2e; border-radius: 8px; border: 2px solid #00ff88; display: none; }
        .new-key-box .key { font-size: 20px; font-family: monospace; color: #00ff88; display: block; margin: 10px 0; padding: 10px; background: #000; border-radius: 6px; word-break: break-all; }
        .search-box { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .search-box input { flex: 1; min-width: 180px; padding: 10px 14px; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 13px; outline: none; }
        .search-box input:focus { border-color: #00ff88; }
        .footer { text-align: center; color: #333; font-size: 11px; margin-top: 30px; }
        @media (max-width: 600px) { .header { flex-direction: column; align-items: flex-start; } .stats { grid-template-columns: repeat(2, 1fr); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🔐 RIDOL FB TOOL <span style="font-size:14px;color:#666;font-weight:400">v4.0</span></h1>
                <div style="color:#666;font-size:12px;margin-top:3px">
                    Admin Panel • <span class="db-badge">🍃 MongoDB</span>
                </div>
            </div>
            <div style="display:flex;gap:10px;align-items:center">
                <span class="badge">👑 ADMIN</span>
                <a href="/admin/logout"><button class="btn-logout">🚪 LOGOUT</button></a>
            </div>
        </div>
        
        <div id="msg" class="msg"></div>
        
        <div class="card">
            <h2>➕ Create License</h2>
            <div class="flex">
                <div class="flex-grow">
                    <div class="form-group">
                        <label>📅 Expiry Days (1-365)</label>
                        <input type="number" id="days" value="30" min="1" max="365">
                    </div>
                </div>
                <div class="flex-grow">
                    <div class="form-group">
                        <label>📝 Notes (Client Name)</label>
                        <input type="text" id="notes" placeholder="e.g., John's Device">
                    </div>
                </div>
            </div>
            <button class="btn btn-green" onclick="createLic()">⚡ GENERATE LICENSE</button>
            <div id="new_key" class="new-key-box">
                <strong style="color:#00ff88">✅ License Created Successfully!</strong>
                <span class="key" id="key_display">RIDOL-XXXX-XXXX-XXXX</span>
                <div class="flex" style="gap:10px">
                    <button class="btn btn-blue" onclick="copyKey()">📋 COPY</button>
                    <button class="btn btn-orange" onclick="searchNewKey()">🔍 FIND</button>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📊 Statistics</h2>
            <div class="stats">
                <div class="stat-box"><div class="number" style="color:#00ff88" id="s_total">0</div><div class="label">Total</div></div>
                <div class="stat-box"><div class="number" style="color:#00ff88" id="s_active">0</div><div class="label">✅ Active</div></div>
                <div class="stat-box"><div class="number" style="color:#ff8800" id="s_expired">0</div><div class="label">⏰ Expired</div></div>
                <div class="stat-box"><div class="number" style="color:#ff4444" id="s_banned">0</div><div class="label">🚫 Banned</div></div>
                <div class="stat-box"><div class="number" style="color:#4488ff" id="s_devices">0</div><div class="label">📱 Devices</div></div>
            </div>
        </div>
        
        <div class="card">
            <h2>👥 License Management</h2>
            <div class="search-box">
                <input type="text" id="search" placeholder="🔍 Search by key, device, or notes..." onkeyup="if(event.key==='Enter')searchLic()">
                <button class="btn btn-blue" onclick="searchLic()">🔍 SEARCH</button>
                <button class="btn btn-orange" onclick="refreshAll()">🔄 REFRESH</button>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>License Key</th>
                            <th>Expires</th>
                            <th>Status</th>
                            <th>Device</th>
                            <th>Created</th>
                            <th>Notes</th>
                            <th style="text-align:center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tbody">
                        <tr><td colspan="7" style="text-align:center;color:rgba(255,255,255,0.1);padding:40px;letter-spacing:2px">Loading licenses...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">✦ RIDOL FB TOOL v4.0 • MongoDB ✦</div>
    </div>
    
    <script>
        var allUsers = {};
        var filteredUsers = {};
        var lastCreatedKey = '';
        
        function showMsg(text, type) {
            var el = document.getElementById('msg');
            el.textContent = text;
            el.className = 'msg msg-' + type;
            el.style.display = 'block';
            setTimeout(function() { el.style.display = 'none'; }, 6000);
        }
        
        function apiCall(url, method, data) {
            return fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: data ? JSON.stringify(data) : undefined
            }).then(function(res) {
                if (res.status === 401 || res.status === 302) {
                    window.location.href = '/admin';
                    return null;
                }
                return res.json();
            }).catch(function(e) {
                showMsg('❌ Network Error: ' + e.message, 'error');
                return null;
            });
        }
        
        function createLic() {
            var days = parseInt(document.getElementById('days').value) || 30;
            var notes = document.getElementById('notes').value || '';
            if (days < 1) { showMsg('❌ At least 1 day', 'error'); return; }
            if (days > 365) { showMsg('❌ Max 365 days', 'error'); return; }
            
            showMsg('⏳ Generating...', 'info');
            apiCall('/admin/create', 'POST', { days: days, notes: notes })
                .then(function(result) {
                    if (result && result.success) {
                        lastCreatedKey = result.license_key;
                        document.getElementById('key_display').textContent = lastCreatedKey;
                        document.getElementById('new_key').style.display = 'block';
                        showMsg('✅ ' + result.message, 'success');
                        refreshAll();
                    } else {
                        showMsg(result ? result.message : '❌ Failed', 'error');
                        document.getElementById('new_key').style.display = 'none';
                    }
                });
        }
        
        function copyKey() {
            var key = document.getElementById('key_display').textContent;
            navigator.clipboard.writeText(key).then(function() {
                showMsg('📋 Copied!', 'success');
            }).catch(function() {
                var ta = document.createElement('textarea');
                ta.value = key;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                showMsg('📋 Copied!', 'success');
            });
        }
        
        function searchNewKey() {
            if (lastCreatedKey) {
                document.getElementById('search').value = lastCreatedKey;
                searchLic();
                document.getElementById('new_key').style.display = 'none';
            }
        }
        
        function toggleBan(key, isBanned) {
            var action = isBanned ? 'unban' : 'ban';
            showMsg('⏳ Processing...', 'info');
            apiCall('/admin/' + action, 'POST', { license_key: key })
                .then(function(result) {
                    if (result && result.success) { showMsg('✅ ' + result.message, 'success'); refreshAll(); }
                    else { showMsg(result ? result.message : '❌ Failed', 'error'); }
                });
        }
        
        function deleteLic(key) {
            if (!confirm('⚠️ Delete ' + key + '?')) return;
            showMsg('⏳ Deleting...', 'info');
            apiCall('/admin/delete', 'POST', { license_key: key })
                .then(function(result) {
                    if (result && result.success) { showMsg('✅ ' + result.message, 'success'); refreshAll(); }
                    else { showMsg(result ? result.message : '❌ Failed', 'error'); }
                });
        }
        
        function renderTable(users) {
            var tbody = document.getElementById('tbody');
            tbody.innerHTML = '';
            var now = new Date();
            var keys = Object.keys(users);
            if (keys.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:rgba(255,255,255,0.05);padding:40px;letter-spacing:3px">No licenses found</td></tr>';
                return;
            }
            keys.forEach(function(key) {
                var u = users[key];
                var expires = u.expires_at ? new Date(u.expires_at) : null;
                var isExpired = expires && now > expires;
                var isBanned = u.banned || false;
                var status = 'Active';
                var badge = 'badge-active';
                if (isBanned) { status = 'Banned'; badge = 'badge-banned'; }
                else if (isExpired) { status = 'Expired'; badge = 'badge-expired'; }
                var tr = document.createElement('tr');
                tr.innerHTML = '<td><code>' + key + '</code></td>' +
                    '<td style="font-size:10px">' + (u.expires_at || 'Never') + '</td>' +
                    '<td><span class="badge ' + badge + '">' + status + '</span></td>' +
                    '<td style="font-size:10px;color:rgba(255,255,255,0.15)">' + (u.device || '-') + '</td>' +
                    '<td style="font-size:9px;color:rgba(255,255,255,0.1)">' + (u.created_at || '-') + '</td>' +
                    '<td style="font-size:10px;color:rgba(255,255,255,0.15)">' + (u.notes || '-') + '</td>' +
                    '<td style="text-align:center;white-space:nowrap">' +
                    '<button class="btn ' + (isBanned ? 'btn-green' : 'btn-red') + ' btn-sm" onclick="toggleBan(\'' + key + '\',' + isBanned + ')" style="margin:2px">' + (isBanned ? 'UNBAN' : 'BAN') + '</button>' +
                    '<button class="btn btn-red btn-sm" onclick="deleteLic(\'' + key + '\')" style="margin:2px">✕</button>' +
                    '</td>';
                tbody.appendChild(tr);
            });
        }
        
        function refreshAll() {
            apiCall('/admin/data', 'GET')
                .then(function(data) {
                    if (!data) {
                        document.getElementById('tbody').innerHTML = '<tr><td colspan="7" style="text-align:center;color:#ff4444;padding:40px">❌ Failed to load</td></tr>';
                        return;
                    }
                    allUsers = data.users || {};
                    filteredUsers = allUsers;
                    renderTable(filteredUsers);
                    document.getElementById('s_total').textContent = data.total || 0;
                    document.getElementById('s_active').textContent = data.active || 0;
                    document.getElementById('s_expired').textContent = data.expired || 0;
                    document.getElementById('s_banned').textContent = data.banned || 0;
                    document.getElementById('s_devices').textContent = data.device_count || 0;
                });
        }
        
        function searchLic() {
            var q = document.getElementById('search').value.toLowerCase().trim();
            if (!q) { filteredUsers = allUsers; renderTable(filteredUsers); return; }
            filteredUsers = {};
            Object.keys(allUsers).forEach(function(key) {
                var u = allUsers[key];
                if (key.toLowerCase().includes(q) || (u.device && u.device.toLowerCase().includes(q)) || (u.notes && u.notes.toLowerCase().includes(q))) {
                    filteredUsers[key] = u;
                }
            });
            renderTable(filteredUsers);
            showMsg('🔍 Found ' + Object.keys(filteredUsers).length + ' result(s)', 'info');
        }
        
        refreshAll();
        setInterval(refreshAll, 30000);
    </script>
</body>
</html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)