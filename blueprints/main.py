from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        session['username'] = request.form.get('username', session.get('username'))
        session['age'] = int(request.form.get('age', session.get('age', 18)))
        session['weight'] = float(request.form.get('weight', session.get('weight', 70)))
        session['fitness_goal'] = request.form.get('fitness_goal', session.get('fitness_goal', 'weight_loss'))
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('profile.html')

@main_bp.route('/leaderboard')
def leaderboard():
    # Mock leaderboard data for demonstration
    leaderboard_data = [
        {'username': session.get('username', 'You'), 'points': session.get('points', 0), 'rank': 1},
        {'username': 'FitChampion', 'points': max(0, session.get('points', 0) - 50), 'rank': 2},
        {'username': 'HealthyHero', 'points': max(0, session.get('points', 0) - 100), 'rank': 3},
        {'username': 'ActiveAce', 'points': max(0, session.get('points', 0) - 150), 'rank': 4},
        {'username': 'FitnessFan', 'points': max(0, session.get('points', 0) - 200), 'rank': 5}
    ]
    
    # Sort by points
    leaderboard_data.sort(key=lambda x: x['points'], reverse=True)
    
    # Update ranks
    for i, user in enumerate(leaderboard_data):
        user['rank'] = i + 1
    
    return render_template('leaderboard.html', leaderboard=leaderboard_data)

@main_bp.route('/check_usage_limit')
def check_usage_limit():
    daily_limit = 120  # 2 hours in minutes
    current_usage = session.get('daily_usage', 0)
    
    if current_usage >= daily_limit:
        return {'limit_reached': True, 'remaining_time': 0}
    else:
        return {'limit_reached': False, 'remaining_time': daily_limit - current_usage}

def award_badge(badge_id):
    """Award a badge to the user if they don't already have it"""
    if badge_id not in session.get('badges', []):
        badges = session.get('badges', [])
        badges.append(badge_id)
        session['badges'] = badges
        session['points'] = session.get('points', 0) + 50  # Bonus points for badge
        return True
    return False

def check_badge_requirements():
    """Check if user has earned any new badges"""
    new_badges = []
    
    # First workout badge
    if session.get('workouts_completed', 0) >= 1:
        if award_badge('first_workout'):
            new_badges.append('first_workout')
    
    # Calorie burner badge
    if session.get('calories_burned', 0) >= 1000:
        if award_badge('calorie_burner'):
            new_badges.append('calorie_burner')
    
    # Time warrior badge
    if session.get('time_active', 0) >= 60:
        if award_badge('time_warrior'):
            new_badges.append('time_warrior')
    
    # Points collector badge
    if session.get('points', 0) >= 500:
        if award_badge('points_collector'):
            new_badges.append('points_collector')
    
    return new_badges
