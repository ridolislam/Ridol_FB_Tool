#!/usr/bin/env python3
"""
Ridol FB Tool License Server
Author: Ridol Islam
License: MIT
"""

from flask import Flask, request, jsonify, render_template_string
import json
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
DB_FILE = 'licenses.json'

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE) as f:
                return json.load(f)
        except:
            pass
    return {'users': {}, 'devices': {}}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

db = load_db()

def generate_license_key():
    return f'RIDOL-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:8].upper()}'

def validate_license(key, device_serial):
    user = db['users'].get(key)
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
        db['devices'][device_serial] = {
            'license_key': key,
            'last_seen': datetime.now().isoformat(),
            'created_at': user.get('created_at', datetime.now().isoformat())
        }
        save_db(db)
    return {
        'valid': True,
        'message': 'License active',
        'expires_at': user.get('expires_at', 'Never'),
        'device': device_serial
    }

@app.route('/')
def home():
    return jsonify({
        'server': 'Ridol FB Tool License Server',
        'version': 'v2.0',
        'status': 'online',
        'endpoints': ['/verify', '/register_device', '/admin']
    })

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    license_key = data.get('license_key', '')
    device_serial = data.get('device_serial', '')
    return jsonify(validate_license(license_key, device_serial))

@app.route('/register_device', methods=['POST'])
def register_device():
    data = request.json
    device_serial = data.get('device_serial', '')
    if device_serial:
        db['devices'][device_serial] = {
            'license_key': '',
            'last_seen': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        save_db(db)
        return jsonify({'success': True, 'device_serial': device_serial})
    return jsonify({'success': False, 'message': 'No device serial'})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data = request.json or request.form
        if data.get('username') == 'admin' and data.get('password') == 'admin123':
            return jsonify({'authenticated': True})
        return jsonify({'authenticated': False})
    return render_template_string(ADMIN_HTML)

@app.route('/admin/check')
def admin_check():
    return jsonify({'authenticated': True})

@app.route('/admin/data')
def admin_data():
    users = db.get('users', {})
    devices = db.get('devices', {})
    now = datetime.now()
    total = len(users)
    active = 0
    expired = 0
    banned = 0
    
    for key, user in users.items():
        if user.get('banned'):
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
        'users': users,
        'devices': devices,
        'total': total,
        'active': active,
        'expired': expired,
        'banned': banned,
        'device_count': len(devices)
    })

@app.route('/admin/create', methods=['POST'])
def admin_create():
    data = request.json
    days = int(data.get('days', 30))
    notes = data.get('notes', '')
    key = generate_license_key()
    expires = (datetime.now() + timedelta(days=days)).isoformat()
    
    db['users'][key] = {
        'created_at': datetime.now().isoformat(),
        'expires_at': expires,
        'banned': False,
        'notes': notes,
        'device': ''
    }
    save_db(db)
    return jsonify({
        'success': True,
        'license_key': key,
        'expires_at': expires
    })

@app.route('/admin/ban', methods=['POST'])
def admin_ban():
    key = request.json.get('license_key', '')
    if key in db['users']:
        db['users'][key]['banned'] = True
        save_db(db)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/admin/unban', methods=['POST'])
def admin_unban():
    key = request.json.get('license_key', '')
    if key in db['users']:
        db['users'][key]['banned'] = False
        save_db(db)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    key = request.json.get('license_key', '')
    if key in db['users']:
        del db['users'][key]
        save_db(db)
        return jsonify({'success': True})
    return jsonify({'success': False})

