# Enhanced games.py with detailed exercise tracking and database options
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, jsonify, session
from datetime import datetime, date, timedelta
import json
import random
import os
import sqlite3
from typing import Dict, List, Optional, Any
import hashlib

games_bp = Blueprint('games', __name__)
main_bp = Blueprint('main', __name__)

# Database Configuration
DATABASE_FILE = 'fitness_games.db'
USE_SQLITE = True  # Set to False to use JSON file storage

def init_database():
    """Initialize SQLite database with required tables"""
    if not USE_SQLITE:
        return
        
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Users table - Fixed to include id column for compatibility
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            points INTEGER DEFAULT 0,
            calories_burned REAL DEFAULT 0,
            time_active REAL DEFAULT 0,
            workouts_completed INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0
        )
    ''')
    
    # Game sessions table - Fixed to use user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            game_type TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration REAL,
            score INTEGER,
            points_earned INTEGER,
            calories_burned REAL,
            tracking_method TEXT,
            raw_data TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    # Exercise tracking data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercise_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TIMESTAMP,
            exercise_count INTEGER,
            tracking_method TEXT,
            sensor_data TEXT,
            confidence_score REAL,
            FOREIGN KEY (session_id) REFERENCES game_sessions (session_id)
        )
    ''')
    
    # Game statistics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_stats (
            username TEXT,
            game_type TEXT,
            games_played INTEGER DEFAULT 0,
            best_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            average_score REAL DEFAULT 0,
            last_played TIMESTAMP,
            PRIMARY KEY (username, game_type),
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    # Achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achievement_id TEXT UNIQUE,
            name TEXT,
            description TEXT,
            category TEXT,
            points_reward INTEGER,
            icon TEXT
        )
    ''')
    
    # User achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            username TEXT,
            achievement_id TEXT,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (username, achievement_id),
            FOREIGN KEY (username) REFERENCES users (username),
            FOREIGN KEY (achievement_id) REFERENCES achievements (achievement_id)
        )
    ''')
    
    # Streaks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_streaks (
            username TEXT PRIMARY KEY,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_activity_date DATE,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    # Daily activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            activity_date DATE,
            activity_type TEXT,
            activity_data TEXT,
            points_earned INTEGER,
            calories_burned REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Initialize default achievements
    initialize_achievements()

