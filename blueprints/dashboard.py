from flask import Blueprint, render_template, jsonify, session
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    # Calculate weekly progress
    weekly_data = calculate_weekly_progress()
    recent_activities = get_recent_activities()
    
    return render_template('dashboard.html', 
                         weekly_data=weekly_data,
                         recent_activities=recent_activities)

@dashboard_bp.route('/stats')
def stats():
    """Return current user statistics"""
    return jsonify({
        'points': session.get('points', 0),
        'badges': len(session.get('badges', [])),
        'workouts_completed': session.get('workouts_completed', 0),
        'calories_burned': session.get('calories_burned', 0),
        'time_active': session.get('time_active', 0),
        'daily_usage': session.get('daily_usage', 0)
    })

@dashboard_bp.route('/weekly_progress')
def weekly_progress():
    """Return weekly progress data for charts"""
    return jsonify(calculate_weekly_progress())

def calculate_weekly_progress():
    """Calculate weekly progress based on user activities"""
    # Get last 7 days
    today = datetime.now()
    week_data = []
    
    for i in range(7):
        date = today - timedelta(days=i)
        day_name = date.strftime('%A')
        
        # Mock data based on current session progress
        # In a real app, this would query actual daily data
        daily_calories = session.get('calories_burned', 0) // 7 if i < 3 else 0
        daily_workouts = 1 if i < 3 and session.get('workouts_completed', 0) > 0 else 0
        daily_time = session.get('time_active', 0) // 7 if i < 3 else 0
        
        week_data.append({
            'day': day_name,
            'calories': daily_calories,
            'workouts': daily_workouts,
            'time_active': daily_time
        })
    
    return list(reversed(week_data))

def get_recent_activities():
    """Get recent activities for the activity feed"""
    activities = session.get('activities', [])
    
    # Sort by timestamp and get latest 10
    sorted_activities = sorted(activities, 
                             key=lambda x: x['timestamp'], 
                             reverse=True)[:10]
    
    # Format for display
    formatted_activities = []
    for activity in sorted_activities:
        formatted_activities.append({
            'type': activity['type'].replace('_', ' ').title(),
            'points': activity['points_earned'],
            'calories': activity['calories_burned'],
            'duration': round(activity['duration'], 1),
            'timestamp': datetime.fromisoformat(activity['timestamp']).strftime('%H:%M - %b %d')
        })
    
    return formatted_activities

@dashboard_bp.route('/achievement_progress')
def achievement_progress():
    """Return progress towards next achievements"""
    progress = {
        'next_workout': {
            'name': 'Workout Streak',
            'description': 'Complete 7 workouts',
            'current': session.get('workouts_completed', 0),
            'target': 7,
            'progress': min(100, (session.get('workouts_completed', 0) / 7) * 100)
        },
        'next_calories': {
            'name': 'Calorie Burner',
            'description': 'Burn 1000 calories',
            'current': session.get('calories_burned', 0),
            'target': 1000,
            'progress': min(100, (session.get('calories_burned', 0) / 1000) * 100)
        },
        'next_time': {
            'name': 'Time Warrior',
            'description': 'Be active for 60 minutes',
            'current': session.get('time_active', 0),
            'target': 60,
            'progress': min(100, (session.get('time_active', 0) / 60) * 100)
        }
    }
    
    return jsonify(progress)
