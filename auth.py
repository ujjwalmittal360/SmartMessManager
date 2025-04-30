import csv
import os
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import USERS_CSV
from utils import read_csv, write_csv

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password', 'danger')
            return render_template('login.html')
        
        # Read users from CSV
        users_df = read_csv(USERS_CSV)
        
        if users_df.empty:
            flash('No users found. Contact the system administrator.', 'danger')
            return render_template('login.html')
        
        # Find the user
        user = users_df[users_df['username'] == username]
        
        if user.empty or not check_password_hash(user.iloc[0]['password'], password):
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
        
        # User authenticated, set session
        session['username'] = username
        session['role'] = user.iloc[0]['role']
        
        flash(f'Welcome, {username}!', 'success')
        return redirect(url_for('analytics.dashboard'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Handle password change."""
    if 'username' not in session:
        flash('You must be logged in to change your password', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('Please fill in all fields', 'danger')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('change_password.html')
        
        # Read users from CSV
        users_df = read_csv(USERS_CSV)
        
        # Find the user
        user_idx = users_df.index[users_df['username'] == session['username']].tolist()
        
        if not user_idx or not check_password_hash(users_df.iloc[user_idx[0]]['password'], current_password):
            flash('Current password is incorrect', 'danger')
            return render_template('change_password.html')
        
        # Update password
        users_df.at[user_idx[0], 'password'] = generate_password_hash(new_password)
        
        # Write updated data back to CSV
        if write_csv(users_df, USERS_CSV):
            flash('Password changed successfully', 'success')
            return redirect(url_for('analytics.dashboard'))
        else:
            flash('Error changing password', 'danger')
    
    return render_template('change_password.html')

# Decorator to require login for routes
def login_required(view_func):
    def wrapped_view(*args, **kwargs):
        if 'username' not in session:
            flash('You must be logged in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

# Decorator to require admin role for routes
def admin_required(view_func):
    def wrapped_view(*args, **kwargs):
        if 'username' not in session:
            flash('You must be logged in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('analytics.dashboard'))
        return view_func(*args, **kwargs)
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view