def initialize_achievements():
    """Initialize default achievements in the database"""
    if not USE_SQLITE:
        return
        
    achievements = [
        {
            'achievement_id': 'first_game',
            'name': 'First Steps',
            'description': 'Play your first fitness game',
            'category': 'beginner',
            'points_reward': 10,
            'icon': 'fa-star'
        },
        {
            'achievement_id': 'streak_3',
            'name': 'Consistent Player',
            'description': 'Play games for 3 days in a row',
            'category': 'streak',
            'points_reward': 25,
            'icon': 'fa-fire'
        },
        {
            'achievement_id': 'streak_7',
            'name': 'Week Warrior',
            'description': 'Play games for 7 days in a row',
            'category': 'streak',
            'points_reward': 75,
            'icon': 'fa-medal'
        },
        {
            'achievement_id': 'streak_30',
            'name': 'Monthly Master',
            'description': 'Play games for 30 days in a row',
            'category': 'streak',
            'points_reward': 300,
            'icon': 'fa-crown'
        },
        {
            'achievement_id': 'squat_master',
            'name': 'Squat Master',
            'description': 'Score 100+ in Squat Tap Challenge',
            'category': 'performance',
            'points_reward': 50,
            'icon': 'fa-arrows-alt-v'
        },
        {
            'achievement_id': 'jump_champion',
            'name': 'Jump Champion',
            'description': 'Score 50+ in Jump Counter',
            'category': 'performance',
            'points_reward': 40,
            'icon': 'fa-arrow-up'
        },
        {
            'achievement_id': 'plank_pro',
            'name': 'Plank Pro',
            'description': 'Hold plank for 120+ seconds',
            'category': 'endurance',
            'points_reward': 60,
            'icon': 'fa-clock'
        },
        {
            'achievement_id': 'burpee_beast',
            'name': 'Burpee Beast',
            'description': 'Complete 25+ burpees',
            'category': 'strength',
            'points_reward': 80,
            'icon': 'fa-dumbbell'
        },
        {
            'achievement_id': 'game_addict',
            'name': 'Game Addict',
            'description': 'Play 100 games total',
            'category': 'milestone',
            'points_reward': 200,
            'icon': 'fa-gamepad'
        },
        {
            'achievement_id': 'calorie_burner',
            'name': 'Calorie Burner',
            'description': 'Burn 1000+ total calories',
            'category': 'fitness',
            'points_reward': 150,
            'icon': 'fa-fire-alt'
        }
    ]
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    for achievement in achievements:
        cursor.execute('''
            INSERT OR IGNORE INTO achievements 
            (achievement_id, name, description, category, points_reward, icon)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            achievement['achievement_id'],
            achievement['name'], 
            achievement['description'],
            achievement['category'],
            achievement['points_reward'],
            achievement['icon']
        ))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    if USE_SQLITE:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    return None

def load_users():
    """Load users from database or JSON file"""
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            users = {}
            for row in cursor.fetchall():
                users[row['username']] = dict(row)
            conn.close()
            return users
    
    # Fallback to JSON
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

def save_user(username: str, user_data: Dict[str, Any]):
    """Save user data to database or JSON file"""
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (username, email, password_hash, points, calories_burned, 
                 time_active, workouts_completed, level, experience)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                username,
                user_data.get('email', ''),
                user_data.get('password_hash', ''),
                user_data.get('points', 0),
                user_data.get('calories_burned', 0),
                user_data.get('time_active', 0),
                user_data.get('workouts_completed', 0),
                user_data.get('level', 1),
                user_data.get('experience', 0)
            ))
            conn.commit()
            conn.close()
            return True
    
    # Fallback to JSON
    users = load_users()
    users[username] = user_data
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)
    return True

def save_game_session(session_data):
    """Save game session to database"""
    if not USE_SQLITE:
        return
        
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO game_sessions
            (session_id, user_id, username, game_type, start_time, end_time, 
             duration, score, points_earned, calories_burned, tracking_method, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data['session_id'],
            session_data.get('user_id'),
            session_data.get('username'),
            session_data['game_type'],
            session_data['start_time'],
            session_data['end_time'],
            session_data['duration'],
            session_data['score'],
            session_data['points_earned'],
            session_data['calories_burned'],
            session_data.get('tracking_method', 'manual'),
            json.dumps(session_data.get('raw_data', {}))
        ))
        conn.commit()
        conn.close()

def save_exercise_tracking_data(tracking_data: List[Dict[str, Any]]):
    """Save exercise tracking data points"""
    if not USE_SQLITE or not tracking_data:
        return
        
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        for data in tracking_data:
            cursor.execute('''
                INSERT INTO exercise_tracking
                (session_id, timestamp, exercise_count, tracking_method, 
                 sensor_data, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['session_id'],
                data['timestamp'],
                data['exercise_count'],
                data['tracking_method'],
                json.dumps(data.get('sensor_data', {})),
                data.get('confidence_score', 0.0)
            ))
        conn.commit()
        conn.close()

