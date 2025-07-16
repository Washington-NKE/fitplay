import os
import logging
from datetime import datetime, timedelta
from flask import Flask, session
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fitplay-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'fitplay:'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

Session(app)

# Initialize session data
@app.before_request
def initialize_session():
    if 'user_id' not in session:
        session['user_id'] = 'guest'
        session['username'] = 'FitPlayer'
        session['points'] = 0
        session['badges'] = []
        session['workouts_completed'] = 0
        session['calories_burned'] = 0
        session['time_active'] = 0
        session['daily_usage'] = 0
        session['last_activity'] = datetime.now().isoformat()
        session['activities'] = []
        session['age'] = 18
        session['weight'] = 70
        session['fitness_goal'] = 'weight_loss'
        session['diet_plan'] = []

# Register blueprints
from blueprints.main import main_bp
from blueprints.games import games_bp
from blueprints.dashboard import dashboard_bp
from blueprints.diet import diet_bp

app.register_blueprint(main_bp)
app.register_blueprint(games_bp, url_prefix='/games')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(diet_bp, url_prefix='/diet')

# Global template variables
@app.context_processor
def inject_globals():
    return {
        'current_user': {
            'username': session.get('username', 'FitPlayer'),
            'points': session.get('points', 0),
            'badges': session.get('badges', []),
            'workouts_completed': session.get('workouts_completed', 0),
            'calories_burned': session.get('calories_burned', 0),
            'time_active': session.get('time_active', 0),
            'daily_usage': session.get('daily_usage', 0)
        }
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
