from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import json
import random

games_bp = Blueprint('games', __name__)

@games_bp.route('/')
def games():
    return render_template('games.html')

@games_bp.route('/start_game', methods=['POST'])
def start_game():
    game_type = request.json.get('game_type')
    session['current_game'] = {
        'type': game_type,
        'start_time': datetime.now().isoformat(),
        'score': 0,
        'duration': 0
    }
    
    # Increment daily usage
    session['daily_usage'] = session.get('daily_usage', 0) + 1
    
    return jsonify({'status': 'success', 'game_type': game_type})

@games_bp.route('/update_score', methods=['POST'])
def update_score():
    if 'current_game' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    score = request.json.get('score', 0)
    session['current_game']['score'] = score
    
    return jsonify({'status': 'success', 'score': score})

@games_bp.route('/end_game', methods=['POST'])
def end_game():
    if 'current_game' not in session:
        return jsonify({'error': 'No active game'}), 400
    
    game_data = session['current_game']
    game_type = game_data['type']
    score = game_data['score']
    
    # Calculate duration in minutes
    start_time = datetime.fromisoformat(game_data['start_time'])
    duration = (datetime.now() - start_time).total_seconds() / 60
    
    # Calculate points and calories based on game type and score
    points_earned = 0
    calories_burned = 0
    
    if game_type == 'squat_tap':
        points_earned = score * 2
        calories_burned = score * 0.5
    elif game_type == 'jump_counter':
        points_earned = score * 3
        calories_burned = score * 0.8
    elif game_type == 'plank_timer':
        points_earned = int(score * 5)  # score is time in seconds
        calories_burned = score * 0.1
    elif game_type == 'burpee_challenge':
        points_earned = score * 10
        calories_burned = score * 1.5
    
    # Update session data
    session['points'] = session.get('points', 0) + points_earned
    session['calories_burned'] = session.get('calories_burned', 0) + calories_burned
    session['time_active'] = session.get('time_active', 0) + duration
    session['workouts_completed'] = session.get('workouts_completed', 0) + 1
    
    # Log activity
    activity = {
        'activity_id': f"game_{datetime.now().timestamp()}",
        'type': game_type,
        'score': score,
        'points_earned': points_earned,
        'calories_burned': calories_burned,
        'duration': duration,
        'timestamp': datetime.now().isoformat()
    }
    
    activities = session.get('activities', [])
    activities.append(activity)
    session['activities'] = activities
    
    # Check for new badges
    from blueprints.main import check_badge_requirements
    new_badges = check_badge_requirements()
    
    # Clear current game
    session.pop('current_game', None)
    
    return jsonify({
        'status': 'success',
        'points_earned': points_earned,
        'calories_burned': calories_burned,
        'total_points': session.get('points', 0),
        'new_badges': new_badges
    })

@games_bp.route('/game_data')
def game_data():
    """Provide game configuration data"""
    return jsonify({
        'squat_tap': {
            'name': 'Squat Tap Challenge',
            'description': 'Tap the screen while doing squats!',
            'icon': 'fa-arrows-alt-v',
            'target_score': 50,
            'time_limit': 60
        },
        'jump_counter': {
            'name': 'Jump Counter',
            'description': 'Jump and tap to count your jumps!',
            'icon': 'fa-arrow-up',
            'target_score': 30,
            'time_limit': 60
        },
        'plank_timer': {
            'name': 'Plank Timer',
            'description': 'Hold your plank and beat the timer!',
            'icon': 'fa-clock',
            'target_score': 60,
            'time_limit': 300
        },
        'burpee_challenge': {
            'name': 'Burpee Challenge',
            'description': 'Complete burpees for maximum points!',
            'icon': 'fa-dumbbell',
            'target_score': 20,
            'time_limit': 120
        }
    })