def update_game_stats(username: str, game_type: str, score: int):
    """Update game statistics"""
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Get current stats
            cursor.execute('''
                SELECT games_played, best_score, total_score 
                FROM game_stats 
                WHERE username = ? AND game_type = ?
            ''', (username, game_type))
            
            row = cursor.fetchone()
            if row:
                games_played = row['games_played'] + 1
                best_score = max(row['best_score'], score)
                total_score = row['total_score'] + score
            else:
                games_played = 1
                best_score = score
                total_score = score
            
            average_score = total_score / games_played if games_played > 0 else 0
            
            cursor.execute('''
                INSERT OR REPLACE INTO game_stats
                (username, game_type, games_played, best_score, total_score, 
                 average_score, last_played)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, game_type, games_played, best_score, 
                total_score, average_score, datetime.now()
            ))
            
            conn.commit()
            conn.close()

def update_user_streak(username: str):
    """Update user's game streak"""
    if not USE_SQLITE:
        return
        
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Get current streak data
        cursor.execute('''
            SELECT current_streak, longest_streak, last_activity_date 
            FROM user_streaks 
            WHERE username = ?
        ''', (username,))
        
        row = cursor.fetchone()
        today = date.today()
        
        if row:
            last_date = datetime.strptime(row['last_activity_date'], '%Y-%m-%d').date() if row['last_activity_date'] else None
            current_streak = row['current_streak']
            longest_streak = row['longest_streak']
            
            if last_date:
                days_diff = (today - last_date).days
                if days_diff == 1:
                    current_streak += 1
                elif days_diff > 1:
                    current_streak = 1
                # If same day, no change
            else:
                current_streak = 1
                
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 1
            longest_streak = 1
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_streaks
            (username, current_streak, longest_streak, last_activity_date)
            VALUES (?, ?, ?, ?)
        ''', (username, current_streak, longest_streak, today))
        
        conn.commit()
        conn.close()
        
        return current_streak, longest_streak

def check_and_award_achievements(username: str, game_type: str, score: int, user_stats: Dict[str, Any]):
    """Check and award achievements"""
    if not USE_SQLITE:
        return []
        
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    new_achievements = []
    
    # Get all achievements
    cursor.execute('SELECT * FROM achievements')
    all_achievements = cursor.fetchall()
    
    # Get user's current achievements
    cursor.execute('''
        SELECT achievement_id FROM user_achievements WHERE username = ?
    ''', (username,))
    user_achievements = {row['achievement_id'] for row in cursor.fetchall()}
    
    # Get updated stats
    cursor.execute('''
        SELECT SUM(games_played) as total_games FROM game_stats WHERE username = ?
    ''', (username,))
    total_games_row = cursor.fetchone()
    total_games = total_games_row['total_games'] if total_games_row['total_games'] else 0
    
    # Get streak info
    cursor.execute('''
        SELECT current_streak FROM user_streaks WHERE username = ?
    ''', (username,))
    streak_row = cursor.fetchone()
    current_streak = streak_row['current_streak'] if streak_row else 0
    
    # Check each achievement
    for achievement in all_achievements:
        achievement_id = achievement['achievement_id']
        
        if achievement_id in user_achievements:
            continue  # Already earned
            
        should_award = False
        
        # Check conditions
        if achievement_id == 'first_game' and total_games >= 1:
            should_award = True
        elif achievement_id == 'streak_3' and current_streak >= 3:
            should_award = True
        elif achievement_id == 'streak_7' and current_streak >= 7:
            should_award = True
        elif achievement_id == 'streak_30' and current_streak >= 30:
            should_award = True
        elif achievement_id == 'squat_master' and game_type == 'squat_tap' and score >= 100:
            should_award = True
        elif achievement_id == 'jump_champion' and game_type == 'jump_counter' and score >= 50:
            should_award = True
        elif achievement_id == 'plank_pro' and game_type == 'plank_timer' and score >= 120:
            should_award = True
        elif achievement_id == 'burpee_beast' and game_type == 'burpee_challenge' and score >= 25:
            should_award = True
        elif achievement_id == 'game_addict' and total_games >= 100:
            should_award = True
        elif achievement_id == 'calorie_burner' and user_stats.get('calories_burned', 0) >= 1000:
            should_award = True
            
        if should_award:
            # Award achievement
            cursor.execute('''
                INSERT INTO user_achievements (username, achievement_id)
                VALUES (?, ?)
            ''', (username, achievement_id))
            
            new_achievements.append({
                'id': achievement_id,
                'name': achievement['name'],
                'description': achievement['description'],
                'points_reward': achievement['points_reward'],
                'icon': achievement['icon']
            })
    
    conn.commit()
    conn.close()
    
    return new_achievements

