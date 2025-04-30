import os
import logging
from datetime import datetime
from flask import Flask, session, redirect, url_for, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# Create and configure the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "mess_management_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import all necessary modules
from auth import auth_bp
from student import student_bp
from menu import menu_bp
from attendance import attendance_bp
from analytics import analytics_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(analytics_bp)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Home route
@app.route('/')
def home():
    # Check if the user is logged in
    username = session.get('username')
    if username:
        # If logged in, redirect to dashboard
        return redirect(url_for('analytics.dashboard'))
    # Otherwise, show the homepage
    return render_template('home.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', error="Page not found", now=datetime.now()), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base.html', error="Internal server error", now=datetime.now()), 500

# Add a context processor to make datetime available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Initialize data files on startup
with app.app_context():
    from utils import init_data_files
    init_data_files()
