#!/usr/bin/env python3
"""
Ridol FB Tool License Server v4.0
Author: Ridol Islam
License: MIT
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
import json
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

DB_FILE = 'licenses.json'
ADMIN_PASSWORD = 'Ridol123@'
CUSTOM_SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_sounds')
os.makedirs(CUSTOM_SOUNDS_DIR, exist_ok=True)

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return jsonify({
        'server': 'Ridol FB Tool License Server',
        'version': 'v4.0',
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

# ============ CUSTOM SOUND ROUTES ============
@app.route('/api/sounds/list')
@login_required
def list_sounds():
    sounds = []
    for f in os.listdir(CUSTOM_SOUNDS_DIR):
        if f.endswith(('.mp3', '.wav', '.ogg')):
            size = os.path.getsize(os.path.join(CUSTOM_SOUNDS_DIR, f))
            sounds.append({
                'name': f,
                'size': size,
                'size_mb': round(size / (1024 * 1024), 2)
            })
    return jsonify({'sounds': sounds})

@app.route('/api/sounds/upload', methods=['POST'])
@login_required
def upload_sound():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if not file.filename.lower().endswith(('.mp3', '.wav', '.ogg')):
            return jsonify({'success': False, 'message': 'Only MP3, WAV, OGG files allowed'})
        
        filename = 'background.wav'
        filepath = os.path.join(CUSTOM_SOUNDS_DIR, filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'message': f'✅ Sound uploaded successfully!',
            'filename': filename,
            'size': os.path.getsize(filepath)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/api/sounds/delete', methods=['POST'])
@login_required
def delete_sound():
    try:
        data = request.json
        filename = data.get('filename', '')
        if not filename:
            return jsonify({'success': False, 'message': 'No filename provided'})
        
        filepath = os.path.join(CUSTOM_SOUNDS_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': '✅ Sound deleted successfully'})
        return jsonify({'success': False, 'message': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/api/sounds/play', methods=['POST'])
@login_required
def play_sound():
    try:
        data = request.json
        filename = data.get('filename', '')
        if not filename:
            return jsonify({'success': False, 'message': 'No filename provided'})
        
        filepath = os.path.join(CUSTOM_SOUNDS_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=False)
        return jsonify({'success': False, 'message': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

# ============ LICENSE ROUTES ============
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template_string(LOGIN_HTML, error='❌ Incorrect password! Please try again.')
    
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_panel'))
    
    return render_template_string(LOGIN_HTML, error=None)

@app.route('/admin/panel')
@login_required
def admin_panel():
    return render_template_string(ADMIN_HTML)

@app.route('/admin/check')
@login_required
def admin_check():
    return jsonify({'authenticated': True})

@app.route('/admin/data')
@login_required
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
@login_required
def admin_create():
    try:
        data = request.json
        days = int(data.get('days', 30))
        notes = data.get('notes', '').strip()
        
        if days < 1:
            return jsonify({'success': False, 'message': '❌ Expiry days must be at least 1'})
        if days > 365:
            return jsonify({'success': False, 'message': '❌ Expiry days cannot exceed 365'})
        
        key = generate_license_key()
        expires = (datetime.now() + timedelta(days=days)).isoformat()
        
        db['users'][key] = {
            'created_at': datetime.now().isoformat(),
            'expires_at': expires,
            'banned': False,
            'notes': notes if notes else 'No notes',
            'device': ''
        }
        save_db(db)
        
        return jsonify({
            'success': True,
            'message': f'✅ License created successfully! Valid for {days} days.',
            'license_key': key,
            'expires_at': expires
        })
    except ValueError:
        return jsonify({'success': False, 'message': '❌ Invalid input! Please enter a valid number for days.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/admin/ban', methods=['POST'])
@login_required
def admin_ban():
    try:
        key = request.json.get('license_key', '')
        if not key:
            return jsonify({'success': False, 'message': '❌ No license key provided'})
        if key not in db['users']:
            return jsonify({'success': False, 'message': '❌ License key not found'})
        db['users'][key]['banned'] = True
        save_db(db)
        return jsonify({'success': True, 'message': '✅ License banned successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/admin/unban', methods=['POST'])
@login_required
def admin_unban():
    try:
        key = request.json.get('license_key', '')
        if not key:
            return jsonify({'success': False, 'message': '❌ No license key provided'})
        if key not in db['users']:
            return jsonify({'success': False, 'message': '❌ License key not found'})
        db['users'][key]['banned'] = False
        save_db(db)
        return jsonify({'success': True, 'message': '✅ License unbanned successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/admin/delete', methods=['POST'])
@login_required
def admin_delete():
    try:
        key = request.json.get('license_key', '')
        if not key:
            return jsonify({'success': False, 'message': '❌ No license key provided'})
        if key not in db['users']:
            return jsonify({'success': False, 'message': '❌ License key not found'})
        del db['users'][key]
        save_db(db)
        return jsonify({'success': True, 'message': '✅ License deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/admin/logout')
@login_required
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# ============================================================
# ============ LOGIN HTML WITH 3D + WRITING EFFECT ============
# ============================================================

LOGIN_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Admin Login - Ridol FB Tool</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: #0a0a1a;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Orbitron', sans-serif;
            overflow: hidden;
            perspective: 1200px;
        }
        
        /* Animated Background */
        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background: 
                radial-gradient(ellipse at 20% 50%, rgba(0, 255, 136, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 50%, rgba(0, 255, 136, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 100%, rgba(0, 255, 136, 0.05) 0%, transparent 30%);
            animation: bgPulse 4s ease-in-out infinite;
        }
        
        @keyframes bgPulse {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.1); }
        }
        
        /* Particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            overflow: hidden;
        }
        
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: #00ff88;
            border-radius: 50%;
            animation: float linear infinite;
            opacity: 0.3;
        }
        
        @keyframes float {
            0% { transform: translateY(100vh) scale(0); opacity: 0; }
            10% { opacity: 0.3; }
            90% { opacity: 0.3; }
            100% { transform: translateY(-100vh) scale(1); opacity: 0; }
        }
        
        /* Main Container */
        .login-container {
            position: relative;
            z-index: 1;
            background: rgba(17, 17, 34, 0.85);
            backdrop-filter: blur(20px);
            padding: 50px 45px;
            border-radius: 24px;
            max-width: 550px;
            width: 100%;
            transform: rotateY(5deg) rotateX(5deg) translateZ(50px);
            box-shadow: 
                0 30px 80px rgba(0, 0, 0, 0.8),
                0 0 40px rgba(0, 255, 136, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.1);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            animation: float3D 6s ease-in-out infinite;
        }
        
        @keyframes float3D {
            0%, 100% { transform: rotateY(5deg) rotateX(5deg) translateZ(50px); }
            50% { transform: rotateY(-3deg) rotateX(-3deg) translateZ(60px); }
        }
        
        .login-container:hover {
            transform: rotateY(0deg) rotateX(0deg) translateZ(80px);
            box-shadow: 0 40px 100px rgba(0, 0, 0, 0.9), 0 0 60px rgba(0, 255, 136, 0.2);
        }
        
        /* ===== 3D BIG TITLE WITH WRITING EFFECT ===== */
        .title-section {
            text-align: center;
            margin-bottom: 35px;
            position: relative;
        }
        
        .title-section .icon {
            font-size: 60px;
            display: block;
            margin-bottom: 10px;
            animation: iconPulse 3s ease-in-out infinite;
            filter: drop-shadow(0 0 40px rgba(0, 255, 136, 0.3));
        }
        
        @keyframes iconPulse {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.15) rotate(5deg); }
        }
        
        /* 3D Title - Large & Glowing */
        .title-3d {
            font-size: 42px;
            font-weight: 900;
            letter-spacing: 6px;
            display: block;
            text-align: center;
            position: relative;
            min-height: 70px;
            margin-bottom: 5px;
            text-shadow: 
                0 0 10px rgba(0, 255, 136, 0.3),
                0 0 20px rgba(0, 255, 136, 0.2),
                0 0 40px rgba(0, 255, 136, 0.1);
            transform: translateZ(30px);
        }
        
        /* Writing Effect Cursor */
        .cursor {
            display: inline-block;
            width: 4px;
            height: 42px;
            background: #00ff88;
            margin-left: 4px;
            vertical-align: middle;
            animation: blink 0.8s step-end infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
        
        /* Gradient Text for Title */
        .title-text {
            background: linear-gradient(135deg, #00ff88 0%, #00ff88 30%, #44ffaa 50%, #4488ff 70%, #00ff88 100%);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientMove 3s ease-in-out infinite;
            text-shadow: none;
            position: relative;
        }
        
        @keyframes gradientMove {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* 3D Shadow Layer */
        .title-3d::before {
            content: 'RIDOL FB TOOL';
            position: absolute;
            top: 4px;
            left: 4px;
            color: rgba(0, 255, 136, 0.1);
            z-index: -1;
            filter: blur(8px);
            -webkit-text-fill-color: rgba(0, 255, 136, 0.1);
        }
        
        /* Subtitle with writing effect */
        .subtitle-3d {
            font-size: 12px;
            letter-spacing: 8px;
            color: rgba(255, 255, 255, 0.2);
            margin-top: 5px;
            font-weight: 400;
            min-height: 20px;
        }
        
        .subtitle-3d .sub-cursor {
            display: inline-block;
            width: 3px;
            height: 14px;
            background: rgba(255, 255, 255, 0.2);
            vertical-align: middle;
            margin-left: 2px;
            animation: blink 0.8s step-end infinite;
        }
        
        .version-badge {
            display: inline-block;
            background: rgba(0, 255, 136, 0.15);
            border: 1px solid rgba(0, 255, 136, 0.2);
            padding: 4px 20px;
            border-radius: 20px;
            color: #00ff88;
            font-size: 11px;
            margin-top: 10px;
            font-weight: 700;
            letter-spacing: 3px;
            animation: badgeGlow 2s ease-in-out infinite;
            transform: translateZ(10px);
        }
        
        @keyframes badgeGlow {
            0%, 100% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.05); }
            50% { box-shadow: 0 0 40px rgba(0, 255, 136, 0.2); }
        }
        
        /* Form */
        .form-group {
            margin-bottom: 22px;
            position: relative;
        }
        
        .form-group label {
            color: rgba(255, 255, 255, 0.4);
            font-size: 10px;
            display: block;
            margin-bottom: 8px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        .form-group .input-wrapper {
            position: relative;
            transform: translateZ(10px);
        }
        
        .form-group .input-wrapper .lock-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.15);
            font-size: 18px;
            transition: all 0.3s ease;
        }
        
        .form-group input {
            width: 100%;
            padding: 16px 16px 16px 50px;
            background: rgba(26, 26, 46, 0.8);
            border: 2px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            color: #fff;
            font-size: 15px;
            font-family: 'Orbitron', sans-serif;
            transition: all 0.3s ease;
            outline: none;
            backdrop-filter: blur(10px);
        }
        
        .form-group input:focus {
            border-color: #00ff88;
            box-shadow: 0 0 40px rgba(0, 255, 136, 0.1), inset 0 0 20px rgba(0, 255, 136, 0.05);
            transform: translateZ(20px) scale(1.02);
        }
        
        .form-group input:focus + .lock-icon,
        .form-group input:focus ~ .lock-icon {
            color: #00ff88;
        }
        
        .form-group input::placeholder {
            color: rgba(255, 255, 255, 0.1);
            font-size: 12px;
            letter-spacing: 2px;
        }
        
        .btn-login {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #00ff88, #00cc77);
            border: none;
            border-radius: 14px;
            color: #000;
            font-size: 16px;
            font-weight: 900;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            letter-spacing: 3px;
            font-family: 'Orbitron', sans-serif;
            text-transform: uppercase;
            position: relative;
            overflow: hidden;
            transform: translateZ(10px);
        }
        
        .btn-login::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.15), transparent);
            transform: rotate(45deg);
            animation: btnShine 3s ease-in-out infinite;
        }
        
        @keyframes btnShine {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(100%) rotate(45deg); }
        }
        
        .btn-login:hover {
            transform: translateZ(30px) scale(1.03);
            box-shadow: 0 20px 60px rgba(0, 255, 136, 0.4);
        }
        
        .btn-login:active {
            transform: translateZ(5px) scale(0.97);
        }
        
        .error-msg {
            background: rgba(255, 68, 68, 0.1);
            border: 1px solid rgba(255, 68, 68, 0.2);
            color: #ff4444;
            padding: 14px 18px;
            border-radius: 12px;
            font-size: 13px;
            margin-bottom: 20px;
            text-align: center;
            animation: shake 0.5s ease-in-out;
            font-weight: 400;
            letter-spacing: 1px;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0) rotateY(0deg); }
            25% { transform: translateX(-10px) rotateY(-3deg); }
            75% { transform: translateX(10px) rotateY(3deg); }
        }
        
        .login-footer {
            text-align: center;
            margin-top: 25px;
            color: rgba(255, 255, 255, 0.05);
            font-size: 9px;
            letter-spacing: 5px;
        }
        
        .login-footer .brand {
            color: rgba(0, 255, 136, 0.2);
            font-weight: 700;
        }
        
        .hint {
            text-align: center;
            color: rgba(255, 255, 255, 0.05);
            font-size: 10px;
            margin-top: 15px;
            letter-spacing: 3px;
        }
        
        .hint span {
            background: rgba(26, 26, 46, 0.3);
            padding: 4px 14px;
            border-radius: 6px;
            font-family: monospace;
            color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.03);
        }
        
        @media (max-width: 480px) {
            .login-container {
                padding: 30px 20px;
                margin: 20px;
                transform: rotateY(0deg) rotateX(0deg) translateZ(0px) !important;
            }
            .title-3d { font-size: 26px; letter-spacing: 3px; }
            .title-3d::before { font-size: 26px; }
            .cursor { height: 28px; }
            .login-container:hover {
                transform: rotateY(0deg) rotateX(0deg) translateZ(0px) !important;
            }
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    <div class="particles" id="particles"></div>
    
    <div class="login-container">
        <div class="title-section">
            <span class="icon">🔐</span>
            
            <!-- 3D BIG TITLE WITH WRITING EFFECT -->
            <div class="title-3d">
                <span class="title-text" id="titleText"></span>
                <span class="cursor" id="cursor"></span>
            </div>
            
            <!-- Subtitle with writing effect -->
            <div class="subtitle-3d">
                <span id="subText"></span>
                <span class="sub-cursor" id="subCursor"></span>
            </div>
            
            <span class="version-badge">✦ v4.0 ✦</span>
        </div>
        
        {% if error %}
        <div class="error-msg">{{ error }}</div>
        {% endif %}
        
        <form method="POST" action="/admin">
            <div class="form-group">
                <label>🔑 Admin Password</label>
                <div class="input-wrapper">
                    <span class="lock-icon">🔒</span>
                    <input type="password" name="password" placeholder="Enter your admin password" required autofocus>
                </div>
            </div>
            <button type="submit" class="btn-login">🚀 Access Panel</button>
        </form>
        
        <div class="hint">
            <span>🔑 Hint: Admin Password</span>
        </div>
        
        <div class="login-footer">
            <span class="brand">✦ RIDOL FB TOOL ✦</span> • v4.0
        </div>
    </div>
    
    <script>
        // ===== WRITING EFFECT =====
        const titleText = "RIDOL FB TOOL";
        const subText = "ADMIN AUTHENTICATION";
        
        let titleIndex = 0;
        let subIndex = 0;
        let isTitleComplete = false;
        
        function typeTitle() {
            if (titleIndex < titleText.length) {
                document.getElementById('titleText').textContent += titleText.charAt(titleIndex);
                titleIndex++;
                setTimeout(typeTitle, 80 + Math.random() * 40);
            } else {
                isTitleComplete = true;
                // Remove cursor after title complete
                document.getElementById('cursor').style.display = 'none';
                // Start subtitle after a delay
                setTimeout(typeSubtitle, 300);
            }
        }
        
        function typeSubtitle() {
            if (subIndex < subText.length) {
                document.getElementById('subText').textContent += subText.charAt(subIndex);
                subIndex++;
                setTimeout(typeSubtitle, 50 + Math.random() * 30);
            } else {
                // Remove subtitle cursor
                document.getElementById('subCursor').style.display = 'none';
            }
        }
        
        // Start typing on page load
        window.onload = function() {
            // Clear any existing text
            document.getElementById('titleText').textContent = '';
            document.getElementById('subText').textContent = '';
            setTimeout(typeTitle, 500);
        };
        
        // ===== PARTICLES =====
        (function createParticles() {
            const container = document.getElementById('particles');
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.width = (Math.random() * 3 + 2) + 'px';
                particle.style.height = particle.style.width;
                particle.style.animationDuration = (Math.random() * 20 + 10) + 's';
                particle.style.animationDelay = (Math.random() * 10) + 's';
                particle.style.opacity = Math.random() * 0.3 + 0.1;
                container.appendChild(particle);
            }
        })();
    </script>
</body>
</html>'''

# ============================================================
# ============ ADMIN HTML WITH 3D UI ============
# ============================================================

ADMIN_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Admin Panel - Ridol FB Tool</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: #0a0a1a;
            color: #fff;
            padding: 20px;
            min-height: 100vh;
            font-family: 'Orbitron', sans-serif;
            perspective: 1200px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* 3D Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 25px 30px;
            background: rgba(17, 17, 34, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(0, 255, 136, 0.1);
            transform: rotateX(2deg) translateZ(20px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .header:hover {
            transform: rotateX(0deg) translateZ(40px);
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.7), 0 0 40px rgba(0, 255, 136, 0.05);
        }
        
        .header-left h1 {
            font-size: 22px;
            font-weight: 900;
            background: linear-gradient(135deg, #00ff88, #00ff88 40%, #4488ff 70%, #00ff88);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientMove 3s ease-in-out infinite;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: 2px;
        }
        
        @keyframes gradientMove {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .header-left .subtitle {
            color: rgba(255, 255, 255, 0.2);
            font-size: 10px;
            letter-spacing: 4px;
            margin-top: 5px;
        }
        
        .header-left .version-badge {
            display: inline-block;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.15);
            padding: 2px 14px;
            border-radius: 20px;
            color: #00ff88;
            font-size: 9px;
            margin-left: 10px;
            font-weight: 700;
            letter-spacing: 2px;
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header-right .badge {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.15);
            padding: 6px 16px;
            border-radius: 20px;
            color: #00ff88;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 2px;
        }
        
        .btn-logout {
            background: rgba(255, 68, 68, 0.1);
            border: 1px solid rgba(255, 68, 68, 0.2);
            color: #ff4444;
            padding: 10px 24px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 700;
            font-size: 11px;
            font-family: 'Orbitron', sans-serif;
            transition: all 0.3s ease;
            letter-spacing: 2px;
        }
        
        .btn-logout:hover {
            background: rgba(255, 68, 68, 0.2);
            transform: translateZ(10px);
            box-shadow: 0 10px 30px rgba(255, 68, 68, 0.1);
        }
        
        /* 3D Cards */
        .card {
            background: rgba(17, 17, 34, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 28px;
            margin-bottom: 24px;
            border: 1px solid rgba(0, 255, 136, 0.05);
            transform: rotateX(2deg) translateZ(10px);
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .card:hover {
            transform: rotateX(0deg) translateZ(30px);
            box-shadow: 0 25px 70px rgba(0, 0, 0, 0.5), 0 0 30px rgba(0, 255, 136, 0.03);
            border-color: rgba(0, 255, 136, 0.1);
        }
        
        .card h2 {
            color: #00ff88;
            font-size: 15px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 700;
            letter-spacing: 3px;
        }
        
        .card h2 .icon { font-size: 20px; }
        
        /* Stats */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
        }
        
        .stat-box {
            text-align: center;
            padding: 20px 15px;
            background: rgba(26, 26, 46, 0.4);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.02);
            transition: all 0.3s ease;
            transform: translateZ(5px);
        }
        
        .stat-box:hover {
            transform: translateZ(20px);
            border-color: rgba(0, 255, 136, 0.05);
        }
        
        .stat-box .number {
            font-size: 28px;
            font-weight: 900;
        }
        
        .stat-box .label {
            color: rgba(255, 255, 255, 0.2);
            font-size: 9px;
            margin-top: 6px;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        /* Form */
        .flex { display: flex; gap: 15px; flex-wrap: wrap; }
        .flex-grow { flex: 1; min-width: 180px; }
        
        .form-group { margin-bottom: 15px; }
        .form-group label {
            color: rgba(255, 255, 255, 0.3);
            font-size: 9px;
            display: block;
            margin-bottom: 6px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 14px 18px;
            background: rgba(26, 26, 46, 0.5);
            border: 2px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            color: #fff;
            font-size: 13px;
            font-family: 'Orbitron', sans-serif;
            transition: all 0.3s ease;
            outline: none;
        }
        
        .form-group input:focus, .form-group select:focus {
            border-color: #00ff88;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.05);
            transform: translateZ(10px);
        }
        
        /* Buttons */
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 700;
            font-size: 12px;
            font-family: 'Orbitron', sans-serif;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            letter-spacing: 2px;
            transform: translateZ(5px);
        }
        
        .btn:hover { transform: translateZ(20px) scale(1.02); }
        
        .btn-green { background: linear-gradient(135deg, #00ff88, #00cc77); color: #000; }
        .btn-green:hover { box-shadow: 0 15px 40px rgba(0, 255, 136, 0.3); }
        
        .btn-red { background: linear-gradient(135deg, #ff4444, #cc0000); color: #fff; }
        .btn-red:hover { box-shadow: 0 15px 40px rgba(255, 68, 68, 0.3); }
        
        .btn-blue { background: linear-gradient(135deg, #4488ff, #2255cc); color: #fff; }
        .btn-blue:hover { box-shadow: 0 15px 40px rgba(68, 136, 255, 0.3); }
        
        .btn-orange { background: linear-gradient(135deg, #ff8800, #cc6600); color: #fff; }
        .btn-orange:hover { box-shadow: 0 15px 40px rgba(255, 136, 0, 0.3); }
        
        .btn-purple { background: linear-gradient(135deg, #aa44ff, #7722cc); color: #fff; }
        .btn-purple:hover { box-shadow: 0 15px 40px rgba(170, 68, 255, 0.3); }
        
        .btn-sm { padding: 8px 14px; font-size: 9px; }
        
        /* Messages */
        .msg {
            padding: 16px 22px;
            border-radius: 14px;
            margin: 10px 0;
            display: none;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 2px;
            transform: translateZ(10px);
        }
        .msg-success { background: rgba(0, 255, 136, 0.08); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.15); }
        .msg-error { background: rgba(255, 68, 68, 0.08); color: #ff4444; border: 1px solid rgba(255, 68, 68, 0.15); }
        .msg-info { background: rgba(68, 136, 255, 0.08); color: #4488ff; border: 1px solid rgba(68, 136, 255, 0.15); }
        
        /* New Key Box */
        .new-key-box {
            margin-top: 18px;
            padding: 24px;
            background: rgba(0, 255, 136, 0.03);
            border-radius: 14px;
            border: 2px solid rgba(0, 255, 136, 0.15);
            display: none;
            transform: translateZ(10px);
        }
        
        .new-key-box .key {
            font-size: 18px;
            font-family: monospace;
            color: #00ff88;
            display: block;
            margin: 12px 0;
            padding: 16px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            word-break: break-all;
            letter-spacing: 2px;
        }
        
        /* Table */
        .table-wrapper { overflow-x: auto; margin-top: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td {
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.02);
            font-size: 11px;
        }
        th {
            color: rgba(0, 255, 136, 0.4);
            font-weight: 700;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 3px;
        }
        td code {
            background: rgba(26, 26, 46, 0.3);
            padding: 2px 10px;
            border-radius: 6px;
            font-size: 9px;
            font-family: monospace;
        }
        
        .badge {
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 1px;
        }
        .badge-active { background: rgba(0, 255, 136, 0.08); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.15); }
        .badge-expired { background: rgba(255, 68, 68, 0.08); color: #ff4444; border: 1px solid rgba(255, 68, 68, 0.15); }
        .badge-banned { background: rgba(255, 136, 0, 0.08); color: #ff8800; border: 1px solid rgba(255, 136, 0, 0.15); }
        
        /* Search */
        .search-box {
            display: flex;
            gap: 12px;
            margin-bottom: 18px;
            flex-wrap: wrap;
        }
        .search-box input {
            flex: 1;
            min-width: 180px;
            padding: 12px 18px;
            background: rgba(26, 26, 46, 0.5);
            border: 2px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            color: #fff;
            font-size: 12px;
            font-family: 'Orbitron', sans-serif;
            outline: none;
            transition: all 0.3s ease;
        }
        .search-box input:focus {
            border-color: #00ff88;
            transform: translateZ(10px);
        }
        
        /* Upload Area */
        .upload-area {
            border: 2px dashed rgba(0, 255, 136, 0.08);
            border-radius: 14px;
            padding: 30px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .upload-area:hover {
            border-color: rgba(0, 255, 136, 0.2);
            background: rgba(0, 255, 136, 0.02);
        }
        .upload-area.dragover {
            border-color: #00ff88;
            background: rgba(0, 255, 136, 0.05);
        }
        .upload-area .icon { font-size: 36px; display: block; margin-bottom: 10px; }
        .upload-area p { color: rgba(255, 255, 255, 0.2); font-size: 11px; letter-spacing: 2px; }
        .upload-area .supported { color: rgba(255, 255, 255, 0.08); font-size: 9px; margin-top: 5px; }
        
        .sound-list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: rgba(26, 26, 46, 0.2);
            border-radius: 10px;
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }
        .sound-list-item:hover {
            background: rgba(26, 26, 46, 0.4);
            transform: translateZ(10px);
        }
        .sound-list-item .info { display: flex; gap: 15px; align-items: center; }
        .sound-list-item .info .name { font-size: 12px; }
        .sound-list-item .info .size { color: rgba(255, 255, 255, 0.15); font-size: 9px; }
        
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.03);
            font-size: 9px;
            margin-top: 40px;
            padding: 20px;
            letter-spacing: 5px;
        }
        
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        .status-dot.online { background: #00ff88; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        @media (max-width: 768px) {
            .header { flex-direction: column; align-items: flex-start; }
            .header-right { width: 100%; justify-content: flex-start; flex-wrap: wrap; }
            .card { padding: 20px; }
            .stat-box .number { font-size: 22px; }
        }
        @media (max-width: 480px) {
            body { padding: 10px; }
            .header-left h1 { font-size: 16px; }
            .card { padding: 16px; }
            .stats { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <h1>
                    <span>🔐</span>
                    RIDOL FB TOOL
                    <span class="version-badge">✦ v4.0 ✦</span>
                </h1>
                <div class="subtitle">
                    <span class="status-dot online"></span>
                    ADMIN PANEL • LICENSE MANAGEMENT
                </div>
            </div>
            <div class="header-right">
                <span class="badge">👑 ADMIN</span>
                <a href="/admin/logout"><button class="btn-logout">🚪 LOGOUT</button></a>
            </div>
        </div>
        
        <div id="msg" class="msg"></div>
        
        <!-- Sound Upload -->
        <div class="card">
            <h2><span class="icon">🎵</span> Custom Background Sound</h2>
            <div class="upload-area" id="dropZone" onclick="document.getElementById('fileInput').click()">
                <span class="icon">📤</span>
                <p>Drop your MP3 / WAV / OGG file here</p>
                <p class="supported">or click to browse • Max 50MB</p>
                <input type="file" id="fileInput" accept=".mp3,.wav,.ogg" style="display:none" onchange="uploadSound(this.files)">
            </div>
            <div style="margin-top:15px" id="soundList"></div>
        </div>
        
        <!-- Create License -->
        <div class="card">
            <h2><span class="icon">➕</span> Create License</h2>
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
        
        <!-- Statistics -->
        <div class="card">
            <h2><span class="icon">📊</span> Statistics</h2>
            <div class="stats">
                <div class="stat-box"><div class="number" style="color:#00ff88" id="s_total">0</div><div class="label">Total</div></div>
                <div class="stat-box"><div class="number" style="color:#00ff88" id="s_active">0</div><div class="label">✅ Active</div></div>
                <div class="stat-box"><div class="number" style="color:#ff8800" id="s_expired">0</div><div class="label">⏰ Expired</div></div>
                <div class="stat-box"><div class="number" style="color:#ff4444" id="s_banned">0</div><div class="label">🚫 Banned</div></div>
                <div class="stat-box"><div class="number" style="color:#4488ff" id="s_devices">0</div><div class="label">📱 Devices</div></div>
            </div>
        </div>
        
        <!-- License List -->
        <div class="card">
            <h2><span class="icon">👥</span> License Management</h2>
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
        
        <div class="footer">✦ RIDOL FB TOOL v4.0 • LICENSE SERVER ✦</div>
    </div>
    
    <script>
        let allUsers = {};
        let filteredUsers = {};
        let lastCreatedKey = '';
        
        function showMsg(text, type) {
            const el = document.getElementById('msg');
            el.textContent = text;
            el.className = 'msg msg-' + type;
            el.style.display = 'block';
            setTimeout(() => { el.style.display = 'none'; }, 6000);
        }
        
        async function apiCall(url, method, data) {
            try {
                const res = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: data ? JSON.stringify(data) : undefined
                });
                if (res.status === 401 || res.status === 302) {
                    window.location.href = '/admin';
                    return null;
                }
                return await res.json();
            } catch (e) {
                showMsg('❌ Network Error: ' + e.message, 'error');
                return null;
            }
        }
        
        // Sound Functions
        const dropZone = document.getElementById('dropZone');
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => { dropZone.classList.remove('dragover'); });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) uploadSound(e.dataTransfer.files);
        });
        
        async function uploadSound(files) {
            if (!files || files.length === 0) { showMsg('❌ No file selected', 'error'); return; }
            const file = files[0];
            if (!file.name.match(/\.(mp3|wav|ogg)$/i)) { showMsg('❌ Only MP3, WAV, OGG allowed', 'error'); return; }
            if (file.size > 50 * 1024 * 1024) { showMsg('❌ Max 50MB', 'error'); return; }
            
            const formData = new FormData();
            formData.append('file', file);
            try {
                showMsg('⏳ Uploading...', 'info');
                const res = await fetch('/api/sounds/upload', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.success) { showMsg('✅ ' + data.message, 'success'); loadSounds(); }
                else { showMsg('❌ ' + data.message, 'error'); }
            } catch (e) { showMsg('❌ Upload failed', 'error'); }
        }
        
        async function loadSounds() {
            try {
                const res = await fetch('/api/sounds/list');
                const data = await res.json();
                const list = document.getElementById('soundList');
                if (data.sounds && data.sounds.length > 0) {
                    let html = '<div style="margin-top:10px"><strong style="color:rgba(255,255,255,0.2);font-size:10px;letter-spacing:3px">CURRENT SOUNDS:</strong></div>';
                    data.sounds.forEach(s => {
                        html += `
                            <div class="sound-list-item">
                                <div class="info"><span style="font-size:18px">🎵</span><span class="name">${s.name}</span><span class="size">${s.size_mb} MB</span></div>
                                <div style="display:flex;gap:8px">
                                    <button class="btn btn-blue btn-sm" onclick="playSound('${s.name}')">▶ PLAY</button>
                                    <button class="btn btn-red btn-sm" onclick="deleteSound('${s.name}')">✕</button>
                                </div>
                            </div>
                        `;
                    });
                    list.innerHTML = html;
                } else {
                    list.innerHTML = '<div style="text-align:center;color:rgba(255,255,255,0.05);padding:20px;font-size:11px;letter-spacing:3px">No custom sounds uploaded</div>';
                }
            } catch (e) {}
        }
        
        async function playSound(filename) {
            try {
                const res = await fetch('/api/sounds/play', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename }) });
                if (res.ok) {
                    const blob = await res.blob();
                    const audio = new Audio(URL.createObjectURL(blob));
                    audio.play();
                    showMsg('▶ Playing: ' + filename, 'info');
                }
            } catch (e) { showMsg('❌ Play failed', 'error'); }
        }
        
        async function deleteSound(filename) {
            if (!confirm('Delete ' + filename + '?')) return;
            try {
                const res = await fetch('/api/sounds/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename }) });
                const data = await res.json();
                if (data.success) { showMsg('✅ ' + data.message, 'success'); loadSounds(); }
                else { showMsg('❌ ' + data.message, 'error'); }
            } catch (e) { showMsg('❌ Delete failed', 'error'); }
        }
        
        // License Functions
        async function createLic() {
            const days = parseInt(document.getElementById('days').value) || 30;
            const notes = document.getElementById('notes').value || '';
            if (days < 1) { showMsg('❌ At least 1 day', 'error'); return; }
            if (days > 365) { showMsg('❌ Max 365 days', 'error'); return; }
            
            showMsg('⏳ Generating...', 'info');
            const result = await apiCall('/admin/create', 'POST', { days, notes });
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
        }
        
        function copyKey() {
            const key = document.getElementById('key_display').textContent;
            navigator.clipboard.writeText(key).then(() => showMsg('📋 Copied!', 'success'))
            .catch(() => {
                const ta = document.createElement('textarea');
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
        
        async function toggleBan(key, isBanned) {
            const action = isBanned ? 'unban' : 'ban';
            showMsg('⏳ Processing...', 'info');
            const result = await apiCall('/admin/' + action, 'POST', { license_key: key });
            if (result && result.success) { showMsg('✅ ' + result.message, 'success'); refreshAll(); }
            else { showMsg(result ? result.message : '❌ Failed', 'error'); }
        }
        
        async function deleteLic(key) {
            if (!confirm('⚠️ Delete ' + key + '?')) return;
            showMsg('⏳ Deleting...', 'info');
            const result = await apiCall('/admin/delete', 'POST', { license_key: key });
            if (result && result.success) { showMsg('✅ ' + result.message, 'success'); refreshAll(); }
            else { showMsg(result ? result.message : '❌ Failed', 'error'); }
        }
        
        function renderTable(users) {
            const tbody = document.getElementById('tbody');
            tbody.innerHTML = '';
            const now = new Date();
            const keys = Object.keys(users);
            if (keys.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:rgba(255,255,255,0.05);padding:40px;letter-spacing:3px">No licenses found</td></tr>';
                return;
            }
            keys.forEach(key => {
                const u = users[key];
                const expires = u.expires_at ? new Date(u.expires_at) : null;
                const isExpired = expires && now > expires;
                const isBanned = u.banned || false;
                let status = 'Active', badge = 'badge-active';
                if (isBanned) { status = 'Banned'; badge = 'badge-banned'; }
                else if (isExpired) { status = 'Expired'; badge = 'badge-expired'; }
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><code>${key}</code></td>
                    <td style="font-size:10px">${u.expires_at || 'Never'}</td>
                    <td><span class="badge ${badge}">${status}</span></td>
                    <td style="font-size:10px;color:rgba(255,255,255,0.15)">${u.device || '-'}</td>
                    <td style="font-size:9px;color:rgba(255,255,255,0.1)">${u.created_at || '-'}</td>
                    <td style="font-size:10px;color:rgba(255,255,255,0.15)">${u.notes || '-'}</td>
                    <td style="text-align:center;white-space:nowrap">
                        <button class="btn ${isBanned ? 'btn-green' : 'btn-red'} btn-sm" onclick="toggleBan('${key}', ${isBanned})" style="margin:2px">${isBanned ? 'UNBAN' : 'BAN'}</button>
                        <button class="btn btn-red btn-sm" onclick="deleteLic('${key}')" style="margin:2px">✕</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        async function refreshAll() {
            const data = await apiCall('/admin/data', 'GET');
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
        }
        
        function searchLic() {
            const q = document.getElementById('search').value.toLowerCase().trim();
            if (!q) { filteredUsers = allUsers; renderTable(filteredUsers); return; }
            filteredUsers = {};
            Object.keys(allUsers).forEach(key => {
                const u = allUsers[key];
                if (key.toLowerCase().includes(q) || (u.device && u.device.toLowerCase().includes(q)) || (u.notes && u.notes.toLowerCase().includes(q))) {
                    filteredUsers[key] = u;
                }
            });
            renderTable(filteredUsers);
            showMsg('🔍 Found ' + Object.keys(filteredUsers).length + ' result(s)', 'info');
        }
        
        refreshAll();
        loadSounds();
        setInterval(refreshAll, 30000);
    </script>
</body>
</html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)