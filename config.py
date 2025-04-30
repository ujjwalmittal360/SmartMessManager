import os

# File paths
DATA_DIR = 'data'
STUDENT_IMAGES_DIR = 'static/student_images'
MODEL_DIR = 'data/models'

# CSV file paths
USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
STUDENTS_CSV = os.path.join(DATA_DIR, 'students.csv')
ATTENDANCE_CSV = os.path.join(DATA_DIR, 'attendance.csv')
MENU_CSV = os.path.join(DATA_DIR, 'menu.csv')
MEAL_PREPARATION_CSV = os.path.join(DATA_DIR, 'meal_preparation.csv')

# OpenCV face detection parameters
FACE_DETECTION_CONFIDENCE = 0.5
FACE_RECOGNITION_THRESHOLD = 0.6

# Meal types
MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner']

# Days of the week
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Application settings
DEBUG = True
