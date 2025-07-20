from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Path to user data file
USER_DATA_FILE = 'users.json'

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4, default=str)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user data"""
    if 'user_id' not in session:
        return None
    
    users = load_users()
    return users.get(session['user_id'])

def create_user_profile(user_id, username, email):
    """Create initial user profile data"""
    return {
        'id': user_id,
        'username': username,
        'email': email,
        'created_at': datetime.now().isoformat(),
        'profile': {
            'level': 1,
            'xp': 0,
            'total_workouts': 0,
            'streak': 0,
            'daily_usage': 0,
            'badges': [],
            'avatar': 'default.png'
        },
        'games': {
            'fitness_quest': {
                'level': 1,
                'score': 0,
                'completed_challenges': []
            },
            'step_counter': {
                'daily_steps': 0,
                'total_steps': 0,
                'step_goal': 10000
            }
        },
        'diet': {
            'daily_calories': 0,
            'calorie_goal': 2000,
            'meals': [],
            'water_intake': 0
        },
        'workouts': []
    }

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')
        
        users = load_users()
        
        # Find user by email
        user = None
        user_id = None
        for uid, user_data in users.items():
            if user_data.get('email', '').lower() == email:
                user = user_data
                user_id = uid
                break
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user_id
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return render_template('auth/signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/signup.html')
        
        users = load_users()
        
        # Check if email already exists
        for user_data in users.values():
            if user_data.get('email', '').lower() == email:
                flash('Email already registered. Please use a different email.', 'error')
                return render_template('auth/signup.html')
        
        # Check if username already exists
        for user_data in users.values():
            if user_data.get('username', '').lower() == username.lower():
                flash('Username already taken. Please choose a different username.', 'error')
                return render_template('auth/signup.html')
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)
        
        user_profile = create_user_profile(user_id, username, email)
        user_profile['password'] = hashed_password
        
        users[user_id] = user_profile
        save_users(users)
        
        # Log the user in
        session['user_id'] = user_id
        session['username'] = username
        
        flash(f'Welcome to FitPlay, {username}! Your account has been created.', 'success')
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('auth/signup.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    return render_template('profile.html', user=user)

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user_id = session['user_id']
    users = load_users()
    
    if user_id not in users:
        flash('User not found.', 'error')
        return redirect(url_for('auth.profile'))
    
    # Update profile fields
    username = request.form.get('username', '').strip()
    if username and username != users[user_id]['username']:
        # Check if new username is taken
        for uid, user_data in users.items():
            if uid != user_id and user_data.get('username', '').lower() == username.lower():
                flash('Username already taken.', 'error')
                return redirect(url_for('auth.profile'))
        
        users[user_id]['username'] = username
        session['username'] = username
    
    # Update other profile fields if needed
    calorie_goal = request.form.get('calorie_goal')
    step_goal = request.form.get('step_goal')
    
    if calorie_goal:
        try:
            users[user_id]['diet']['calorie_goal'] = int(calorie_goal)
        except ValueError:
            pass
    
    if step_goal:
        try:
            users[user_id]['games']['step_counter']['step_goal'] = int(step_goal)
        except ValueError:
            pass
    
    save_users(users)
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

# Helper function to update user data
def update_user_data(user_id, data_path, value):
    """Update specific user data field"""
    users = load_users()
    if user_id in users:
        # Navigate to nested dict using data_path (e.g., "profile.xp")
        keys = data_path.split('.')
        current = users[user_id]
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        save_users(users)
        return True
    return False

# API endpoints for updating user progress
@auth_bp.route('/api/update_xp', methods=['POST'])
@login_required
def update_xp():
    data = request.json
    xp_gain = data.get('xp', 0)
    
    user_id = session['user_id']
    users = load_users()
    
    if user_id in users:
        current_xp = users[user_id]['profile']['xp']
        new_xp = current_xp + xp_gain
        users[user_id]['profile']['xp'] = new_xp
        
        # Level up logic (every 1000 XP = 1 level)
        new_level = (new_xp // 1000) + 1
        if new_level > users[user_id]['profile']['level']:
            users[user_id]['profile']['level'] = new_level
            flash(f'Congratulations! You reached level {new_level}!', 'success')
        
        save_users(users)
        return jsonify({'success': True, 'new_xp': new_xp, 'level': new_level})
    
    return jsonify({'success': False}), 400