def get_current_user():
    """Get current user data from session - Fixed for proper database queries"""
    # First check for user_id (numeric ID)
    user_id = session.get('user_id')
    if user_id:
        if USE_SQLITE:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                # Check if user_id is numeric (database ID) or string (username)
                try:
                    # Try as numeric ID first
                    cursor.execute('SELECT * FROM users WHERE id = ?', (int(user_id),))
                    row = cursor.fetchone()
                    if row:
                        conn.close()
                        return dict(row)
                except (ValueError, TypeError):
                    # If not numeric, try as username
                    cursor.execute('SELECT * FROM users WHERE username = ?', (str(user_id),))
                    row = cursor.fetchone()
                    if row:
                        conn.close()
                        return dict(row)
                conn.close()
        
        # Fallback to JSON
        users = load_users()
        return users.get(str(user_id))
    
    # Fallback to check for username (legacy support)
    username = session.get('username')
    if username:
        if USE_SQLITE:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    return dict(row)
        
        users = load_users()
        # Search by username in JSON data
        for user in users.values():
            if user.get('username') == username:
                return user
    
    return None

# Initialize database on import
init_database()

@games_bp.route('/')
def games():
    """Main games page"""
    user_data = get_current_user()
    if not user_data:
        return render_template('games.html', game_stats=None)
    
    # Get game statistics from database
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT game_type, games_played, best_score, total_score, average_score
                FROM game_stats WHERE username = ?
            ''', (user_data['username'],))
            
            game_stats = {}
            for row in cursor.fetchall():
                game_stats[row['game_type']] = dict(row)
            
            # Get streak info
            cursor.execute('''
                SELECT current_streak, longest_streak FROM user_streaks WHERE username = ?
            ''', (user_data['username'],))
            streak_row = cursor.fetchone()
            
            conn.close()
            
            return render_template('games.html', 
                                 game_stats=game_stats,
                                 current_streak=streak_row['current_streak'] if streak_row else 0,
                                 longest_streak=streak_row['longest_streak'] if streak_row else 0)
    
    return render_template('games.html', game_stats=None)

@games_bp.route('/start_game', methods=['POST'])
def start_game():
    user_data = get_current_user()
    if not user_data:
        return jsonify({'error': 'User not logged in'}), 401
    
    # Use appropriate user identifier
    user_id = user_data.get('id') or user_data.get('username')
    username = user_data.get('username')
    
    game_type = request.json.get('game_type')
    tracking_method = request.json.get('tracking_method', 'manual')
    
    session_id = f"{username}_{game_type}_{datetime.now().timestamp()}"
    
    session['current_game'] = {
        'session_id': session_id,
        'user_id': user_id,
        'username': username,
        'type': game_type,
        'start_time': datetime.now().isoformat(),
        'score': 0,
        'tracking_method': tracking_method,
        'exercise_tracking_data': [],
        'sensor_readings': []
    }
    
    return jsonify({
        'status': 'success',
        'game_type': game_type,
        'session_id': session_id,
        'tracking_method': tracking_method
    })

@games_bp.route('/update_score', methods=['POST'])
def update_score():
    """Update game score with exercise tracking data"""
    if 'current_game' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    score = request.json.get('score', 0)
    tracking_data = request.json.get('tracking_data', {})
    sensor_data = request.json.get('sensor_data', {})
    
    # Update session data
    session['current_game']['score'] = score
    
    # Store tracking data point
    tracking_point = {
        'session_id': session['current_game']['session_id'],
        'timestamp': datetime.now().isoformat(),
        'exercise_count': score,
        'tracking_method': session['current_game']['tracking_method'],
        'sensor_data': sensor_data,
        'confidence_score': tracking_data.get('confidence', 0.8)
    }
    
    session['current_game']['exercise_tracking_data'].append(tracking_point)
    
    return jsonify({
        'status': 'success', 
        'score': score,
        'tracking_data_stored': True
    })

@games_bp.route('/end_game', methods=['POST'])
def end_game():
    """End game session and save all data"""
    user_data = get_current_user()
    if not user_data or 'current_game' not in session:
        return jsonify({'error': 'No active game or user not logged in'}), 400
    
    game_data = session['current_game']
    game_type = game_data['type']
    score = game_data['score']
    username = user_data['username']
    
    # Calculate duration
    start_time = datetime.fromisoformat(game_data['start_time'])
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60  # minutes
    
    # Calculate points and calories
    points_earned, calories_burned = calculate_rewards(game_type, score, duration)
    
    # Update user stats
    user_data['points'] = user_data.get('points', 0) + points_earned
    user_data['calories_burned'] = user_data.get('calories_burned', 0) + calories_burned
    user_data['time_active'] = user_data.get('time_active', 0) + duration
    user_data['workouts_completed'] = user_data.get('workouts_completed', 0) + 1
    
    # Save updated user data
    save_user(username, user_data)
    
    # Save game session
    session_data = {
        'session_id': game_data['session_id'],
        'user_id': user_data.get('id'),
        'username': username,
        'game_type': game_type,
        'start_time': game_data['start_time'],
        'end_time': end_time.isoformat(),
        'duration': duration,
        'score': score,
        'points_earned': points_earned,
        'calories_burned': calories_burned,
        'tracking_method': game_data['tracking_method'],
        'raw_data': {
            'exercise_tracking_data': game_data.get('exercise_tracking_data', []),
            'sensor_readings': game_data.get('sensor_readings', [])
        }
    }
    save_game_session(session_data)
    
    # Save exercise tracking data
    save_exercise_tracking_data(game_data.get('exercise_tracking_data', []))
    
    # Update game statistics
    update_game_stats(username, game_type, score)
    
    # Update streak
    current_streak, longest_streak = update_user_streak(username)
    
    # Check achievements
    new_achievements = check_and_award_achievements(
        username, game_type, score, user_data
    )
    
    # Get updated best score
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT best_score FROM game_stats 
                WHERE username = ? AND game_type = ?
            ''', (username, game_type))
            row = cursor.fetchone()
            best_score = row['best_score'] if row else score
            conn.close()
        else:
            best_score = score
    else:
        best_score = score
    
    # Clear current game from session
    session.pop('current_game', None)
    
    return jsonify({
        'status': 'success',
        'points_earned': points_earned,
        'calories_burned': calories_burned,
        'duration': duration,
        'total_points': user_data['points'],
        'new_achievements': new_achievements,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'best_score': best_score,
        'is_personal_best': score == best_score,
        'session_id': game_data['session_id']
    })