ADMIN_HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>Ridol Admin Panel</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:Arial,sans-serif }
        body { background:#0a0a1a; color:#fff; padding:20px }
        .container { max-width:1200px; margin:0 auto }
        h1 { color:#00ff88; text-align:center; margin-bottom:30px }
        .card { background:#111; border-radius:8px; padding:20px; margin-bottom:20px; border:1px solid #222 }
        .card h2 { color:#00ff88; margin-bottom:15px }
        .form-group { margin-bottom:15px }
        label { color:#aaa; font-size:13px }
        input,select { width:100%; padding:10px; background:#1a1a2e; border:1px solid #333; color:#fff; border-radius:4px }
        button { padding:10px 20px; border:none; border-radius:4px; cursor:pointer; font-weight:bold }
        .btn-green { background:#00ff88; color:#000 }
        .btn-red { background:#ff4444; color:#fff }
        .btn-blue { background:#4488ff; color:#fff }
        .btn-orange { background:#ff8800; color:#000 }
        table { width:100%; border-collapse:collapse; margin-top:10px }
        th,td { padding:8px; text-align:left; border-bottom:1px solid #222; font-size:13px }
        th { color:#00ff88 }
        .badge { padding:2px 8px; border-radius:10px; font-size:11px }
        .badge-active { background:#003311; color:#00ff88 }
        .badge-expired { background:#330000; color:#ff4444 }
        .badge-banned { background:#331100; color:#ff8800 }
        .msg { padding:10px; margin:10px 0; border-radius:4px; display:none }
        .msg-success { background:#003311; color:#00ff88 }
        .msg-error { background:#330000; color:#ff4444 }
        .msg-info { background:#001133; color:#4488ff }
        .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:15px }
        .stat-box { text-align:center; padding:15px; background:#1a1a2e; border-radius:5px }
        .stat-box .number { font-size:28px; font-weight:bold }
        .stat-box .label { color:#888; font-size:12px; margin-top:5px }
        .footer { text-align:center; color:#444; margin-top:40px; font-size:12px }
        .flex { display:flex; gap:10px; flex-wrap:wrap }
        .flex-grow { flex:1 }
        code { background:#1a1a2e; padding:2px 6px; border-radius:3px; font-size:12px }
        .copy-btn { background:#333; color:#fff; padding:5px 10px; border:none; border-radius:3px; cursor:pointer; font-size:11px }
        .copy-btn:hover { background:#555 }
    </style>
</head>
<body>
<div class="container">
    <h1>🔐 RIDOL FB TOOL ADMIN</h1>
    <div style="text-align:center;color:#888;margin-bottom:20px">🌐 https://ridol-fb-tool.onrender.com</div>
    
    <div id="msg" class="msg"></div>
    
    <div class="card">
        <h2>➕ Create License</h2>
        <div class="flex">
            <div class="flex-grow">
                <div class="form-group">
                    <label>Expiry Days</label>
                    <input type="number" id="days" value="30" min="1" max="365">
                </div>
            </div>
            <div class="flex-grow">
                <div class="form-group">
                    <label>Notes (User/Client)</label>
                    <input type="text" id="notes" placeholder="Client name">
                </div>
            </div>
        </div>
        <button class="btn-green" onclick="createLic()">⚡ Generate Key</button>
        <div id="new_key" style="margin-top:15px;padding:15px;background:#1a1a2e;border-radius:4px;display:none;border:1px solid #00ff88"></div>
    </div>
    
    <div class="card">
        <h2>📊 License Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="number" style="color:#00ff88" id="s_total">0</div>
                <div class="label">Total Licenses</div>
            </div>
            <div class="stat-box">
                <div class="number" style="color:#00ff88" id="s_active">0</div>
                <div class="label">Active</div>
            </div>
            <div class="stat-box">
                <div class="number" style="color:#ff8800" id="s_expired">0</div>
                <div class="label">Expired</div>
            </div>
            <div class="stat-box">
                <div class="number" style="color:#ff4444" id="s_banned">0</div>
                <div class="label">Banned</div>
            </div>
            <div class="stat-box">
                <div class="number" style="color:#4488ff" id="s_devices">0</div>
                <div class="label">Registered Devices</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>👥 License Management</h2>
        <div class="flex" style="margin-bottom:15px">
            <input type="text" id="search" placeholder="Search by key or device..." class="flex-grow">
            <button class="btn-blue" onclick="searchLic()">🔍 Search</button>
            <button class="btn-orange" onclick="refreshAll()">🔄 Refresh</button>
        </div>
        <div style="overflow-x:auto">
        <table>
            <thead>
                <tr>
                    <th>License Key</th>
                    <th>Expires</th>
                    <th>Status</th>
                    <th>Device</th>
                    <th>Created</th>
                    <th>Notes</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="tbody"></tbody>
        </table>
        </div>
    </div>
    
    <div class="footer">Ridol FB Tool License Server v2.0</div>
</div>

<script>
let allUsers = {};
let filteredUsers = {};

function showMsg(text, type) {
    const el = document.getElementById('msg');
    el.textContent = text;
    el.className = 'msg msg-' + type;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 4000);
}

async function apiCall(url, method, data) {
    try {
        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: data ? JSON.stringify(data) : undefined
        });
        return await res.json();
    } catch (e) {
        showMsg('Error: ' + e.message, 'error');
        return null;
    }
}

async function createLic() {
    const days = parseInt(document.getElementById('days').value) || 30;
    const notes = document.getElementById('notes').value || '';
    const result = await apiCall('/admin/create', 'POST', { days, notes });
    
    if (result && result.success) {
        const key = result.license_key;
        document.getElementById('new_key').innerHTML = 
            '<strong style="color:#00ff88">✅ New License Key</strong><br>' +
            '<code style="font-size:20px;display:block;margin:10px 0;padding:10px;background:#000;border-radius:4px">' + key + '</code>' +
            '<div class="flex">' +
            '<button class="btn-blue" onclick="copyKey(\'' + key + '\')">📋 Copy</button>' +
            '<button class="btn-green" onclick="document.getElementById(\\\'search\\\').value=\\'\' + key + '\\\';searchLic()">🔍 Find</button>' +
            '</div>';
        document.getElementById('new_key').style.display = 'block';
        showMsg('✅ License created successfully!', 'success');
        refreshAll();
    } else {
        showMsg('❌ Failed to create license', 'error');
    }
}

function copyKey(key) {
    navigator.clipboard.writeText(key).then(() => {
        showMsg('📋 Copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = key;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showMsg('📋 Copied!', 'success');
    });
}

async function toggleBan(key, isBanned) {
    const action = isBanned ? 'unban' : 'ban';
    const result = await apiCall('/admin/' + action, 'POST', { license_key: key });
    if (result && result.success) {
        showMsg('✅ License ' + (isBanned ? 'unbanned' : 'banned'), 'success');
        refreshAll();
    } else {
        showMsg('❌ Operation failed', 'error');
    }
}

async function deleteLic(key) {
    if (!confirm('⚠️ Permanently delete license: ' + key + '?')) return;
    const result = await apiCall('/admin/delete', 'POST', { license_key: key });
    if (result && result.success) {
        showMsg('✅ License deleted', 'success');
        refreshAll();
    } else {
        showMsg('❌ Delete failed', 'error');
    }
}

function renderTable(users) {
    const tbody = document.getElementById('tbody');
    tbody.innerHTML = '';
    const now = new Date();
    
    Object.keys(users).forEach(key => {
        const u = users[key];
        const expires = u.expires_at ? new Date(u.expires_at) : null;
        const isExpired = expires && now > expires;
        const isBanned = u.banned || false;
        
        let status = 'Active';
        let badge = 'badge-active';
        if (isBanned) { status = 'Banned'; badge = 'badge-banned'; }
        else if (isExpired) { status = 'Expired'; badge = 'badge-expired'; }
        
        const tr = document.createElement('tr');
        tr.innerHTML = 
            '<td><code style="font-size:11px">' + key + '</code></td>' +
            '<td>' + (u.expires_at || 'Never') + '</td>' +
            '<td><span class="badge ' + badge + '">' + status + '</span></td>' +
            '<td>' + (u.device || '-') + '</td>' +
            '<td style="font-size:11px">' + (u.created_at || '-') + '</td>' +
            '<td style="font-size:11px;color:#888">' + (u.notes || '-') + '</td>' +
            '<td>' +
            '<button class="btn-' + (isBanned ? 'green' : 'red') + '" onclick="toggleBan(\'' + key + '\',' + isBanned + ')" style="padding:3px 8px;font-size:11px;margin:2px">' + (isBanned ? 'Unban' : 'Ban') + '</button> ' +
            '<button class="btn-red" onclick="deleteLic(\'' + key + '\')" style="padding:3px 8px;font-size:11px;margin:2px">✕</button>' +
            '</td>';
        tbody.appendChild(tr);
    });
    
    if (Object.keys(users).length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#666;padding:20px">No licenses found</td></tr>';
    }
}

async function refreshAll() {
    const data = await apiCall('/admin/data', 'GET');
    if (!data) return;
    
    allUsers = data.users || {};
    filteredUsers = allUsers;
    renderTable(filteredUsers);
    
    document.getElementById('s_total').textContent = data.total || 0;
    document.getElementById('s_active').textContent = data.active || 0;
    document.getElementById('s_expired').textContent = data.expired || 0;
    document.getElementById('s_banned').textContent = data.banned || 0;
    document.getElementById('s_devices').textContent = data.device_count || 0;
}

function searchLic() {
    const q = document.getElementById('search').value.toLowerCase().trim();
    if (!q) {
        filteredUsers = allUsers;
        renderTable(filteredUsers);
        return;
    }
    filteredUsers = {};
    Object.keys(allUsers).forEach(key => {
        const u = allUsers[key];
        if (key.toLowerCase().includes(q) || 
            (u.device && u.device.toLowerCase().includes(q)) ||
            (u.notes && u.notes.toLowerCase().includes(q))) {
            filteredUsers[key] = u;
        }
    });
    renderTable(filteredUsers);
    showMsg('🔍 Found ' + Object.keys(filteredUsers).length + ' result(s)', 'info');
}

// Auto-refresh every 30 seconds
refreshAll();
setInterval(refreshAll, 30000);

// Search on Enter key
document.getElementById('search').addEventListener('keyup', function(e) {
    if (e.key === 'Enter') searchLic();
});
</script>
</body>
</html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)