#!/usr/bin/env python3
"""
Ridol FB Tool License Server v4.0 - MongoDB Atlas Integration
Author: Ridol Islam
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
from flask_cors import CORS
import os
import uuid
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
import logging
import gridfs
from pymongo import MongoClient
from bson import ObjectId
import io

# ==================== MONGODB ATLAS CONNECTION ====================
MONGODB_URI = "mongodb+srv://ridoli310_db_user:2knTC9AMZDDUfeil@cluster0.hamwqgx.mongodb.net/?appName=Cluster0"

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client['ridol_fb_tool']
    users_collection = db['users']
    devices_collection = db['devices']
    sounds_collection = db['sounds']
    fs = gridfs.GridFS(db)
    
    # Test connection
    client.admin.command('ping')
    print("[+] MongoDB Atlas Connected Successfully!")
except Exception as e:
    print(f"[-] MongoDB Connection Error: {e}")
    # Fallback to local file storage
    db = None
    fs = None

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ADMIN_PASSWORD = 'Ridol123@'

# ==================== DATABASE FUNCTIONS ====================

def get_user(license_key):
    """Get user by license key from MongoDB"""
    if db:
        return users_collection.find_one({'license_key': license_key})
    return None

def get_users():
    """Get all users from MongoDB"""
    if db:
        return list(users_collection.find({}))
    return []

def get_devices():
    """Get all devices from MongoDB"""
    if db:
        return list(devices_collection.find({}))
    return []

def get_device(device_serial):
    """Get device by serial from MongoDB"""
    if db:
        return devices_collection.find_one({'device_serial': device_serial})
    return None

def save_user(user_data):
    """Save user to MongoDB"""
    if db:
        if 'created_at' not in user_data:
            user_data['created_at'] = datetime.now().isoformat()
        # Check if exists
        existing = users_collection.find_one({'license_key': user_data['license_key']})
        if existing:
            users_collection.update_one(
                {'license_key': user_data['license_key']},
                {'$set': user_data}
            )
        else:
            users_collection.insert_one(user_data)
        return True
    return False

def save_device(device_data):
    """Save device to MongoDB"""
    if db:
        if 'created_at' not in device_data:
            device_data['created_at'] = datetime.now().isoformat()
        existing = devices_collection.find_one({'device_serial': device_data['device_serial']})
        if existing:
            devices_collection.update_one(
                {'device_serial': device_data['device_serial']},
                {'$set': device_data}
            )
        else:
            devices_collection.insert_one(device_data)
        return True
    return False

def delete_user(license_key):
    """Delete user from MongoDB"""
    if db:
        return users_collection.delete_one({'license_key': license_key})
    return None

def save_sound_file(file_data, filename):
    """Save sound file to GridFS"""
    if fs:
        # Delete existing sound file
        existing = fs.find_one({'filename': filename})
        if existing:
            fs.delete(existing._id)
        
        # Save new file
        file_id = fs.put(file_data, filename=filename, uploaded_at=datetime.now().isoformat())
        return file_id
    return None

def get_sound_file(filename):
    """Get sound file from GridFS"""
    if fs:
        return fs.find_one({'filename': filename})
    return None

def delete_sound_file(filename):
    """Delete sound file from GridFS"""
    if fs:
        existing = fs.find_one({'filename': filename})
        if existing:
            fs.delete(existing._id)
            return True
    return False

def get_all_sound_files():
    """Get all sound files from GridFS"""
    if fs:
        sounds = []
        for f in fs.find({}):
            sounds.append({
                'name': f.filename,
                'size': f.length,
                'size_mb': round(f.length / (1024 * 1024), 2),
                'uploaded_at': f.uploaded_at if hasattr(f, 'uploaded_at') else 'N/A'
            })
        return sounds
    return []

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

# ==================== API ENDPOINTS ====================

@app.route('/api/v1/ping')
def ping():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': 'v4.0',
        'database': 'MongoDB Atlas' if db else 'Local File Storage'
    })

@app.route('/api/v1/status')
def api_status():
    users = get_users() if db else []
    devices = get_devices() if db else []
    sound_files = get_all_sound_files()
    
    return jsonify({
        'status': 'online',
        'version': 'v4.0',
        'timestamp': datetime.now().isoformat(),
        'license_count': len(users),
        'device_count': len(devices),
        'sound_files': [f['name'] for f in sound_files],
        'sound_exists': len(sound_files) > 0,
        'database': 'MongoDB Atlas' if db else 'Local File Storage'
    })

@app.route('/api/v1/sound/status')
def api_sound_status():
    sound_files = get_all_sound_files()
    return jsonify({
        'exists': len(sound_files) > 0,
        'sounds': sound_files,
        'count': len(sound_files)
    })

@app.route('/api/v1/sound/download/<filename>')
def api_download_sound(filename):
    try:
        if not filename.endswith(('.mp3', '.wav', '.ogg')):
            return jsonify({'error': 'Invalid file type'}), 400
        
        sound_file = get_sound_file(filename)
        if sound_file:
            data = sound_file.read()
            return send_file(
                io.BytesIO(data),
                as_attachment=True,
                download_name=filename,
                mimetype='audio/mpeg' if filename.endswith('.mp3') else 'audio/wav'
            )
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/sound/download')
def api_download_sound_default():
    try:
        sound_files = get_all_sound_files()
        if sound_files:
            # Prefer MP3
            for f in sound_files:
                if f['name'].endswith('.mp3'):
                    return api_download_sound(f['name'])
            return api_download_sound(sound_files[0]['name'])
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
        
        filename = f'background{ext}'
        file_data = file.read()
        
        file_id = save_sound_file(file_data, filename)
        if file_id:
            return jsonify({
                'success': True,
                'message': f'✅ Sound uploaded successfully!',
                'filename': filename,
                'original_name': file.filename,
                'size': len(file_data),
                'download_url': f'/api/v1/sound/download/{filename}'
            })
        return jsonify({'success': False, 'message': 'Failed to save to database'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/api/v1/sound/delete', methods=['POST'])
@login_required
def api_delete_sound():
    try:
        filename = request.json.get('filename', '')
        if not filename:
            return jsonify({'success': False, 'message': 'No filename provided'})
        
        if delete_sound_file(filename):
            return jsonify({'success': True, 'message': '✅ Sound deleted'})
        return jsonify({'success': False, 'message': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/v1/license/verify', methods=['POST'])
def api_verify_license():
    data = request.json
    return jsonify(validate_license(data.get('license_key', ''), data.get('device_serial', '')))

@app.route('/api/v1/license/status/<license_key>')
def api_license_status(license_key):
    user = get_user(license_key)
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

@app.route('/api/v1/device/register', methods=['POST'])
def api_register_device():
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
    save_device(device_data)
    return jsonify({'success': True, 'device_serial': device_serial})

@app.route('/api/v1/device/status/<device_serial>')
def api_device_status(device_serial):
    device = get_device(device_serial)
    if not device:
        return jsonify({'exists': False, 'message': 'Device not found'})
    
    return jsonify({
        'exists': True,
        'license_key': device.get('license_key', ''),
        'last_seen': device.get('last_seen', ''),
        'created_at': device.get('created_at', '')
    })

# ==================== ADMIN ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        'server': 'Ridol FB Tool License Server',
        'version': 'v4.0',
        'status': 'online',
        'database': 'MongoDB Atlas' if db else 'Local File Storage',
        'api_endpoints': {
            'ping': '/api/v1/ping',
            'status': '/api/v1/status',
            'sound_status': '/api/v1/sound/status',
            'sound_download': '/api/v1/sound/download',
            'sound_upload': '/api/v1/sound/upload',
            'license_verify': '/api/v1/license/verify',
            'device_register': '/api/v1/device/register',
            'admin': '/admin'
        }
    })

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
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
    users = get_users() if db else []
    devices = get_devices() if db else []
    
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
        
        result = delete_user(key)
        if result and result.deleted_count > 0:
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
    <title>🔐 Admin Login - MongoDB</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
        body { background: #0a0a1a; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .login-container { background: #111; padding: 40px; border-radius: 16px; border: 1px solid #1a1a2e; max-width: 400px; width: 100%; }
        .login-container h1 { color: #00ff88; text-align: center; font-size: 24px; }
        .login-container .subtitle { text-align: center; color: #666; font-size: 13px; margin-bottom: 30px; }
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
        .db-badge { background: #003311; color: #00ff88; padding: 2px 12px; border-radius: 12px; font-size: 10px; display: inline-block; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔐 RIDOL FB TOOL</h1>
        <div class="subtitle">Admin Authentication • v4.0</div>
        <div style="text-align:center"><span class="db-badge">🍃 MongoDB Atlas</span></div>
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
    <title>🔐 Admin Panel - MongoDB</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
        body { background: #0a0a1a; color: #fff; padding: 20px; }
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
        .upload-area { border: 2px dashed #1a1a2e; border-radius: 12px; padding: 30px; text-align: center; cursor: pointer; transition: all 0.3s; }
        .upload-area:hover { border-color: #00ff88; background: rgba(0,255,136,0.02); }
        .upload-area.dragover { border-color: #00ff88; background: rgba(0,255,136,0.05); }
        .upload-area .icon { font-size: 32px; display: block; margin-bottom: 10px; }
        .upload-area p { color: #666; font-size: 13px; }
        .upload-area .supported { color: #444; font-size: 11px; margin-top: 5px; }
        .sound-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: #1a1a2e; border-radius: 8px; margin-bottom: 8px; }
        .sound-item .type { background: #222; padding: 2px 8px; border-radius: 4px; font-size: 10px; }
        .search-box { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .search-box input { flex: 1; min-width: 180px; padding: 10px 14px; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 13px; outline: none; }
        .search-box input:focus { border-color: #00ff88; }
        .footer { text-align: center; color: #333; font-size: 11px; margin-top: 30px; }
        .api-info { background: #1a1a2e; padding: 10px 14px; border-radius: 8px; font-size: 12px; color: #888; margin-top: 10px; }
        .api-info code { color: #00ff88; }
        @media (max-width: 600px) { .header { flex-direction: column; align-items: flex-start; } .stats { grid-template-columns: repeat(2, 1fr); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🔐 RIDOL FB TOOL <span style="font-size:14px;color:#666;font-weight:400">v4.0</span></h1>
                <div style="color:#666;font-size:12px;margin-top:3px">
                    Admin Panel • <span class="db-badge">🍃 MongoDB Atlas</span>
                </div>
            </div>
            <div style="display:flex;gap:10px;align-items:center">
                <span class="badge">👑 ADMIN</span>
                <a href="/admin/logout"><button class="btn-logout">🚪 LOGOUT</button></a>
            </div>
        </div>
        
        <div id="msg" class="msg"></div>
        
        <!-- API Info -->
        <div class="card">
            <h2>🔌 MongoDB API Endpoints</h2>
            <div class="api-info">
                <code>/api/v1/sound/status</code> - Check sound status<br>
                <code>/api/v1/sound/download</code> - Download sound<br>
                <code>/api/v1/sound/upload</code> - Upload MP3/WAV<br>
                <code>/api/v1/sound/delete</code> - Delete sound<br>
                <code>/api/v1/license/verify</code> - Verify license<br>
                <code>/api/v1/device/register</code> - Register device
            </div>
        </div>
        
        <!-- SOUND UPLOAD -->
        <div class="card">
            <h2>🎵 Custom Sound Upload (MP3 / WAV / OGG)</h2>
            <div class="upload-area" id="dropZone" onclick="document.getElementById('fileInput').click()">
                <span class="icon">📤</span>
                <p>Drop your MP3 / WAV / OGG file here</p>
                <p class="supported">or click to browse • Max 50MB</p>
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
        
        <!-- LICENSE -->
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
                        <label>📝 Notes</label>
                        <input type="text" id="notes" placeholder="Client name">
                    </div>
                </div>
            </div>
            <button class="btn btn-green" onclick="createLic()">⚡ GENERATE LICENSE</button>
            <div id="new_key" class="new-key-box">
                <strong style="color:#00ff88">✅ License Created!</strong>
                <span class="key" id="key_display">RIDOL-XXXX-XXXX-XXXX</span>
                <div class="flex" style="gap:10px">
                    <button class="btn btn-blue" onclick="copyKey()">📋 COPY</button>
                    <button class="btn btn-orange" onclick="searchNewKey()">🔍 FIND</button>
                </div>
            </div>
        </div>
        
        <!-- STATISTICS -->
        <div class="card">
            <h2>📊 Statistics</h2>
            <div class="stats">
                <div class="stat-box"><div class="number" style="color:#00ff88" id="s_total">0</div><div class="label">Total</div></div>
                <div class="stat-box"><div class="number" style="color:#00ff88" id="s_active">0</div><div class="label">Active</div></div>
                <div class="stat-box"><div class="number" style="color:#ff8800" id="s_expired">0</div><div class="label">Expired</div></div>
                <div class="stat-box"><div class="number" style="color:#ff4444" id="s_banned">0</div><div class="label">Banned</div></div>
                <div class="stat-box"><div class="number" style="color:#4488ff" id="s_devices">0</div><div class="label">Devices</div></div>
            </div>
        </div>
        
        <!-- LICENSE LIST -->
        <div class="card">
            <h2>👥 License Management</h2>
            <div class="search-box">
                <input type="text" id="search" placeholder="🔍 Search..." onkeyup="if(event.key==='Enter')searchLic()">
                <button class="btn btn-blue" onclick="searchLic()">🔍 SEARCH</button>
                <button class="btn btn-orange" onclick="refreshAll()">🔄 REFRESH</button>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>Key</th><th>Expires</th><th>Status</th><th>Device</th><th>Notes</th><th>Actions</th></tr></thead>
                    <tbody id="tbody"><tr><td colspan="6" style="text-align:center;color:#666;padding:30px">Loading...</td></tr></tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">✦ RIDOL FB TOOL v4.0 • MongoDB Atlas ✦</div>
    </div>
    
    <script>
        let allUsers = {};
        let lastCreatedKey = '';
        
        function showMsg(text, type) {
            const el = document.getElementById('msg');
            el.textContent = text;
            el.className = 'msg msg-' + type;
            el.style.display = 'block';
            setTimeout(() => el.style.display = 'none', 5000);
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
                showMsg('❌ Network Error', 'error');
                return null;
            }
        }
        
        // ===== TEST CONNECTION =====
        async function testConnection() {
            showMsg('🔌 Testing API connection...', 'info');
            try {
                const res = await fetch('/api/v1/ping');
                const data = await res.json();
                if (data.status === 'online') {
                    showMsg('✅ Server reachable! DB: ' + data.database, 'success');
                } else {
                    showMsg('❌ Server error', 'error');
                }
            } catch (e) {
                showMsg('❌ Connection failed: ' + e.message, 'error');
            }
        }
        
        // ===== SOUND FUNCTIONS =====
        const dropZone = document.getElementById('dropZone');
        dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => { dropZone.classList.remove('dragover'); });
        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) uploadSound(e.dataTransfer.files);
        });
        
        async function uploadSound(files) {
            if (!files || files.length === 0) { showMsg('❌ No file', 'error'); return; }
            const file = files[0];
            if (!file.name.match(/\.(mp3|wav|ogg)$/i)) {
                showMsg('❌ Only MP3, WAV, OGG allowed', 'error');
                return;
            }
            if (file.size > 50*1024*1024) { showMsg('❌ Max 50MB', 'error'); return; }
            
            const formData = new FormData();
            formData.append('file', file);
            try {
                showMsg('⏳ Uploading to MongoDB...', 'info');
                const res = await fetch('/api/v1/sound/upload', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.success) {
                    showMsg('✅ ' + data.message + ' (' + file.name + ')', 'success');
                    loadSounds();
                    checkSoundStatus();
                } else {
                    showMsg('❌ ' + data.message, 'error');
                }
            } catch (e) { showMsg('❌ Upload failed', 'error'); }
        }
        
        async function loadSounds() {
            try {
                const res = await fetch('/api/v1/sound/status');
                const data = await res.json();
                const list = document.getElementById('soundList');
                if (data.sounds && data.sounds.length > 0) {
                    let html = '<div style="margin-bottom:8px;color:#666;font-size:11px">CURRENT SOUNDS (MongoDB):</div>';
                    data.sounds.forEach(s => {
                        const ext = s.name.split('.').pop().toUpperCase();
                        html += `<div class="sound-item">
                            <span>🎵 ${s.name}</span>
                            <span class="type">${ext}</span>
                            <span class="size">${s.size_mb} MB</span>
                            <div style="display:flex;gap:6px">
                                <button class="btn btn-blue btn-sm" onclick="playSound('${s.name}')">▶</button>
                                <button class="btn btn-green btn-sm" onclick="copySingleLink('${s.name}')">📋</button>
                                <button class="btn btn-red btn-sm" onclick="deleteSound('${s.name}')">✕</button>
                            </div>
                        </div>`;
                    });
                    list.innerHTML = html;
                } else {
                    list.innerHTML = '<div style="text-align:center;color:#444;padding:15px;font-size:13px">No sounds in MongoDB</div>';
                }
            } catch (e) {}
        }
        
        async function playSound(filename) {
            try {
                const url = window.location.origin + '/api/v1/sound/download/' + filename;
                const audio = new Audio(url);
                audio.play();
                showMsg('▶ Playing: ' + filename, 'info');
            } catch (e) { showMsg('❌ Play failed: ' + e.message, 'error'); }
        }
        
        function copySingleLink(filename) {
            const url = window.location.origin + '/api/v1/sound/download/' + filename;
            navigator.clipboard.writeText(url).then(() => showMsg('📋 Link copied!', 'success'))
            .catch(() => {
                const ta = document.createElement('textarea');
                ta.value = url;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                showMsg('📋 Link copied!', 'success');
            });
        }
        
        async function deleteSound(filename) {
            if (!confirm('Delete ' + filename + '?')) return;
            try {
                const res = await fetch('/api/v1/sound/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename })
                });
                const data = await res.json();
                if (data.success) { showMsg('✅ ' + data.message, 'success'); loadSounds(); checkSoundStatus(); }
                else { showMsg('❌ ' + data.message, 'error'); }
            } catch (e) { showMsg('❌ Delete failed', 'error'); }
        }
        
        function copyDownloadLink() {
            const url = window.location.origin + '/api/v1/sound/download';
            navigator.clipboard.writeText(url).then(() => showMsg('📋 Download link copied!', 'success'))
            .catch(() => {
                const ta = document.createElement('textarea');
                ta.value = url;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                showMsg('📋 Link copied!', 'success');
            });
        }
        
        async function checkSoundStatus() {
            try {
                const res = await fetch('/api/v1/sound/status');
                const data = await res.json();
                if (data.exists) {
                    showMsg('✅ Sound exists in MongoDB! ' + data.count + ' file(s)', 'success');
                } else {
                    showMsg('❌ No sound in MongoDB', 'error');
                }
            } catch (e) { showMsg('❌ Status check failed', 'error'); }
        }
        
        async function refreshSounds() {
            showMsg('🔄 Refreshing...', 'info');
            await loadSounds();
            await checkSoundStatus();
        }
        
        // ===== LICENSE FUNCTIONS =====
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
            const result = await apiCall('/admin/' + action, 'POST', { license_key: key });
            if (result && result.success) { showMsg('✅ ' + result.message, 'success'); refreshAll(); }
            else { showMsg(result ? result.message : '❌ Failed', 'error'); }
        }
        
        async function deleteLic(key) {
            if (!confirm('Delete ' + key + '?')) return;
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
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#444;padding:30px">No licenses</td></tr>';
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
                    <td style="font-size:11px">${u.expires_at || 'Never'}</td>
                    <td><span class="badge ${badge}">${status}</span></td>
                    <td style="color:#666;font-size:12px">${u.device || '-'}</td>
                    <td style="color:#666;font-size:12px">${u.notes || '-'}</td>
                    <td>
                        <button class="btn ${isBanned ? 'btn-green' : 'btn-red'} btn-sm" onclick="toggleBan('${key}', ${isBanned})">${isBanned ? 'UNBAN' : 'BAN'}</button>
                        <button class="btn btn-red btn-sm" onclick="deleteLic('${key}')">✕</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        async function refreshAll() {
            const data = await apiCall('/admin/data', 'GET');
            if (!data) {
                document.getElementById('tbody').innerHTML = '<tr><td colspan="6" style="text-align:center;color:#ff4444;padding:30px">❌ Failed</td></tr>';
                return;
            }
            allUsers = data.users || {};
            renderTable(allUsers);
            document.getElementById('s_total').textContent = data.total || 0;
            document.getElementById('s_active').textContent = data.active || 0;
            document.getElementById('s_expired').textContent = data.expired || 0;
            document.getElementById('s_banned').textContent = data.banned || 0;
            document.getElementById('s_devices').textContent = data.device_count || 0;
        }
        
        function searchLic() {
            const q = document.getElementById('search').value.toLowerCase().trim();
            if (!q) { renderTable(allUsers); return; }
            const filtered = {};
            Object.keys(allUsers).forEach(key => {
                const u = allUsers[key];
                if (key.toLowerCase().includes(q) || (u.device && u.device.toLowerCase().includes(q)) || (u.notes && u.notes.toLowerCase().includes(q))) {
                    filtered[key] = u;
                }
            });
            renderTable(filtered);
            showMsg('🔍 Found ' + Object.keys(filtered).length + ' result(s)', 'info');
        }
        
        // ===== INIT =====
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