# server.py - Ridol FB Tool License Server v2.0
# Render এ deploy করার জন্য

from flask import Flask, request, jsonify, render_template_string
import sqlite3
import uuid
import hashlib
import datetime
import os
import base64

app = Flask(__name__)
DB = "licenses.db"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"  # production এ change করুন

# ============== ডাটাবেস ==============
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  license_key TEXT UNIQUE NOT NULL,
                  device_id TEXT,
                  username TEXT,
                  created_at TEXT,
                  expires_at TEXT,
                  is_active INTEGER DEFAULT 1,
                  is_banned INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS usage_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  license_key TEXT,
                  device_id TEXT,
                  ip_address TEXT,
                  action TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def generate_license_key():
    return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16].upper()

def log_usage(license_key, device_id, ip, action):
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO usage_log (license_key, device_id, ip_address, action, timestamp) VALUES (?,?,?,?,?)",
                  (license_key, device_id, ip, action, datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except:
        pass

def check_admin_auth(auth):
    if not auth.startswith('Basic '):
        return False
    try:
        decoded = base64.b64decode(auth[6:]).decode()
        user, pwd = decoded.split(':', 1)
        return user == ADMIN_USER and pwd == ADMIN_PASS
    except:
        return False

# ============== API Endpoints ==============

@app.route('/')
def home():
    return jsonify({"status": "Ridol License Server Active", "version": "2.0"})

@app.route('/verify', methods=['POST'])
def verify_license():
    data = request.json
    key = data.get('license_key', '').strip()
    device_id = data.get('device_id', '').strip()
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM licenses WHERE license_key=? AND is_active=1 AND is_banned=0", (key,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"valid": False, "message": "Invalid license key"})
    
    expires = datetime.datetime.fromisoformat(row[6])
    if datetime.datetime.now() > expires:
        return jsonify({"valid": False, "message": "License expired"})
    
    log_usage(key, device_id, request.remote_addr, "verify")
    
    return jsonify({
        "valid": True,
        "device_id": row[2],
        "username": row[3],
        "expires_at": row[6],
        "days_left": (expires - datetime.datetime.now()).days
    })

@app.route('/register_device', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id', '').strip()
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM licenses WHERE device_id=? AND is_banned=0", (device_id,))
    existing = c.fetchone()
    
    if existing:
        exp = datetime.datetime.fromisoformat(existing[6])
        if datetime.datetime.now() < exp:
            conn.close()
            return jsonify({
                "status": "registered",
                "license_key": existing[1],
                "expires_at": existing[6]
            })
    conn.close()
    
    return jsonify({
        "status": "pending",
        "device_id": device_id,
        "message": "Device not registered. Send this Device ID to admin."
    })

@app.route('/admin/generate', methods=['POST'])
def admin_generate():
    data = request.json
    auth = request.headers.get('Authorization', '')
    if not check_admin_auth(auth):
        return jsonify({"error": "Unauthorized"}), 401
    
    device_id = data.get('device_id', '')
    username = data.get('username', 'user')
    days = data.get('days', 30)
    
    key = generate_license_key()
    created = datetime.datetime.now().isoformat()
    expires = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO licenses (license_key, device_id, username, created_at, expires_at) VALUES (?,?,?,?,?)",
                  (key, device_id, username, created, expires))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Device already has a license"}), 400
    conn.close()
    
    return jsonify({
        "status": "created",
        "license_key": key,
        "device_id": device_id,
        "username": username,
        "expires_at": expires
    })

@app.route('/admin/ban', methods=['POST'])
def admin_ban():
    data = request.json
    auth = request.headers.get('Authorization', '')
    if not check_admin_auth(auth):
        return jsonify({"error": "Unauthorized"}), 401
    
    key = data.get('license_key', '')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE licenses SET is_banned=1, is_active=0 WHERE license_key=?", (key,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    
    if affected:
        return jsonify({"status": "banned", "license_key": key})
    return jsonify({"error": "License not found"}), 404

@app.route('/admin/extend', methods=['POST'])
def admin_extend():
    data = request.json
    auth = request.headers.get('Authorization', '')
    if not check_admin_auth(auth):
        return jsonify({"error": "Unauthorized"}), 401
    
    key = data.get('license_key', '')
    extra_days = data.get('days', 30)
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT expires_at FROM licenses WHERE license_key=?", (key,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "License not found"}), 404
    
    current_expires = datetime.datetime.fromisoformat(row[0])
    new_expires = max(current_expires, datetime.datetime.now()) + datetime.timedelta(days=extra_days)
    
    c.execute("UPDATE licenses SET expires_at=? WHERE license_key=?", (new_expires.isoformat(), key))
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "extended",
        "license_key": key,
        "new_expires_at": new_expires.isoformat()
    })

