#!/usr/bin/env python3
"""
Ridol FB Tool License Server v4.0 - Optimized Edition
Compatible with bot.py v4.0
Author: Ridol Islam
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

# ==================== CONFIGURATION ====================
ADMIN_PASSWORD = 'Ridol123@'
DB_FILE = 'licenses.json'
CUSTOM_SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_sounds')
os.makedirs(CUSTOM_SOUNDS_DIR, exist_ok=True)

# ==================== DATABASE FUNCTIONS ====================
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE) as f:
                return json.load(f)
        except: pass
    return {'users': {}, 'devices': {}}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

db = load_db()

# ==================== HELPERS ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROOT ROUTE ====================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Server is ready for GET requests',
        'status': 'online',
        'version': '4.0',
        'timestamp': datetime.now().isoformat()
    })

# ==================== BOT API ROUTES ====================

@app.route('/api/v1/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'online',
        'version': '4.0',
        'database': 'JSON File',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v1/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'online',
        'license_count': len(db['users']),
        'device_count': len(db['devices']),
        'database': 'JSON File'
    })

@app.route('/api/v1/license/verify', methods=['POST'])
def verify_license():
    data = request.json
    key = data.get('license_key', '')
    device_serial = data.get('device_serial', '')
    
    user = db['users'].get(key)
    if not user:
        return jsonify({'valid': False, 'message': 'Invalid license key'})
    
    if user.get('banned', False):
        return jsonify({'valid': False, 'message': 'This license is banned'})
    
    # Expiry Check
    if user.get('expires_at'):
        try:
            if datetime.now() > datetime.fromisoformat(user['expires_at']):
                return jsonify({'valid': False, 'message': 'License has expired'})
        except: pass

    # Auto-link device if not linked
    if device_serial and not user.get('device'):
        user['device'] = device_serial
        save_db(db)

    return jsonify({
        'valid': True,
        'message': 'License active',
        'expires_at': user.get('expires_at', 'Never'),
        'device': user.get('device', '')
    })

@app.route('/api/v1/device/register', methods=['POST'])
def register_device():
    data = request.json
    serial = data.get('device_serial', '')
    key = data.get('license_key', '')
    
    if not serial:
        return jsonify({'success': False, 'message': 'Device serial missing'})
    
    db['devices'][serial] = {
        'last_seen': datetime.now().isoformat(),
        'license_key': key
    }
    save_db(db)
    return jsonify({'success': True, 'message': 'Device registered'})

# ==================== SOUND API ====================

@app.route('/api/v1/sounds/list', methods=['GET'])
def list_sounds():
    sounds = []
    for f in os.listdir(CUSTOM_SOUNDS_DIR):
        if f.endswith(('.mp3', '.wav', '.ogg')):
            size = os.path.getsize(os.path.join(CUSTOM_SOUNDS_DIR, f))
            sounds.append({'name': f, 'size_mb': round(size / (1024 * 1024), 2)})
    return jsonify({'sounds': sounds})

@app.route('/api/v1/sounds/play', methods=['POST'])
def play_sound():
    filename = request.json.get('filename', 'background.mp3')
    filepath = os.path.join(CUSTOM_SOUNDS_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return jsonify({'success': False, 'message': 'File not found'}), 404

# ==================== ADMIN ROUTES ====================

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
    return render_template_string(LOGIN_HTML)

@app.route('/admin/panel')
@login_required
def admin_panel():
    return render_template_string(ADMIN_HTML)

@app.route('/admin/data')
@login_required
def admin_data():
    return jsonify({
        'users': db['users'],
        'devices': db['devices'],
        'total': len(db['users']),
        'device_count': len(db['devices'])
    })

@app.route('/admin/create', methods=['POST'])
@login_required
def create_license():
    data = request.json
    days = int(data.get('days', 30))
    key = f'RIDOL-{uuid.uuid4().hex[:8].upper()}'
    expires = (datetime.now() + timedelta(days=days)).isoformat()
    
    db['users'][key] = {
        'created_at': datetime.now().isoformat(),
        'expires_at': expires,
        'banned': False,
        'notes': data.get('notes', ''),
        'device': ''
    }
    save_db(db)
    return jsonify({'success': True, 'license_key': key})

@app.route('/admin/ban', methods=['POST'])
@login_required
def ban_license():
    key = request.json.get('license_key')
    if key in db['users']:
        db['users'][key]['banned'] = True
        save_db(db)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

# ==================== HTML TEMPLATES ====================
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Admin Login</title></head>
<body style="background:#0a0a1a; color:white; font-family:sans-serif; text-align:center; padding-top:100px;">
    <h2>🔐 Ridol Server Login</h2>
    <form method="POST">
        <input type="password" name="password" placeholder="Password" style="padding:10px; border-radius:5px;"><br><br>
        <button type="submit" style="padding:10px 20px; background:#00ff88; border:none; cursor:pointer;">Login</button>
    </form>
</body>
</html>
'''

ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <style>
        body { background: #0a101f; color: #fff; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .card { background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #00ff8833; }
        input, button { padding: 10px; border-radius: 5px; border: none; margin: 5px; }
        button { background: #00ff88; color: #000; font-weight: bold; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border-bottom: 1px solid #333; text-align: left; }
    </style>
</head>
<body>
    <h1>🚀 Ridol FB Tool Admin</h1>
    <div class="card">
        <h3>Generate License</h3>
        <input type="number" id="days" placeholder="Days (e.g. 30)">
        <input type="text" id="notes" placeholder="Notes (Client Name)">
        <button onclick="createLicense()">Create Key</button>
        <p id="newKey" style="color: #00ff88; font-weight: bold;"></p>
    </div>

    <div class="card">
        <h3>License List</h3>
        <button onclick="loadData()">Refresh List</button>
        <table>
            <thead><tr><th>Key</th><th>Expiry</th><th>Device</th><th>Status</th><th>Action</th></tr></thead>
            <tbody id="tableBody"></tbody>
        </table>
    </div>

    <script>
        function createLicense() {
            const days = document.getElementById('days').value;
            const notes = document.getElementById('notes').value;
            fetch('/admin/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({days, notes})
            }).then(r => r.json()).then(data => {
                document.getElementById('newKey').innerText = "Created: " + data.license_key;
                loadData();
            });
        }

        function loadData() {
            fetch('/admin/data').then(r => r.json()).then(data => {
                const tbody = document.getElementById('tableBody');
                tbody.innerHTML = '';
                for (let key in data.users) {
                    const u = data.users[key];
                    tbody.innerHTML += `<tr>
                        <td>${key}</td>
                        <td>${u.expires_at.split('T')[0]}</td>
                        <td>${u.device || 'N/A'}</td>
                        <td>${u.banned ? 'Banned' : 'Active'}</td>
                        <td><button style="background:red; color:white;" onclick="banKey('${key}')">Ban</button></td>
                    </tr>`;
                }
            });
        }
        function banKey(key) {
            fetch('/admin/ban', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({license_key: key})
            }).then(() => loadData());
        }
        window.onload = loadData;
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)