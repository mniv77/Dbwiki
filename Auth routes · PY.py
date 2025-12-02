# HaGOLEM Wiki - User Authentication Routes
# Add these routes to your Flask app

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import bcrypt
import secrets
from datetime import datetime, timedelta
from functools import wraps

# ============================================================================
# Configuration
# ============================================================================

app.secret_key = 'your-secret-key-change-this-to-random-string'  # CHANGE THIS!

# Database connection (same as before)
def get_db():
    return mysql.connector.connect(
        host='your-mysql-host.mysql.pythonanywhere-services.com',
        user='your-username',
        password='your-password',
        database='your-database-name'
    )

# ============================================================================
# Authentication Decorator - Protect routes that need login
# ============================================================================

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Please login first'}), 401
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# Helper Functions
# ============================================================================

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def log_activity(user_id, action, target_type=None, target_id=None, details=None):
    """Log user activity"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hagolem_activity_log 
            (user_id, action, target_type, target_id, details, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, action, target_type, target_id, details, request.remote_addr))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error logging activity: {e}")

# ============================================================================
# MAIN PAGES
# ============================================================================

@app.route('/hagolem/login')
def login_page():
    """Login page"""
    if 'user_id' in session:
        return redirect('/hagolem/wiki')
    return render_template('hagolem_login.html')

@app.route('/hagolem/register')
def register_page():
    """Registration page"""
    if 'user_id' in session:
        return redirect('/hagolem/wiki')
    return render_template('hagolem_register.html')

@app.route('/hagolem/wiki')
@login_required
def hagolem_wiki():
    """Main wiki dashboard - NOW REQUIRES LOGIN"""
    return render_template('hagolem_wiki.html')

# ============================================================================
# AUTHENTICATION API ROUTES
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        
        # Validate input
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'Username, email, and password required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Check if username or email already exists
        cursor.execute("SELECT id FROM hagolem_users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert new user
        cursor.execute("""
            INSERT INTO hagolem_users 
            (username, email, password_hash, full_name, role)
            VALUES (%s, %s, %s, %s, 'user')
        """, (username, email, password_hash, full_name))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        # Log activity
        log_activity(user_id, 'register', 'user', user_id)
        
        return jsonify({'success': True, 'message': 'Registration successful! Please login.'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Get user by username or email
        cursor.execute("""
            SELECT id, username, email, password_hash, full_name, role, is_active
            FROM hagolem_users 
            WHERE (username = %s OR email = %s) AND is_active = TRUE
        """, (username, username))
        
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
        
        # Update last login
        cursor.execute("UPDATE hagolem_users SET last_login = NOW() WHERE id = %s", (user['id'],))
        conn.commit()
        
        # Create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['role'] = user['role']
        session.permanent = True
        
        cursor.close()
        conn.close()
        
        # Log activity
        log_activity(user['id'], 'login', 'user', user['id'])
        
        return jsonify({
            'success': True, 
            'user': {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    user_id = session.get('user_id')
    log_activity(user_id, 'logout', 'user', user_id)
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me')
@login_required
def get_current_user():
    """Get current logged-in user info"""
    return jsonify({
        'success': True,
        'user': {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'full_name': session.get('full_name'),
            'role': session.get('role')
        }
    })

# ============================================================================
# USER MANAGEMENT (Admin only)
# ============================================================================

@app.route('/api/users')
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                u.id, u.username, u.email, u.full_name, u.role, 
                u.is_active, u.date_registered, u.last_login,
                COUNT(DISTINCT i.id) as ideas_count,
                COUNT(DISTINCT c.id) as comments_count
            FROM hagolem_users u
            LEFT JOIN hagolem_ideas i ON u.id = i.created_by_user_id
            LEFT JOIN hagolem_comments c ON u.id = c.user_id
            GROUP BY u.id
            ORDER BY u.date_registered DESC
        """)
        
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_user_active(user_id):
    """Enable/disable a user (admin only)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE hagolem_users 
            SET is_active = NOT is_active 
            WHERE id = %s
        """, (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        log_activity(session.get('user_id'), 'toggle_user_active', 'user', user_id)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/change-role', methods=['PUT'])
@admin_required
def change_user_role(user_id):
    """Change user role (admin only)"""
    try:
        data = request.json
        new_role = data.get('role')
        
        if new_role not in ['admin', 'user', 'viewer']:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE hagolem_users SET role = %s WHERE id = %s", (new_role, user_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        log_activity(session.get('user_id'), 'change_user_role', 'user', user_id, f'Changed to {new_role}')
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# UPDATE EXISTING ROUTES TO TRACK USERS
# ============================================================================

# Modify your existing add_idea route:
@app.route('/api/wiki/ideas', methods=['POST'])
@login_required  # ADD THIS
def add_idea():
    """Add new idea - NOW TRACKS USER"""
    try:
        data = request.json
        user_id = session.get('user_id')  # Get logged-in user
        
        conn = get_db()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO hagolem_ideas 
            (idea_title, idea_summary, idea_content, idea_type, category, 
             priority, status, tags, source_file, created_by_user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            data.get('title'),
            data.get('summary'),
            data.get('content'),
            data.get('type', 'General'),
            data.get('category', 'Uncategorized'),
            data.get('priority', 'Medium'),
            data.get('status', 'New'),
            data.get('tags', ''),
            data.get('source_file', ''),
            user_id  # ADD THIS
        )
        
        cursor.execute(query, values)
        conn.commit()
        idea_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        # Log activity
        log_activity(user_id, 'add_idea', 'idea', idea_id)
        
        return jsonify({'success': True, 'id': idea_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Modify your existing add_comment route:
@app.route('/api/wiki/comments', methods=['POST'])
@login_required  # ADD THIS
def add_comment():
    """Add comment - NOW TRACKS USER"""
    try:
        data = request.json
        user_id = session.get('user_id')  # Get logged-in user
        full_name = session.get('full_name', 'Anonymous')
        
        conn = get_db()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO hagolem_comments 
            (idea_id, comment_text, comment_type, commenter_name, user_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        values = (
            data.get('idea_id'),
            data.get('comment_text'),
            data.get('comment_type', 'Comment'),
            full_name,  # Use their real name from profile
            user_id  # ADD THIS
        )
        
        cursor.execute(query, values)
        conn.commit()
        comment_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        # Log activity
        log_activity(user_id, 'add_comment', 'comment', comment_id)
        
        return jsonify({'success': True, 'id': comment_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# INSTALL REQUIRED PACKAGE
# ============================================================================
"""
You need to install bcrypt for password hashing.
Run this in PythonAnywhere bash console:

pip install bcrypt --user

"""