@app.route('/admin/users', methods=['GET'])
def admin_users():
    auth = request.headers.get('Authorization', '')
    if not check_admin_auth(auth):
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT license_key, device_id, username, created_at, expires_at, is_active, is_banned FROM licenses")
    rows = c.fetchall()
    conn.close()
    
    users = []
    for r in rows:
        users.append({
            "license_key": r[0],
            "device_id": r[1],
            "username": r[2],
            "created_at": r[3],
            "expires_at": r[4],
            "is_active": bool(r[5]),
            "is_banned": bool(r[6])
        })
    
    return jsonify({"users": users, "total": len(users)})

@app.route('/admin')
def admin_panel():
    return render_template_string(ADMIN_HTML)

# ============== Admin Panel HTML ==============
ADMIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ridol FB Tool - Admin Panel v2.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0d1117;color:#c9d1d9;padding:16px}
.container{max-width:1200px;margin:0 auto}
h1{color:#58a6ff;font-size:22px;margin-bottom:16px}
h2{color:#8b949e;font-size:16px;margin:16px 0 8px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:16px}
.form-group{margin-bottom:12px}
label{display:block;margin-bottom:4px;color:#8b949e;font-size:13px}
input,select{width:100%;padding:10px;background:#0d1117;border:1px solid #30363d;border-radius:6px;color:#c9d1d9;font-size:14px}
input:focus{outline:none;border-color:#58a6ff}
button{background:#238636;color:#fff;border:none;padding:10px 18px;border-radius:6px;cursor:pointer;font-size:13px;margin-right:8px;margin-bottom:6px}
button:hover{background:#2ea043}
button.danger{background:#da3633}
button.danger:hover{background:#f85149}
.output{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:12px;margin-top:12px;font-family:'Courier New',monospace;font-size:12px;white-space:pre-wrap;min-height:40px;word-break:break-all}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:12px}
th,td{padding:8px;text-align:left;border-bottom:1px solid #30363d;word-break:break-all}
th{color:#8b949e;font-weight:600}
.status-active{color:#3fb950;font-weight:600}
.status-banned{color:#f85149;font-weight:600}
.status-expired{color:#d29922;font-weight:600}
.tabs{display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap}
.tab{padding:8px 14px;background:#161b22;border:1px solid #30363d;border-radius:6px;cursor:pointer;font-size:13px}
.tab.active{background:#1f6feb;border-color:#1f6feb}
.success{color:#3fb950}
.error{color:#f85149}
@media(max-width:600px){table{font-size:10px}th,td{padding:4px}}
</style>
</head>
<body>
<div class="container">
<h1>🔑 Ridol FB Tool Admin v2.0</h1>

<div class="card" id="authForm">
<h2>Admin Login</h2>
<div class="form-group"><label>Username</label><input type="text" id="adminUser" value="admin"></div>
<div class="form-group"><label>Password</label><input type="password" id="adminPass" value="admin123"></div>
<button onclick="login()">Login</button>
</div>

<div id="mainContent" style="display:none">
<div class="tabs">
<div class="tab active" onclick="showTab('generate')">➕ Generate</div>
<div class="tab" onclick="showTab('manage')">⚙️ Manage</div>
<div class="tab" onclick="showTab('users')">👥 Users</div>
<div class="tab" onclick="showTab('logs')">📋 Logs</div>
</div>

<div id="generate" class="card">
<h2>Generate License</h2>
<div class="form-group"><label>Device ID</label><input type="text" id="deviceId" placeholder="Device ID from user..."></div>
<div class="form-group"><label>Username</label><input type="text" id="username" value="user"></div>
<div class="form-group"><label>Days</label><input type="number" id="days" value="30" min="1"></div>
<button onclick="generateLicense()">Generate License</button>
<div class="output" id="genOut">Waiting...</div>
</div>

<div id="manage" class="card" style="display:none">
<h2>Manage License</h2>
<div class="form-group"><label>License Key</label><input type="text" id="licenseKey" placeholder="License key..."></div>
<div class="form-group"><label>Extend Days</label><input type="number" id="extendDays" value="30" min="1"></div>
<button onclick="extendLicense()">📅 Extend</button>
<button class="danger" onclick="banUser()">🚫 Ban</button>
<div class="output" id="manageOut">Waiting...</div>
</div>

<div id="users" class="card" style="display:none">
<h2>All Users <span id="userCount"></span></h2>
<button onclick="loadUsers()">🔄 Refresh</button>
<div id="userTable"></div>
</div>

<div id="logs" class="card" style="display:none">
<h2>Usage Logs</h2>
<p style="color:#8b949e;font-size:13px">Logs available via API: <code>GET /admin/users</code></p>
</div>
</div>
</div>

<script>
let authToken = '';
function login() {
    const user = document.getElementById('adminUser').value;
    const pass = document.getElementById('adminPass').value;
    authToken = btoa(user + ':' + pass);
    document.getElementById('authForm').style.display = 'none';
    document.getElementById('mainContent').style.display = 'block';
}
function showTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    [...document.querySelectorAll('.card')].forEach(c => c.style.display = 'none');
    document.querySelector(`.tab[onclick*="'${tab}'"]`).classList.add('active');
    document.getElementById(tab).style.display = 'block';
}
async function api(method, endpoint, body) {
    try {
        const opts = {method, headers:{'Content-Type':'application/json','Authorization':'Basic '+authToken}};
        if(body) opts.body = JSON.stringify(body);
        const r = await fetch(endpoint, opts);
        return await r.json();
    } catch(e) { return {error:e.message}; }
}
async function generateLicense() {
    const out = document.getElementById('genOut');
    out.textContent = 'Generating...';
    const r = await api('POST', '/admin/generate', {
        device_id: document.getElementById('deviceId').value.trim(),
        username: document.getElementById('username').value.trim(),
        days: parseInt(document.getElementById('days').value)
    });
    out.textContent = JSON.stringify(r, null, 2);
    if(r.status === 'created') out.className = 'output success';
}
async function extendLicense() {
    const out = document.getElementById('manageOut');
    out.textContent = 'Extending...';
    const r = await api('POST', '/admin/extend', {
        license_key: document.getElementById('licenseKey').value.trim(),
        days: parseInt(document.getElementById('extendDays').value)
    });
    out.textContent = JSON.stringify(r, null, 2);
}
async function banUser() {
    const out = document.getElementById('manageOut');
    if(!confirm('Ban this user?')) return;
    out.textContent = 'Banning...';
    const r = await api('POST', '/admin/ban', {
        license_key: document.getElementById('licenseKey').value.trim()
    });
    out.textContent = JSON.stringify(r, null, 2);
}
async function loadUsers() {
    const out = document.getElementById('userTable');
    out.innerHTML = 'Loading...';
    const r = await api('GET', '/admin/users', null);
    if(!r.users) { out.innerHTML = JSON.stringify(r); return; }
    document.getElementById('userCount').textContent = '('+r.total+')';
    let html = '<table><tr><th>Key</th><th>Device</th><th>User</th><th>Expires</th><th>Status</th></tr>';
    r.users.forEach(u => {
        let cls = 'status-expired', lbl = 'Expired';
        if(u.is_banned) { cls = 'status-banned'; lbl = 'Banned'; }
        else if(u.is_active) { cls = 'status-active'; lbl = 'Active'; }
        html += `<tr><td>${u.license_key}</td><td>${(u.device_id||'').substring(0,12)}...</td><td>${u.username}</td><td>${(u.expires_at||'').substring(0,10)}</td><td class="${cls}">${lbl}</td></tr>`;
    });
    html += '</table>';
    out.innerHTML = html;
}
</script>
</body>
</html>"""

# ============== মেইন ==============
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