def calculate_rewards(game_type: str, score: int, duration: float) -> tuple:
    """Calculate points and calories based on game type and performance"""
    base_multipliers = {
        'squat_tap': {'points': 2, 'calories': 0.5},
        'jump_counter': {'points': 3, 'calories': 0.8},
        'plank_timer': {'points': 5, 'calories': 0.1},
        'burpee_challenge': {'points': 10, 'calories': 1.5}
    }
    
    multiplier = base_multipliers.get(game_type, {'points': 1, 'calories': 0.3})
    
    # Base calculation
    points_earned = int(score * multiplier['points'])
    calories_burned = score * multiplier['calories']
    
    # Duration bonus (for longer sessions)
    if duration > 5:  # More than 5 minutes
        points_earned = int(points_earned * 1.2)
        calories_burned *= 1.1
    
    return points_earned, round(calories_burned, 2)

@games_bp.route('/leaderboard/<game_type>')
def get_leaderboard(game_type):
    """Get leaderboard for specific game type"""
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.username, gs.best_score, gs.games_played, gs.average_score
                FROM game_stats gs
                JOIN users u ON gs.username = u.username
                WHERE gs.game_type = ? AND gs.best_score > 0
                ORDER BY gs.best_score DESC
                LIMIT 10
            ''', (game_type,))
            
            leaderboard = []
            for row in cursor.fetchall():
                leaderboard.append({
                    'username': row['username'],
                    'best_score': row['best_score'],
                    'games_played': row['games_played'],
                    'average_score': round(row['average_score'], 1)
                })
            
            conn.close()
            return jsonify(leaderboard)
    
    return jsonify([])

@games_bp.route('/user_stats')
def get_user_stats():
    """Get comprehensive user statistics"""
    user_data = get_current_user()
    if not user_data:
        return jsonify({'error': 'User not logged in'}), 401
    
    stats = {
        'basic_stats': {
            'points': user_data.get('points', 0),
            'calories_burned': user_data.get('calories_burned', 0),
            'time_active': user_data.get('time_active', 0),
            'workouts_completed': user_data.get('workouts_completed', 0),
            'level': user_data.get('level', 1),
            'experience': user_data.get('experience', 0)
        }
    }
    
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Get game stats
            cursor.execute('''
                SELECT * FROM game_stats WHERE username = ?
            ''', (user_data['username'],))
            game_stats = {}
            for row in cursor.fetchall():
                game_stats[row['game_type']] = dict(row)
            
            # Get streak info
            cursor.execute('''
                SELECT * FROM user_streaks WHERE username = ?
            ''', (user_data['username'],))
            streak_row = cursor.fetchone()
            
            # Get achievements
            cursor.execute('''
                SELECT a.*, ua.earned_at
                FROM achievements a
                JOIN user_achievements ua ON a.achievement_id = ua.achievement_id
                WHERE ua.username = ?
                ORDER BY ua.earned_at DESC
            ''', (user_data['username'],))
            achievements = [dict(row) for row in cursor.fetchall()]
            
            # Get recent sessions
            cursor.execute('''
                SELECT * FROM game_sessions 
                WHERE username = ? 
                ORDER BY end_time DESC 
                LIMIT 10
            ''', (user_data['username'],))
            recent_sessions = [dict(row) for row in cursor.fetchall()]
            
            conn.close()

            
            stats.update({
                'game_stats': game_stats,
                'streak_info': dict(streak_row) if streak_row else None,
                'achievements': achievements,
                'recent_sessions': recent_sessions
            })
    
    return jsonify(stats)

@games_bp.route('/game_data')
def game_data():
    """Provide game configuration data"""
    return jsonify({
        'squat_tap': {
            'name': 'Squat Tap Challenge',
            'description': 'Tap the screen while doing',
            'icon': 'fa-arrows-alt-v',
            'target_score': 50,
            'time_limit': 60,
            'points_per_unit': 2,
            'calories_per_unit': 0.5
        },
        'jump_counter': {
            'name': 'Jump Counter',
            'description': 'Jump and tap to count your jumps!',
            'icon': 'fa-arrow-up',
            'target_score': 30,
            'time_limit': 60,
            'points_per_unit': 3,
            'calories_per_unit': 0.8
        },
        'plank_timer': {
            'name': 'Plank Timer',
            'description': 'Hold your plank and beat the timer!',
            'icon': 'fa-clock',
            'target_score': 60,
            'time_limit': 300,  
            'points_per_unit': 5,
            'calories_per_unit': 0.1
        }
    })


@main_bp.route('/capture_exercise', methods=['POST'])
def capture_exercise():
    """Capture exercise data from tracking systems"""
    user_data = get_current_user()
    if not user_data:
        return jsonify({'error': 'User not logged in'}), 401
    
    data = request.json
    exercise_type = data.get('exercise_type')
    count = data.get('count', 1)
    tracking_method = data.get('tracking_method', 'manual')
    sensor_data = data.get('sensor_data', {})
    confidence_score = data.get('confidence', 0.8)
    
    # Create tracking data entry
    tracking_entry = {
        'session_id': f"manual_{user_data['username']}_{datetime.now().timestamp()}",
        'timestamp': datetime.now().isoformat(),
        'exercise_count': count,
        'tracking_method': tracking_method,
        'sensor_data': sensor_data,
        'confidence_score': confidence_score
    }
    
    # Save tracking data
    save_exercise_tracking_data([tracking_entry])
    
    # Calculate calories and points
    calories_per_exercise = {
        'squat': 0.5,
        'jump': 0.8,
        'pushup': 0.3,
        'burpee': 1.5,
        'plank_second': 0.1
    }
    
    calories_burned = count * calories_per_exercise.get(exercise_type, 0.3)
    points_earned = count * 2
    
    # Update user stats
    user_data['calories_burned'] = user_data.get('calories_burned', 0) + calories_burned
    user_data['points'] = user_data.get('points', 0) + points_earned
    user_data['workouts_completed'] = user_data.get('workouts_completed', 0) + 1
    
    # Save updated user data
    save_user(user_data['username'], user_data)
    
    # Update streak and check achievements
    current_streak, longest_streak = update_user_streak(user_data['username'])
    new_achievements = check_and_award_achievements(
        user_data['username'], exercise_type, count, user_data
    )
    
    return jsonify({
        'status': 'success',
        'points_earned': points_earned,
        'calories_burned': calories_burned,
        'total_points': user_data['points'],
        'new_achievements': new_achievements,
        'current_streak': current_streak
    })

@main_bp.route('/get_exercise_history')
def get_exercise_history():
    """Get user's exercise history"""
    user_data = get_current_user()
    if not user_data:
        return jsonify({'error': 'User not logged in'}), 401
    
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT et.*, gs.game_type, gs.score, gs.start_time, gs.duration
                FROM exercise_tracking et
                LEFT JOIN game_sessions gs ON et.session_id = gs.session_id
                WHERE gs.username = ? OR et.session_id LIKE ?
                ORDER BY et.timestamp DESC
                LIMIT 50
            ''', (user_data['username'], f"manual_{user_data['username']}%"))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'timestamp': row['timestamp'],
                    'exercise_count': row['exercise_count'],
                    'tracking_method': row['tracking_method'],
                    'game_type': row['game_type'] if row['game_type'] else 'manual_exercise',
                    'score': row['score'] if row['score'] else row['exercise_count'],
                    'confidence_score': row['confidence_score']
                })
            
            conn.close()
            return jsonify(history)
    
    return jsonify([])

