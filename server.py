#!/usr/bin/env python3
"""
Ridol FB Tool License Server v4.0 - Firebase Integration
Author: Ridol Islam
License: MIT
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
from flask_cors import CORS
import os
import sys
import json
import uuid
import base64
from datetime import datetime, timedelta
from functools import wraps
import logging
import io
import requests
import traceback

# ==================== FIREBASE CONFIGURATION ====================
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("[-] Firebase not installed. Install: pip install firebase-admin")

# Initialize Firebase
firebase_db = None
firebase_bucket = None

if FIREBASE_AVAILABLE:
    try:
        # Load Firebase config
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase_config.json')
        
        if os.path.exists(config_path):
            cred = credentials.Certificate(config_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'ridol-fb-tool.firebasestorage.app'
            })
            firebase_db = firestore.client()
            firebase_bucket = storage.bucket()
            print("[+] Firebase Connected Successfully!")
        else:
            print("[-] firebase_config.json not found!")
            FIREBASE_AVAILABLE = False
    except Exception as e:
        print(f"[-] Firebase Error: {e}")
        FIREBASE_AVAILABLE = False

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

ADMIN_PASSWORD = 'Ridol123@'

# ==================== FIREBASE DATABASE FUNCTIONS ====================

def firebase_get_user(license_key):
    """Get user by license key from Firebase"""
    if firebase_db:
        try:
            doc = firebase_db.collection('users').document(license_key).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"[-] Firebase get user error: {e}")
    return None

def firebase_get_users():
    """Get all users from Firebase"""
    if firebase_db:
        try:
            docs = firebase_db.collection('users').stream()
            users = []
            for doc in docs:
                user = doc.to_dict()
                user['license_key'] = doc.id
                users.append(user)
            return users
        except Exception as e:
            print(f"[-] Firebase get users error: {e}")
    return []

def firebase_save_user(user_data):
    """Save user to Firebase"""
    if firebase_db:
        try:
            license_key = user_data['license_key']
            if 'created_at' not in user_data:
                user_data['created_at'] = datetime.now().isoformat()
            firebase_db.collection('users').document(license_key).set(user_data)
            return True
        except Exception as e:
            print(f"[-] Firebase save user error: {e}")
    return False

def firebase_delete_user(license_key):
    """Delete user from Firebase"""
    if firebase_db:
        try:
            firebase_db.collection('users').document(license_key).delete()
            return True
        except Exception as e:
            print(f"[-] Firebase delete user error: {e}")
    return False

def firebase_get_devices():
    """Get all devices from Firebase"""
    if firebase_db:
        try:
            docs = firebase_db.collection('devices').stream()
            devices = []
            for doc in docs:
                device = doc.to_dict()
                device['device_serial'] = doc.id
                devices.append(device)
            return devices
        except Exception as e:
            print(f"[-] Firebase get devices error: {e}")
    return []

def firebase_get_device(device_serial):
    """Get device by serial from Firebase"""
    if firebase_db:
        try:
            doc = firebase_db.collection('devices').document(device_serial).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"[-] Firebase get device error: {e}")
    return None

def firebase_save_device(device_data):
    """Save device to Firebase"""
    if firebase_db:
        try:
            device_serial = device_data['device_serial']
            if 'created_at' not in device_data:
                device_data['created_at'] = datetime.now().isoformat()
            firebase_db.collection('devices').document(device_serial).set(device_data)
            return True
        except Exception as e:
            print(f"[-] Firebase save device error: {e}")
    return False

# ==================== FIREBASE STORAGE FUNCTIONS ====================

def firebase_upload_sound(file_data, filename):
    """Upload sound file to Firebase Storage"""
    if firebase_bucket:
        try:
            blob = firebase_bucket.blob(f'sounds/{filename}')
            blob.upload_from_string(file_data, content_type='audio/mpeg' if filename.endswith('.mp3') else 'audio/wav')
            blob.make_public()
            
            # Save metadata to Firestore
            sound_data = {
                'filename': filename,
                'size': len(file_data),
                'uploaded_at': datetime.now().isoformat(),
                'url': blob.public_url,
                'content_type': 'audio/mpeg' if filename.endswith('.mp3') else 'audio/wav'
            }
            firebase_db.collection('sounds').document(filename).set(sound_data)
            
            return blob.public_url
        except Exception as e:
            print(f"[-] Firebase upload error: {e}")
    return None

def firebase_get_sound(filename):
    """Get sound file from Firebase Storage"""
    if firebase_bucket:
        try:
            blob = firebase_bucket.blob(f'sounds/{filename}')
            if blob.exists():
                return blob.download_as_bytes()
        except Exception as e:
            print(f"[-] Firebase get sound error: {e}")
    return None

def firebase_delete_sound(filename):
    """Delete sound file from Firebase Storage"""
    if firebase_bucket:
        try:
            blob = firebase_bucket.blob(f'sounds/{filename}')
            if blob.exists():
                blob.delete()
                firebase_db.collection('sounds').document(filename).delete()
                return True
        except Exception as e:
            print(f"[-] Firebase delete sound error: {e}")
    return False

def firebase_get_all_sounds():
    """Get all sound metadata from Firebase"""
    if firebase_db:
        try:
            docs = firebase_db.collection('sounds').stream()
            sounds = []
            for doc in docs:
                sound = doc.to_dict()
                sounds.append({
                    'name': sound.get('filename', doc.id),
                    'size': sound.get('size', 0),
                    'size_mb': round(sound.get('size', 0) / (1024 * 1024), 2),
                    'uploaded_at': sound.get('uploaded_at', 'N/A'),
                    'url': sound.get('url', '')
                })
            return sounds
        except Exception as e:
            print(f"[-] Firebase get sounds error: {e}")
    return []

# ==================== LICENSE FUNCTIONS ====================

def generate_license_key():
    return f'RIDOL-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:8].upper()}'

def validate_license(key, device_serial):
    user = firebase_get_user(key)
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
        firebase_save_device(device_data)
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
        users = firebase_get_users()
        devices = firebase_get_devices()
        sounds = firebase_get_all_sounds()
        
        return jsonify({
            'server': 'Ridol FB Tool License Server',
            'version': '4.0',
            'status': 'online',
            'database': 'Firebase Firestore',
            'storage': 'Firebase Storage',
            'users': len(users),
            'devices': len(devices),
            'sounds': len(sounds),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/ping')
def ping():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '4.0',
        'database': 'Firebase Firestore',
        'storage': 'Firebase Storage'
    })

@app.route('/api/v1/status')
def api_status():
    try:
        users = firebase_get_users()
        devices = firebase_get_devices()
        sounds = firebase_get_all_sounds()
        
        return jsonify({
            'status': 'online',
            'version': '4.0',
            'timestamp': datetime.now().isoformat(),
            'database': 'Firebase Firestore',
            'storage': 'Firebase Storage',
            'license_count': len(users),
            'device_count': len(devices),
            'sound_files': [s['name'] for s in sounds],
            'sound_exists': len(sounds) > 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/sound/status')
def api_sound_status():
    try:
        sounds = firebase_get_all_sounds()
        return jsonify({
            'exists': len(sounds) > 0,
            'sounds': sounds,
            'count': len(sounds)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/sound/download/<filename>')
def api_download_sound(filename):
    try:
        if not filename.endswith(('.mp3', '.wav', '.ogg')):
            return jsonify({'error': 'Invalid file type'}), 400
        
        file_data = firebase_get_sound(filename)
        if file_data:
            mimetype = 'audio/mpeg' if filename.endswith('.mp3') else 'audio/wav'
            return send_file(
                io.BytesIO(file_data),
                as_attachment=True,
                download_name=filename,
                mimetype=mimetype
            )
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/sound/download')
def api_download_sound_default():
    try:
        sounds = firebase_get_all_sounds()
        if sounds:
            for s in sounds:
                if s['name'].endswith('.mp3'):
                    return api_download_sound(s['name'])
            return api_download_sound(sounds[0]['name'])
        return jsonify({'error': 'No sound found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/sound/upload', methods=['POST'])
@login_required
def api_upload_sound():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.mp3', '.wav', '.ogg']:
            return jsonify({'success': False, 'message': 'Only MP3, WAV, OGG allowed'})
        
        file_data = file.read()
        file_size = len(file_data)
        if file_size == 0:
            return jsonify({'success': False, 'message': 'File is empty'})
        
        if file_size > 50 * 1024 * 1024:
            return jsonify({'success': False, 'message': f'File too large: {file_size / (1024*1024):.2f} MB. Max 50 MB.'})
        
        filename = f'background{ext}'
        
        # Upload to Firebase Storage
        url = firebase_upload_sound(file_data, filename)
        
        if url:
            return jsonify({
                'success': True,
                'message': 'Sound uploaded successfully to Firebase!',
                'filename': filename,
                'original_name': file.filename,
                'size': file_size,
                'download_url': f'/api/v1/sound/download/{filename}',
                'storage': 'Firebase Storage'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to upload to Firebase'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/v1/sound/delete', methods=['POST'])
@login_required
def api_delete_sound():
    try:
        filename = request.json.get('filename', '')
        if not filename:
            return jsonify({'success': False, 'message': 'No filename provided'})
        
        if firebase_delete_sound(filename):
            return jsonify({'success': True, 'message': 'Sound deleted from Firebase'})
        return jsonify({'success': False, 'message': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/v1/license/verify', methods=['POST'])
def api_verify_license():
    try:
        data = request.json
        return jsonify(validate_license(data.get('license_key', ''), data.get('device_serial', '')))
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)})

@app.route('/api/v1/license/status/<license_key>')
def api_license_status(license_key):
    try:
        user = firebase_get_user(license_key)
        if not user:
            return jsonify({'exists': False, 'message': 'License not found'})
        
        return jsonify({
            'exists': True,
            'valid': not user.get('banned', False),
            'expires_at': user.get('expires_at', 'Never'),
            'device': user.get('device', ''),
            'notes': user.get('notes', ''),
            'created_at': user.get('created_at', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/device/register', methods=['POST'])
def api_register_device():
    try:
        data = request.json
        device_serial = data.get('device_serial', '')
        license_key = data.get('license_key', '')
        
        if not device_serial:
            return jsonify({'success': False, 'message': 'No device serial'})
        
        device_data = {
            'device_serial': device_serial,
            'license_key': license_key,
            'last_seen': datetime.now().isoformat()
        }
        firebase_save_device(device_data)
        return jsonify({'success': True, 'device_serial': device_serial})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/v1/device/status/<device_serial>')
def api_device_status(device_serial):
    try:
        device = firebase_get_device(device_serial)
        if not device:
            return jsonify({'exists': False, 'message': 'Device not found'})
        
        return jsonify({
            'exists': True,
            'license_key': device.get('license_key', ''),
            'last_seen': device.get('last_seen', ''),
            'created_at': device.get('created_at', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        users = firebase_get_users()
        devices = firebase_get_devices()
        
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
        
        if firebase_save_user(user_data):
            return jsonify({
                'success': True,
                'message': f'✅ License created! Valid for {days} days.',
                'license_key': key,
                'expires_at': expires
            })
        return jsonify({'success': False, 'message': 'Failed to save to Firebase'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/ban', methods=['POST'])
@login_required
def admin_ban():
    try:
        key = request.json.get('license_key', '')
        if not key:
            return jsonify({'success': False, 'message': 'No license key'})
        
        user = firebase_get_user(key)
        if not user:
            return jsonify({'success': False, 'message': 'License not found'})
        
        user['banned'] = True
        firebase_save_user(user)
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
        
        user = firebase_get_user(key)
        if not user:
            return jsonify({'success': False, 'message': 'License not found'})
        
        user['banned'] = False
        firebase_save_user(user)
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
        
        if firebase_delete_user(key):
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
    <title>🔐 Admin Login - Firebase</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: #0a0a1a; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .login-container { background: #111; padding: 40px; border-radius: 16px; border: 1px solid #1a1a2e; max-width: 420px; width: 100%; }
        .login-container h1 { color: #ff9100; text-align: center; font-size: 24px; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #666; font-size: 13px; margin-bottom: 30px; }
        .db-badge { background: #ff9100; color: #fff; padding: 2px 12px; border-radius: 12px; font-size: 10px; display: inline-block; text-align: center; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { color: #aaa; font-size: 13px; display: block; margin-bottom: 6px; }
        .form-group input { width: 100%; padding: 12px 16px; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
        .form-group input:focus { border-color: #ff9100; }
        .btn-login { width: 100%; padding: 14px; background: #ff9100; border: none; border-radius: 8px; color: #000; font-size: 16px; font-weight: bold; cursor: pointer; }
        .btn-login:hover { background: #e67e00; }
        .error-msg { background: rgba(255,68,68,0.1); border: 1px solid #ff4444; color: #ff4444; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; text-align: center; }
        .hint { text-align: center; color: #333; font-size: 12px; margin-top: 15px; }
        .hint span { background: #1a1a2e; padding: 2px 10px; border-radius: 4px; color: #666; }
        .footer { text-align: center; color: #333; font-size: 11px; margin-top: 20px; }
        .footer .brand { color: #ff9100; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔐 RIDOL FB TOOL</h1>
        <div class="subtitle">Admin Authentication • v4.0</div>
        <div style="text-align:center"><span class="db-badge">🔥 Firebase</span></div>
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
    <title>🔐 Admin Panel - Firebase</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: #0a0a1a; color: #fff; padding: 20px; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #111; border-radius: 12px; border: 1px solid #1a1a2e; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
        .header h1 { color: #ff9100; font-size: 20px; }
        .header .badge { background: #ff9100; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .header .db-badge { background: #ff9100; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 10px; border: 1px solid #ff9100; }
        .btn-logout { background: #ff4444; color: #fff; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; }
        .btn-logout:hover { background: #cc0000; }
        .card { background: #111; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #1a1a2e; }
        .card h2 { color: #ff9100; font-size: 16px; margin-bottom: 15px; }
        .flex { display: flex; gap: 15px; flex-wrap: wrap; }
        .flex-grow { flex: 1; min-width: 200px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { color: #aaa; font-size: 12px; display: block; margin-bottom: 5px; }
        .form-group input, .form-group select { width: 100%; padding: 10px 14px; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
        .form-group input:focus { border-color: #ff9100; }
        .btn { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 13px; }
        .btn:hover { transform: scale(1.02); }
        .btn-green { background: #ff9100; color: #000; }
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
        th { color: #ff9100; font-size: 11px; text-transform: uppercase; }
        td code { background: #1a1a2e; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
        .badge { padding: 2px 10px; border-radius: 20px; font-size: 11px; }
        .badge-active { background: #003311; color: #00ff88; }
        .badge-expired { background: #330000; color: #ff4444; }
        .badge-banned { background: #331100; color: #ff8800; }
        .msg { padding: 12px 16px; border-radius: 8px; margin: 10px 0; display: none; font-weight: bold; }
        .msg-success { background: #003311; color: #00ff88; border: 1px solid #00ff88; }
        .msg-error { background: #330000; color: #ff4444; border: 1px solid #ff4444; }
        .msg-info { background: #001133; color: #4488ff; border: 1px solid #4488ff; }
        .new-key-box { margin-top: 15px; padding: 20px; background: #1a1a2e; border-radius: 8px; border: 2px solid #ff9100; display: none; }
        .new-key-box .key { font-size: 20px; font-family: monospace; color: #ff9100; display: block; margin: 10px 0; padding: 10px; background: #000; border-radius: 6px; word-break: break-all; }
        .upload-area { border: 2px dashed #1a1a2e; border-radius: 12px; padding: 30px; text-align: center; cursor: pointer; transition: all 0.3s; }
        .upload-area:hover { border-color: #ff9100; background: rgba(255,145,0,0.02); }
        .upload-area.dragover { border-color: #ff9100; background: rgba(255,145,0,0.05); }
        .upload-area .icon { font-size: 32px; display: block; margin-bottom: 10px; }
        .upload-area p { color: #666; font-size: 13px; }
        .upload-area .supported { color: #444; font-size: 11px; margin-top: 5px; }
        .sound-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: #1a1a2e; border-radius: 8px; margin-bottom: 8px; }
        .sound-item .type { background: #222; padding: 2px 8px; border-radius: 4px; font-size: 10px; }
        .search-box { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .search-box input { flex: 1; min-width: 180px; padding: 10px 14px; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 13px; outline: none; }
        .search-box input:focus { border-color: #ff9100; }
        .footer { text-align: center; color: #333; font-size: 11px; margin-top: 30px; }
        .api-info { background: #1a1a2e; padding: 10px 14px; border-radius: 8px; font-size: 12px; color: #888; margin-top: 10px; }
        .api-info code { color: #ff9100; }
        @media (max-width: 600px) { .header { flex-direction: column; align-items: flex-start; } .stats { grid-template-columns: repeat(2, 1fr); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🔐 RIDOL FB TOOL <span style="font-size:14px;color:#666;font-weight:400">v4.0</span></h1>
                <div style="color:#666;font-size:12px;margin-top:3px">
                    Admin Panel • <span class="db-badge">🔥 Firebase</span>
                </div>
            </div>
            <div style="display:flex;gap:10px;align-items:center">
                <span class="badge">👑 ADMIN</span>
                <a href="/admin/logout"><button class="btn-logout">🚪 LOGOUT</button></a>
            </div>
        </div>
        
        <div id="msg" class="msg"></div>
        
        <div class="card">
            <h2>🔌 Firebase API Endpoints</h2>
            <div class="api-info">
                <code>/api/v1/sound/status</code> - Check sound status<br>
                <code>/api/v1/sound/download</code> - Download sound<br>
                <code>/api/v1/sound/upload</code> - Upload MP3/WAV (Firebase Storage)<br>
                <code>/api/v1/sound/delete</code> - Delete sound<br>
                <code>/api/v1/license/verify</code> - Verify license<br>
                <code>/api/v1/device/register</code> - Register device
            </div>
        </div>
        
        <div class="card">
            <h2>🎵 Custom Sound Upload (MP3 / WAV / OGG)</h2>
            <div style="background:#1a1a2e; padding:10px; border-radius:8px; margin-bottom:15px; color:#888; font-size:12px;">
                ⚡ Files are stored in <strong style="color:#ff9100;">Firebase Storage</strong>
            </div>
            <div class="upload-area" id="dropZone" onclick="document.getElementById('fileInput').click()">
                <span class="icon">📤</span>
                <p>Drop your MP3 / WAV / OGG file here</p>
                <p class="supported">or click to browse • Max 50MB • Firebase Storage</p>
                <input type="file" id="fileInput" accept=".mp3,.wav,.ogg" style="display:none" onchange="uploadSound(this.files)">
            </div>
            <div style="margin-top:15px" id="soundList"></div>
            <div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap">
                <button class="btn btn-blue" onclick="refreshSounds()">🔄 Refresh</button>
                <button class="btn btn-purple" onclick="copyDownloadLink()">📋 Copy Link</button>
                <button class="btn btn-orange" onclick="checkSoundStatus()">📊 Status</button>
                <button class="btn btn-green" onclick="testConnection()">🔌 Test</button>
            </div>
        </div>
        
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
                <strong style="color:#ff9100">✅ License Created Successfully!</strong>
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
                <div class="stat-box"><div class="number" style="color:#ff9100" id="s_total">0</div><div class="label">Total</div></div>
                <div class="stat-box"><div class="number" style="color:#ff9100" id="s_active">0</div><div class="label">✅ Active</div></div>
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
        
        <div class="footer">✦ RIDOL FB TOOL v4.0 • Firebase ✦</div>
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
        
        // ===== TEST CONNECTION =====
        function testConnection() {
            showMsg('🔌 Testing Firebase connection...', 'info');
            fetch('/api/v1/ping')
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.status === 'online') {
                        showMsg('✅ Server reachable! DB: ' + data.database + ' | Storage: ' + data.storage, 'success');
                    } else {
                        showMsg('❌ Server error', 'error');
                    }
                })
                .catch(function(e) {
                    showMsg('❌ Connection failed: ' + e.message, 'error');
                });
        }
        
        // ===== SOUND FUNCTIONS =====
        var dropZone = document.getElementById('dropZone');
        dropZone.addEventListener('dragover', function(e) { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', function() { dropZone.classList.remove('dragover'); });
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) uploadSound(e.dataTransfer.files);
        });
        
        function uploadSound(files) {
            if (!files || files.length === 0) { showMsg('❌ No file selected', 'error'); return; }
            var file = files[0];
            var ext = file.name.split('.').pop().toLowerCase();
            if (!['mp3', 'wav', 'ogg'].includes(ext)) { showMsg('❌ Only MP3, WAV, OGG allowed', 'error'); return; }
            if (file.size > 50 * 1024 * 1024) { showMsg('❌ Max 50MB', 'error'); return; }
            
            var formData = new FormData();
            formData.append('file', file);
            showMsg('⏳ Uploading to Firebase Storage...', 'info');
            
            fetch('/api/v1/sound/upload', { method: 'POST', body: formData })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.success) {
                        showMsg('✅ ' + data.message + ' (' + data.original_name + ' | ' + (data.size / 1024).toFixed(2) + ' KB)', 'success');
                        loadSounds();
                        checkSoundStatus();
                    } else {
                        showMsg('❌ ' + data.message, 'error');
                    }
                })
                .catch(function(e) { showMsg('❌ Upload failed: ' + e.message, 'error'); });
        }
        
        function loadSounds() {
            fetch('/api/v1/sound/status')
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    var list = document.getElementById('soundList');
                    if (data.sounds && data.sounds.length > 0) {
                        var html = '<div style="margin-top:10px"><strong style="color:rgba(255,255,255,0.2);font-size:10px;letter-spacing:3px">CURRENT SOUNDS (Firebase):</strong></div>';
                        data.sounds.forEach(function(s) {
                            var ext = s.name.split('.').pop().toUpperCase();
                            html += '<div class="sound-item">' +
                                '<div class="info"><span style="font-size:18px">🎵</span><span class="name">' + s.name + '</span><span class="type">' + ext + '</span><span class="size">' + s.size_mb + ' MB</span></div>' +
                                '<div style="display:flex;gap:8px">' +
                                '<button class="btn btn-blue btn-sm" onclick="playSound(\'' + s.name + '\')">▶ PLAY</button>' +
                                '<button class="btn btn-green btn-sm" onclick="copySingleLink(\'' + s.name + '\')">📋</button>' +
                                '<button class="btn btn-red btn-sm" onclick="deleteSound(\'' + s.name + '\')">✕</button>' +
                                '</div></div>';
                        });
                        list.innerHTML = html;
                    } else {
                        list.innerHTML = '<div style="text-align:center;color:rgba(255,255,255,0.05);padding:20px;font-size:11px;letter-spacing:3px">No sounds in Firebase</div>';
                    }
                })
                .catch(function(e) { showMsg('❌ Failed to load sounds', 'error'); });
        }
        
        function playSound(filename) {
            var url = window.location.origin + '/api/v1/sound/download/' + filename;
            var audio = new Audio(url);
            audio.play();
            showMsg('▶ Playing: ' + filename, 'info');
        }
        
        function copySingleLink(filename) {
            var url = window.location.origin + '/api/v1/sound/download/' + filename;
            navigator.clipboard.writeText(url).then(function() {
                showMsg('📋 Link copied!', 'success');
            }).catch(function() {
                var ta = document.createElement('textarea');
                ta.value = url;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                showMsg('📋 Link copied!', 'success');
            });
        }
        
        function deleteSound(filename) {
            if (!confirm('Delete ' + filename + '?')) return;
            fetch('/api/v1/sound/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: filename })
            })
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.success) { showMsg('✅ ' + data.message, 'success'); loadSounds(); checkSoundStatus(); }
                else { showMsg('❌ ' + data.message, 'error'); }
            })
            .catch(function(e) { showMsg('❌ Delete failed', 'error'); });
        }
        
        function copyDownloadLink() {
            var url = window.location.origin + '/api/v1/sound/download';
            navigator.clipboard.writeText(url).then(function() {
                showMsg('📋 Download link copied!', 'success');
            }).catch(function() {
                var ta = document.createElement('textarea');
                ta.value = url;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                showMsg('📋 Link copied!', 'success');
            });
        }
        
        function checkSoundStatus() {
            showMsg('📊 Checking Firebase sound status...', 'info');
            fetch('/api/v1/sound/status')
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.exists) {
                        showMsg('✅ Sound exists in Firebase! ' + data.count + ' file(s)', 'success');
                    } else {
                        showMsg('❌ No sound in Firebase', 'error');
                    }
                })
                .catch(function(e) { showMsg('❌ Status check failed: ' + e.message, 'error'); });
        }
        
        function refreshSounds() {
            showMsg('🔄 Refreshing...', 'info');
            loadSounds();
            checkSoundStatus();
        }
        
        // ===== LICENSE FUNCTIONS =====
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
        loadSounds();
        setTimeout(checkSoundStatus, 1000);
        setInterval(refreshAll, 30000);
    </script>
</body>
</html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)