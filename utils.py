import os
import csv
import logging
import pandas as pd
from datetime import datetime
from config import DATA_DIR, USERS_CSV, STUDENTS_CSV, ATTENDANCE_CSV, MENU_CSV, MEAL_PREPARATION_CSV, STUDENT_IMAGES_DIR

def ensure_dir_exists(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def init_data_files():
    """Initialize data directories and CSV files if they don't exist."""
    # Create data directory if it doesn't exist
    ensure_dir_exists(DATA_DIR)
    ensure_dir_exists(STUDENT_IMAGES_DIR)
    
    # Initialize users.csv if it doesn't exist
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password', 'role'])
            # Add a default admin user (password: admin123)
            writer.writerow(['admin', 'scrypt:32768:8:1$3dQrJ21JQ79BH8pG$527ed2e4fb7d8022b385a971ffc6309e49ed4bfefac2c01ffffd57668f394a58568f77f1a2a33166894605928775597f4ec8418668fcc8283f2fc2d5f78eff1e', 'admin'])
    
    # Initialize students.csv if it doesn't exist
    if not os.path.exists(STUDENTS_CSV):
        with open(STUDENTS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'roll_number', 'image_path', 'registration_date'])
    
    # Initialize attendance.csv if it doesn't exist
    if not os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'student_id', 'date', 'time', 'meal_type', 'leftover_weight'])
    
    # Initialize menu.csv if it doesn't exist
    if not os.path.exists(MENU_CSV):
        with open(MENU_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'day', 'meal_type', 'meal_name', 'description'])
    
    # Initialize meal_preparation.csv if it doesn't exist
    if not os.path.exists(MEAL_PREPARATION_CSV):
        with open(MEAL_PREPARATION_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'meal_name', 'date', 'quantity_prepared', 'expected_students'])

def read_csv(file_path):
    """Read a CSV file into a pandas DataFrame."""
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return pd.read_csv(file_path)
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error reading CSV file {file_path}: {e}")
        return pd.DataFrame()

def write_csv(df, file_path):
    """Write a pandas DataFrame to a CSV file."""
    try:
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        logging.error(f"Error writing to CSV file {file_path}: {e}")
        return False

def get_next_id(file_path):
    """Get the next available ID for a CSV file."""
    df = read_csv(file_path)
    if df.empty:
        return 1
    return df['id'].max() + 1 if 'id' in df.columns else 1

def get_current_date():
    """Get the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    """Get the current time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")

def get_current_meal_type():
    """Get the current meal type based on the time of day."""
    hour = datetime.now().hour
    if 0 <= hour < 11:
        return "Breakfast"
    elif 11 <= hour < 16:
        return "Lunch"
    else:
        return "Dinner"
        
def get_current_day_of_week():
    """Get the current day of the week."""
    return datetime.now().strftime("%A")
    
def get_current_day_meal():
    """Get the current day and meal type based on the time."""
    day = get_current_day_of_week()
    meal_type = get_current_meal_type()
    return day, meal_type

def get_students_count():
    """Get the total number of registered students."""
    students_df = read_csv(STUDENTS_CSV)
    return len(students_df)

def get_today_attendance_count(meal_type):
    """Get the count of students who attended a specific meal today."""
    attendance_df = read_csv(ATTENDANCE_CSV)
    if attendance_df.empty:
        return 0
    today = get_current_date()
    return len(attendance_df[(attendance_df['date'] == today) & (attendance_df['meal_type'] == meal_type)])

def format_date(date_str):
    """Format a date string from YYYY-MM-DD to a more readable format."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str
        
def get_meal_name_from_menu(day, meal_type):
    """Get the meal name from the menu based on day and meal type."""
    menu_df = read_csv(MENU_CSV)
    if menu_df.empty:
        return f"No {meal_type} menu for {day}"
    
    # Find the menu item for the given day and meal type
    menu_item = menu_df[(menu_df['day'] == day) & (menu_df['meal_type'] == meal_type)]
    
    if menu_item.empty:
        return f"No {meal_type} menu for {day}"
    
    return menu_item.iloc[0]['meal_name']
