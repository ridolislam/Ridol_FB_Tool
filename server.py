#!/usr/bin/env python3
"""
Ridol FB Tool - Server Side (Render)
License & Credit Management System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
import re
import json
import random
import string
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURATION ====================
CLIPROXY_API_URL = "https://api.cliproxy.io/white/api"
PORT = int(os.environ.get('PORT', 10000))
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# ==================== DATABASE ====================
DB_PATH = 'licenses.db'

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Licenses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            license_key TEXT PRIMARY KEY,
            credits INTEGER DEFAULT 0,
            max_browsers INTEGER DEFAULT 1,
            created_at TEXT,
            expires_at TEXT,
            is_active INTEGER DEFAULT 1,
            used_credits INTEGER DEFAULT 0,
            last_used TEXT
        )
    ''')
    
    # Logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT,
            action TEXT,
            ip_used TEXT,
            country TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== LICENSE FUNCTIONS ====================

def generate_license():
    """Generate a random license key"""
    prefix = "RIDOL"
    parts = []
    for _ in range(4):
        part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        parts.append(part)
    return f"{prefix}-{'-'.join(parts)}"

def validate_license(license_key):
    """Check if license is valid and return details"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM licenses 
        WHERE license_key = ? AND is_active = 1
    ''', (license_key,))
    
    result = c.fetchone()
    conn.close()
    
    if not result:
        return None
    
    # Check expiry
    if result['expires_at']:
        expires = datetime.fromisoformat(result['expires_at'])
        if expires < datetime.now():
            return None
    
    return dict(result)

def deduct_credit(license_key):
    """Deduct 1 credit for each operation"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT credits, used_credits FROM licenses WHERE license_key = ?', (license_key,))
    result = c.fetchone()
    
    if not result or result['credits'] <= 0:
        conn.close()
        return False
    
    new_credits = result['credits'] - 1
    new_used = result['used_credits'] + 1
    
    c.execute('''
        UPDATE licenses 
        SET credits = ?, used_credits = ?, last_used = ?
        WHERE license_key = ?
    ''', (new_credits, new_used, datetime.now().isoformat(), license_key))
    
    conn.commit()
    conn.close()
    return True

# ==================== API ROUTES ====================

@app.route('/', methods=['GET'])
def home():
    """Health check"""
    return jsonify({
        'status': 'online',
        'service': 'Ridol FB Tool License Server',
        'version': '7.0',
        'timestamp': datetime.now().isoformat()
    })

# ==================== USER API (Bot ব্যবহার করবে) ====================

@app.route('/api/verify', methods=['POST'])
def verify_license():
    """
    Verify license and get user info
    Request: {"license_key": "RIDOL-XXXX-XXXX-XXXX"}
    Response: {"valid": true, "credits": 1000, "max_browsers": 5}
    """
    try:
        data = request.get_json()
        license_key = data.get('license_key', '').strip().upper()
        
        if not license_key:
            return jsonify({'valid': False, 'error': 'License key required'}), 400
        
        # Validate format
        if not re.match(r'^RIDOL-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$', license_key):
            return jsonify({'valid': False, 'error': 'Invalid license format'}), 400
        
        license_data = validate_license(license_key)
        
        if not license_data:
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired license'
            }), 401
        
        return jsonify({
            'valid': True,
            'credits': license_data['credits'],
            'max_browsers': license_data['max_browsers'],
            'expires_at': license_data['expires_at'],
            'used_credits': license_data['used_credits']
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

@app.route('/api/get_ip', methods=['POST'])
def get_ip():
    """
    Get IP from Cliproxy API and deduct credit
    Request: {"license_key": "RIDOL-XXXX-XXXX-XXXX", "country": "BD"}
    Response: {"success": true, "ip": "103.xxx.xxx.xxx", "port": 3010, "remaining_credits": 999}
    """
    try:
        data = request.get_json()
        license_key = data.get('license_key', '').strip().upper()
        country = data.get('country', 'Rand').upper()
        
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
        if not deduct_credit(license_key):
            return jsonify({'success': False, 'error': 'Failed to deduct credit'}), 500
        
        # Get IP from Cliproxy
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
                'error': 'Invalid IP from Cliproxy',
                'details': ip
            }), 500
        
        # Log usage
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO usage_logs (license_key, action, ip_used, country, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (license_key, 'get_ip', ip, country, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        # Get updated credits
        updated_data = validate_license(license_key)
        
        return jsonify({
            'success': True,
            'ip': ip,
            'port': 3010,
            'country': country,
            'remaining_credits': updated_data['credits'] if updated_data else 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['POST'])
def get_status():
    """
    Get license status without deducting credit
    Request: {"license_key": "RIDOL-XXXX-XXXX-XXXX"}
    """
    try:
        data = request.get_json()
        license_key = data.get('license_key', '').strip().upper()
        
        license_data = validate_license(license_key)
        
        if not license_data:
            return jsonify({'valid': False, 'error': 'Invalid license'}), 401
        
        return jsonify({
            'valid': True,
            'credits': license_data['credits'],
            'max_browsers': license_data['max_browsers'],
            'used_credits': license_data['used_credits'],
            'expires_at': license_data['expires_at']
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

# ==================== ADMIN API ====================

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login"""
    data = request.get_json()
    password = data.get('password', '')
    
    if password == ADMIN_PASSWORD:
        return jsonify({'success': True, 'token': 'admin_token'})
    return jsonify({'success': False}), 401

@app.route('/admin/create_license', methods=['POST'])
def create_license():
    """Create new license with credits"""
    try:
        data = request.get_json()
        
        # Simple auth check
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        credits = int(data.get('credits', 100))
        max_browsers = int(data.get('max_browsers', 1))
        expiry_days = int(data.get('expiry_days', 30))
        
        license_key = generate_license()
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO licenses (license_key, credits, max_browsers, created_at, expires_at, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (license_key, credits, max_browsers, created_at, expires_at))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'license_key': license_key,
            'credits': credits,
            'max_browsers': max_browsers,
            'expires_at': expires_at
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/list_licenses', methods=['GET'])
def list_licenses():
    """List all licenses"""
    try:
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db()
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
def add_credits():
    """Add credits to existing license"""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        license_key = data.get('license_key', '').strip().upper()
        add_credits = int(data.get('credits', 0))
        
        if add_credits <= 0:
            return jsonify({'success': False, 'error': 'Invalid credit amount'}), 400
        
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE licenses SET credits = credits + ? WHERE license_key = ?', 
                 (add_credits, license_key))
        
        if c.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'License not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'added_credits': add_credits})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/revoke_license', methods=['POST'])
def revoke_license():
    """Revoke/deactivate a license"""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        license_key = data.get('license_key', '').strip().upper()
        
        conn = get_db()
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
def get_logs():
    """Get usage logs"""
    try:
        token = request.headers.get('Authorization', '')
        if token != 'Bearer admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        limit = request.args.get('limit', 50)
        
        conn = get_db()
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
    logger.info(f"[+] Starting License Server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)