@main_bp.route('/dashboard')
def dashboard():
    """Enhanced dashboard with exercise tracking stats"""
    user_data = get_current_user()
    if not user_data:
        flash('Please log in first', 'error')
        return redirect(url_for('auth.login'))
    
    dashboard_stats = {
        'total_points': user_data.get('points', 0),
        'calories_burned': user_data.get('calories_burned', 0),
        'workouts_completed': user_data.get('workouts_completed', 0),
        'time_active': user_data.get('time_active', 0)
    }
    
    # Get recent exercise data
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Get recent sessions
            cursor.execute('''
                SELECT game_type, score, calories_burned, duration, end_time
                FROM game_sessions 
                WHERE username = ? 
                ORDER BY end_time DESC 
                LIMIT 5
            ''', (user_data['username'],))
            recent_workouts = [dict(row) for row in cursor.fetchall()]
            
            # Get exercise tracking stats for today
            cursor.execute('''
                SELECT COUNT(*) as exercises_today, SUM(exercise_count) as total_exercises
                FROM exercise_tracking et
                JOIN game_sessions gs ON et.session_id = gs.session_id
                WHERE gs.username = ? AND DATE(et.timestamp) = DATE('now')
            ''', (user_data['username'],))
            today_stats = cursor.fetchone()
            
            # Get streak info
            cursor.execute('''
                SELECT current_streak, longest_streak 
                FROM user_streaks 
                WHERE username = ?
            ''', (user_data['username'],))
            streak_info = cursor.fetchone()
            
            conn.close()
            
            dashboard_stats.update({
                'recent_workouts': recent_workouts,
                'exercises_today': today_stats['total_exercises'] if today_stats else 0,
                'current_streak': streak_info['current_streak'] if streak_info else 0,
                'longest_streak': streak_info['longest_streak'] if streak_info else 0
            })
    
    return render_template('dashboard.html', stats=dashboard_stats)

@main_bp.route('/check_usage_limit')
def check_usage_limit():
    daily_limit = 120  # 2 hours in minutes
    current_usage = session.get('daily_usage', 0)
    
    if current_usage >= daily_limit:
        return jsonify({'limit_reached': True, 'remaining_time': 0})
    else:
        return jsonify({'limit_reached': False, 'remaining_time': daily_limit - current_usage})

def award_badge(username, badge_id):
    """Award a badge to the user if they don't already have it"""
    if USE_SQLITE:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if user already has this achievement
            cursor.execute('''
                SELECT achievement_id FROM user_achievements 
                WHERE username = ? AND achievement_id = ?
            ''', (username, badge_id))
            
            if not cursor.fetchone():
                # Award the achievement
                cursor.execute('''
                    INSERT INTO user_achievements (username, achievement_id)
                    VALUES (?, ?)
                ''', (username, badge_id))
                
                # Get points reward
                cursor.execute('''
                    SELECT points_reward FROM achievements WHERE achievement_id = ?
                ''', (badge_id,))
                achievement_row = cursor.fetchone()
                points_reward = achievement_row['points_reward'] if achievement_row else 50
                
                # Update user points
                cursor.execute('''
                    UPDATE users SET points = points + ? WHERE username = ?
                ''', (points_reward, username))
                
                conn.commit()
                conn.close()
                return True
    
    # Fallback to session-based badges
    if badge_id not in session.get('badges', []):
        badges = session.get('badges', [])
        badges.append(badge_id)
        session['badges'] = badges
        session['points'] = session.get('points', 0) + 50
        return True
    return False

def check_badge_requirements():
    """Check if user has earned any new badges"""
    user_data = get_current_user()
    if not user_data:
        return []
    
    new_badges = []
    username = user_data['username']
    
    # First workout badge
    if user_data.get('workouts_completed', 0) >= 1:
        if award_badge(username, 'first_workout'):
            new_badges.append('first_workout')
    
    # Calorie burner badge
    if user_data.get('calories_burned', 0) >= 1000:
        if award_badge(username, 'calorie_burner'):
            new_badges.append('calorie_burner')
    
    # Time warrior badge
    if user_data.get('time_active', 0) >= 60:
        if award_badge(username, 'time_warrior'):
            new_badges.append('time_warrior')
    
    # Points collector badge
    if user_data.get('points', 0) >= 500:
        if award_badge(username, 'points_collector'):
            new_badges.append('points_collector')
    
    return new_badges

@main_bp.route('/sync_exercise_data', methods=['POST'])
def sync_exercise_data():
    """Sync exercise data from external devices or apps"""
    user_data = get_current_user()
    if not user_data:
        return jsonify({'error': 'User not logged in'}), 401
    
    data = request.json
    exercise_sessions = data.get('sessions', [])
    
    synced_count = 0
    total_calories = 0
    total_points = 0
    
    for session in exercise_sessions:
        # Create tracking data
        tracking_data = {
            'session_id': f"sync_{user_data['username']}_{datetime.now().timestamp()}_{synced_count}",
            'timestamp': session.get('timestamp', datetime.now().isoformat()),
            'exercise_count': session.get('count', 1),
            'tracking_method': session.get('source', 'external_sync'),
            'sensor_data': session.get('data', {}),
            'confidence_score': session.get('confidence', 0.9)
        }
        
        save_exercise_tracking_data([tracking_data])
        
        # Calculate rewards
        calories = session.get('calories', session.get('count', 1) * 0.5)
        points = session.get('points', session.get('count', 1) * 2)
        
        total_calories += calories
        total_points += points
        synced_count += 1
    
    # Update user stats
    if synced_count > 0:
        user_data['calories_burned'] = user_data.get('calories_burned', 0) + total_calories
        user_data['points'] = user_data.get('points', 0) + total_points
        user_data['workouts_completed'] = user_data.get('workouts_completed', 0) + synced_count
        save_user(user_data['username'], user_data)
        
        # Check for new achievements
        new_achievements = check_and_award_achievements(
            user_data['username'], 'synced_exercise', synced_count, user_data
        )
    
    return jsonify({
        'status': 'success',
        'synced_sessions': synced_count,
        'total_calories': total_calories,
        'total_points': total_points,
        'new_achievements': new_achievements if synced_count > 0 else []
    })