import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from utils import read_csv
from config import ATTENDANCE_CSV, MENU_CSV, MEAL_PREPARATION_CSV, MEAL_TYPES, DAYS_OF_WEEK, MODEL_DIR

# Model file paths
ATTENDANCE_MODEL_PATH = os.path.join(MODEL_DIR, 'attendance_model.pkl')
FOOD_MODEL_PATH = os.path.join(MODEL_DIR, 'food_model.pkl')

def get_day_of_week(date_str):
    """Get the day of the week (0=Monday, 6=Sunday) from a date string."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.weekday()

def train_prediction_model():
    """Train a model to predict meal attendance based on historical data."""
    # Make sure the model directory exists
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    # Read attendance data
    attendance_df = read_csv(ATTENDANCE_CSV)
    
    if attendance_df.empty:
        return False
    
    # Count daily attendance by meal type
    attendance_counts = attendance_df.groupby(['date', 'meal_type']).size().reset_index(name='count')
    
    # Add day of week feature
    attendance_counts['day_of_week'] = attendance_counts['date'].apply(get_day_of_week)
    
    # Check if we have enough data
    if len(attendance_counts) < 14:  # Need at least 2 weeks of data
        return False
    
    # Create features and target
    features = ['day_of_week']
    X = attendance_counts[features].copy()
    
    # Convert day_of_week to one-hot encoding
    X = pd.get_dummies(X, columns=['day_of_week'], prefix='dow')
    
    # Group by day of week and meal type for training separate models
    models = {}
    
    for meal_type in MEAL_TYPES:
        # Filter data for this meal type
        meal_data = attendance_counts[attendance_counts['meal_type'] == meal_type]
        
        if len(meal_data) < 5:  # Need at least a few samples for this meal type
            continue
        
        # Get features and target for this meal type
        X_meal = X.loc[meal_data.index]
        y_meal = meal_data['count']
        
        # Train model with cross-validation if we have enough data
        if len(X_meal) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(X_meal, y_meal, test_size=0.2, random_state=42)
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Check model performance
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            print(f"MAE for {meal_type}: {mae:.2f} students")
        else:
            # Use simpler model for small datasets
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_meal, y_meal)
        
        # Store model
        models[meal_type] = model
    
    # Save models
    with open(ATTENDANCE_MODEL_PATH, 'wb') as f:
        pickle.dump(models, f)
    
    return True

def predict_meal_attendance(date_str):
    """Predict attendance for each meal type on a specific date."""
    # Load models
    if not os.path.exists(ATTENDANCE_MODEL_PATH):
        # Try to train the model if it doesn't exist
        success = train_prediction_model()
        if not success:
            return None
    
    try:
        with open(ATTENDANCE_MODEL_PATH, 'rb') as f:
            models = pickle.load(f)
    except:
        return None
    
    # Get day of week
    day_of_week = get_day_of_week(date_str)
    
    # Create feature vector
    X_pred = pd.DataFrame({
        f'dow_{day_of_week}': [1]
    })
    
    # Add missing day of week columns
    for i in range(7):
        if f'dow_{i}' not in X_pred.columns:
            X_pred[f'dow_{i}'] = 0
    
    # Sort columns to match training data
    X_pred = X_pred.reindex(sorted(X_pred.columns), axis=1)
    
    # Make predictions for each meal type
    predictions = {}
    
    for meal_type in MEAL_TYPES:
        if meal_type in models:
            model = models[meal_type]
            predicted_count = model.predict(X_pred)[0]
            predictions[meal_type] = max(0, int(round(predicted_count)))  # Ensure non-negative integer
        else:
            # Use average attendance if no model is available
            attendance_df = read_csv(ATTENDANCE_CSV)
            if not attendance_df.empty:
                # Filter for same day of week and meal type
                mask = (attendance_df['date'].apply(get_day_of_week) == day_of_week) & (attendance_df['meal_type'] == meal_type)
                avg_attendance = attendance_df[mask].groupby('date').size().mean()
                predictions[meal_type] = max(0, int(round(avg_attendance))) if not np.isnan(avg_attendance) else 0
            else:
                predictions[meal_type] = 0
    
    return predictions

def generate_meal_recommendations(date_str):
    """Generate meal preparation recommendations based on predicted attendance."""
    # Get predicted attendance
    attendance_prediction = predict_meal_attendance(date_str)
    
    if not attendance_prediction:
        return None
    
    # Get menu for the day
    menu_df = read_csv(MENU_CSV)
    
    if menu_df.empty:
        return None
    
    # Get day of week
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    day_name = DAYS_OF_WEEK[dt.weekday()]
    
    # Filter menu for the day
    day_menu = menu_df[menu_df['day'] == day_name]
    
    # Get meal preparation history
    meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
    
    # Calculate average food per student
    food_per_student = {}
    
    if not meal_prep_df.empty and 'leftover_weight' in meal_prep_df.columns:
        # Extract meal type from meal name
        def extract_meal_type(meal_name):
            if 'Break' in meal_name:
                return 'Breakfast'
            elif 'Lunch' in meal_name:
                return 'Lunch'
            elif 'Dinner' in meal_name:
                return 'Dinner'
            return None
        
        # Add meal type if not present
        if 'meal_type' not in meal_prep_df.columns:
            meal_prep_df['meal_type'] = meal_prep_df['meal_name'].apply(extract_meal_type)
        
        # Calculate actual consumption
        meal_prep_df['actual_consumption'] = meal_prep_df['quantity_prepared'] - meal_prep_df['leftover_weight']
        
        # Calculate consumption per student
        for meal_type in MEAL_TYPES:
            meal_data = meal_prep_df[meal_prep_df['meal_type'] == meal_type]
            
            if not meal_data.empty:
                # Calculate average consumption per student
                meal_data = meal_data[meal_data['expected_students'] > 0]  # Avoid division by zero
                meal_data['consumption_per_student'] = meal_data['actual_consumption'] / meal_data['expected_students']
                avg_consumption = meal_data['consumption_per_student'].mean()
                food_per_student[meal_type] = avg_consumption
    
    # Default values if no historical data is available
    if 'Breakfast' not in food_per_student: food_per_student['Breakfast'] = 0.3  # 300g per student
    if 'Lunch' not in food_per_student: food_per_student['Lunch'] = 0.5  # 500g per student
    if 'Dinner' not in food_per_student: food_per_student['Dinner'] = 0.5  # 500g per student
    
    # Generate recommendations
    recommendations = {}
    
    for meal_type in MEAL_TYPES:
        # Get menu item for this meal type
        menu_item = day_menu[day_menu['meal_type'] == meal_type]
        
        if not menu_item.empty:
            menu_name = menu_item.iloc[0]['meal_name']
            menu_description = menu_item.iloc[0]['description']
        else:
            menu_name = f"{day_name}_{meal_type}"
            menu_description = "Standard meal"
        
        # Calculate recommended quantity
        predicted_attendance = attendance_prediction.get(meal_type, 0)
        recommended_quantity = predicted_attendance * food_per_student[meal_type]
        
        # Add buffer for uncertainty (10%)
        recommended_quantity *= 1.1
        
        # Round to nearest 0.5 kg
        recommended_quantity = round(recommended_quantity * 2) / 2
        
        # Store recommendation
        recommendations[meal_type] = {
            'menu_name': menu_name,
            'menu_description': menu_description,
            'predicted_attendance': predicted_attendance,
            'recommended_quantity': recommended_quantity,
            'consumption_per_student': food_per_student[meal_type]
        }
    
    return recommendations

def extract_features_from_meal_name(meal_name):
    """Extract features from meal name (e.g., 'Mon_Lunch_2' -> 'Monday', 'Lunch')."""
    parts = meal_name.split('_')
    
    # Extract day
    day_abbr = parts[0].lower()
    day = None
    for d in DAYS_OF_WEEK:
        if d.lower().startswith(day_abbr):
            day = d
            break
    
    # Extract meal type
    meal_type = None
    if len(parts) > 1:
        meal_part = parts[1].lower()
        for mt in MEAL_TYPES:
            if mt.lower().startswith(meal_part):
                meal_type = mt
                break
    
    return day, meal_type

def train_food_prediction_model():
    """Train a model to predict food quantities based on historical data."""
    # Ensure model directory exists
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    # Read meal preparation data
    meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
    menu_df = read_csv(MENU_CSV)
    attendance_df = read_csv(ATTENDANCE_CSV)
    
    # Check if we have enough data
    if meal_prep_df.empty or len(meal_prep_df) < 14:  # Need at least 2 weeks of data
        return False
    
    # Process meal preparation data
    meal_prep_df['date'] = pd.to_datetime(meal_prep_df['date'])
    meal_prep_df['day_of_week'] = meal_prep_df['date'].dt.dayofweek
    
    # Always extract meal type from meal name to ensure it's available
    def extract_meal_type(meal_name):
        if 'Break' in meal_name:
            return 'Breakfast'
        elif 'Lunch' in meal_name:
            return 'Lunch'
        elif 'Dinner' in meal_name:
            return 'Dinner'
        return 'Unknown'
    
    # Apply the function to extract meal type
    meal_prep_df['meal_type'] = meal_prep_df['meal_name'].apply(extract_meal_type)
    
    # Extract day from the menu data if available and day column is not present
    if 'day' not in meal_prep_df.columns:
        if not menu_df.empty:
            menu_df = menu_df[['meal_name', 'day', 'meal_type']]
            meal_prep_df = pd.merge(meal_prep_df, menu_df, on='meal_name', how='left')
        else:
            # Extract from meal name if menu data is not available
            extracted = meal_prep_df['meal_name'].apply(extract_features_from_meal_name)
            meal_prep_df['day'] = extracted.apply(lambda x: x[0])
    
    # Calculate actual consumption if available
    if 'leftover_weight' in meal_prep_df.columns:
        meal_prep_df['actual_consumption'] = meal_prep_df['quantity_prepared'] - meal_prep_df['leftover_weight']
    else:
        # Estimate consumption from quantity_prepared if leftover data is not available
        meal_prep_df['actual_consumption'] = meal_prep_df['quantity_prepared']
    
    # Add attendance information if available
    if not attendance_df.empty:
        # Count daily attendance by date and meal type
        attendance_counts = attendance_df.groupby(['date', 'meal_type']).size().reset_index(name='attendance_count')
        
        # Convert date to datetime for joining
        attendance_counts['date'] = pd.to_datetime(attendance_counts['date'])
        
        # Ensure meal_type exists in meal_prep_df
        # Extract meal type if it doesn't exist
        if 'meal_type' not in meal_prep_df.columns:
            def extract_meal_type(meal_name):
                if 'Break' in meal_name:
                    return 'Breakfast'
                elif 'Lunch' in meal_name:
                    return 'Lunch'
                elif 'Dinner' in meal_name:
                    return 'Dinner'
                return 'Unknown'
            
            meal_prep_df['meal_type'] = meal_prep_df['meal_name'].apply(extract_meal_type)
            
        # Join with meal preparation data
        meal_prep_df = pd.merge(
            meal_prep_df,
            attendance_counts,
            on=['date', 'meal_type'],
            how='left'
        )
        
        # Fill missing attendance with expected students
        meal_prep_df['attendance_count'] = meal_prep_df['attendance_count'].fillna(meal_prep_df['expected_students'])
    else:
        # Use expected students as attendance if attendance data is not available
        meal_prep_df['attendance_count'] = meal_prep_df['expected_students']
    
    # Prepare feature set
    features = ['day_of_week', 'attendance_count', 'expected_students']
    X = meal_prep_df[features].copy()
    
    # Convert day_of_week to one-hot encoding
    X = pd.get_dummies(X, columns=['day_of_week'], prefix='dow')
    
    # Store feature names
    feature_names = X.columns.tolist()
    
    # Target: actual consumption
    y = meal_prep_df['actual_consumption']
    
    # Create one model for each meal type
    models = {}
    
    # Combine day and meal type to create unique key
    day_meal_combinations = []
    for day in DAYS_OF_WEEK:
        for meal_type in MEAL_TYPES:
            day_meal_combinations.append((day, meal_type))
    
    for day, meal_type in day_meal_combinations:
        # Filter data for this day and meal type
        mask = (meal_prep_df['day'] == day) & (meal_prep_df['meal_type'] == meal_type)
        meal_data = meal_prep_df[mask]
        
        if len(meal_data) < 5:  # Need at least a few samples for this meal
            continue
        
        # Get features and target for this meal
        X_meal = X.loc[meal_data.index]
        y_meal = y.loc[meal_data.index]
        
        # Train model with cross-validation if we have enough data
        if len(X_meal) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(X_meal, y_meal, test_size=0.2, random_state=42)
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Check model performance
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            print(f"MAE for {day} {meal_type}: {mae:.2f} kg")
        else:
            # Use simpler model for small datasets
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_meal, y_meal)
        
        # Store model
        models[(day, meal_type)] = model
    
    # Save models and feature names
    model_data = {
        'models': models,
        'feature_names': feature_names
    }
    with open(FOOD_MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f)
    
    return True

def predict_food_quantity_for_week():
    """Predict food quantities for all meals in the upcoming week."""
    # Initialize models as None to use fallback method if model loading fails
    models = None
    feature_names = None
    
    # Try to load models only if the file exists
    if os.path.exists(FOOD_MODEL_PATH):
        try:
            with open(FOOD_MODEL_PATH, 'rb') as f:
                model_data = pickle.load(f)
                models = model_data['models']
                feature_names = model_data['feature_names']
        except:
            # If loading fails, models will remain None and we'll use the fallback
            print("Could not load food prediction models, using fallback estimation instead")
    else:
        # Try to train the model
        success = train_food_prediction_model()
        if success:
            try:
                with open(FOOD_MODEL_PATH, 'rb') as f:
                    model_data = pickle.load(f)
                    models = model_data['models']
                    feature_names = model_data['feature_names']
            except:
                print("Could not load newly trained food prediction models, using fallback estimation instead")
    
    # Get current date
    today = datetime.now().date()
    
    # Calculate the start date (upcoming Monday)
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7  # If today is Monday, use next Monday
    
    start_date = today + timedelta(days=days_until_monday)
    
    # Get attendance data from the attendance model
    attendance_df = read_csv(ATTENDANCE_CSV)
    menu_df = read_csv(MENU_CSV)
    meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
    
    # Calculate average attendance for each day and meal type
    if not attendance_df.empty:
        # Add day of week
        attendance_df['date'] = pd.to_datetime(attendance_df['date'])
        attendance_df['day_of_week'] = attendance_df['date'].dt.dayofweek
        
        # Map day of week to day name
        day_map = {i: day for i, day in enumerate(DAYS_OF_WEEK)}
        attendance_df['day'] = attendance_df['day_of_week'].map(day_map)
        
        # Group by day and meal type
        attendance_counts = attendance_df.groupby(['day', 'meal_type']).size().reset_index(name='attendance_count')
    else:
        # Create empty DataFrame if no attendance data
        attendance_counts = pd.DataFrame(columns=['day', 'meal_type', 'attendance_count'])
    
    # Calculate average expected students for each day and meal type
    if not meal_prep_df.empty:
        meal_prep_df['date'] = pd.to_datetime(meal_prep_df['date'])
        meal_prep_df['day_of_week'] = meal_prep_df['date'].dt.dayofweek
        
        # Always extract meal type from meal name
        def extract_meal_type(meal_name):
            if 'Break' in meal_name:
                return 'Breakfast'
            elif 'Lunch' in meal_name:
                return 'Lunch'
            elif 'Dinner' in meal_name:
                return 'Dinner'
            return 'Unknown'
        
        meal_prep_df['meal_type'] = meal_prep_df['meal_name'].apply(extract_meal_type)
        
        # Extract day if needed
        if 'day' not in meal_prep_df.columns:
            if not menu_df.empty:
                menu_df = menu_df[['meal_name', 'day']]
                meal_prep_df = pd.merge(meal_prep_df, menu_df, on='meal_name', how='left')
            else:
                extracted = meal_prep_df['meal_name'].apply(extract_features_from_meal_name)
                meal_prep_df['day'] = extracted.apply(lambda x: x[0])
        
        # Group by day and meal type
        expected_students = meal_prep_df.groupby(['day', 'meal_type'])['expected_students'].mean().reset_index()
    else:
        # Create empty DataFrame if no meal prep data
        expected_students = pd.DataFrame(columns=['day', 'meal_type', 'expected_students'])
    
    # Set default values
    default_attendance = 50  # Default attendance count
    default_expected = 60    # Default expected students
    
    # Generate predictions for each day in the next week
    weekly_predictions = {}
    
    for i in range(7):  # 7 days of the week
        current_date = start_date + timedelta(days=i)
        current_day = DAYS_OF_WEEK[current_date.weekday()]
        date_str = current_date.strftime("%Y-%m-%d")
        
        day_predictions = {}
        
        for meal_type in MEAL_TYPES:
            # Get the model for this day and meal type (if models exist)
            if models is not None and (current_day, meal_type) in models:
                model = models[(current_day, meal_type)]
                
                # Get attendance for this day and meal type
                attendance_row = attendance_counts[
                    (attendance_counts['day'] == current_day) & 
                    (attendance_counts['meal_type'] == meal_type)
                ]
                attendance = attendance_row['attendance_count'].values[0] if not attendance_row.empty else default_attendance
                
                # Get expected students for this day and meal type
                expected_row = expected_students[
                    (expected_students['day'] == current_day) & 
                    (expected_students['meal_type'] == meal_type)
                ]
                expected = expected_row['expected_students'].values[0] if not expected_row.empty else default_expected
                
                # Create feature vector
                X_pred = pd.DataFrame({
                    'day_of_week': [current_date.weekday()],
                    'attendance_count': [attendance],
                    'expected_students': [expected]
                })
                
                # Convert day_of_week to one-hot encoding
                X_pred = pd.get_dummies(X_pred, columns=['day_of_week'], prefix='dow')
                
                # Ensure all feature columns are present in the correct order
                X_pred = X_pred.reindex(columns=feature_names, fill_value=0)
                
                # Make prediction
                predicted_quantity = model.predict(X_pred)[0]
                predicted_quantity = max(0, round(predicted_quantity, 2))  # Ensure non-negative and round
                
                # Get menu item description if available
                meal_description = "Standard meal"
                if not menu_df.empty:
                    # Extract meal type from menu if not present
                    if 'meal_type' not in menu_df.columns:
                        # First try to get meal type from menu name
                        def extract_meal_type(meal_name):
                            if isinstance(meal_name, str):
                                if 'Break' in meal_name:
                                    return 'Breakfast'
                                elif 'Lunch' in meal_name:
                                    return 'Lunch'
                                elif 'Dinner' in meal_name:
                                    return 'Dinner'
                            return 'Unknown'
                        
                        menu_df['meal_type'] = menu_df['meal_name'].apply(extract_meal_type)
                    
                    # Try to find matching menu item
                    try:
                        menu_item = menu_df[(menu_df['day'] == current_day) & (menu_df['meal_type'] == meal_type)]
                        if not menu_item.empty:
                            meal_description = menu_item.iloc[0]['description']
                    except KeyError:
                        # If we can't find the menu item, use default description
                        pass
                
                # Store prediction
                day_predictions[meal_type] = {
                    'predicted_quantity': predicted_quantity,
                    'expected_students': int(round(expected)),
                    'menu_description': meal_description
                }
            else:
                # Use a fallback if no model is available
                # Get expected students from historical data
                expected_row = expected_students[
                    (expected_students['day'] == current_day) & 
                    (expected_students['meal_type'] == meal_type)
                ]
                expected = expected_row['expected_students'].values[0] if not expected_row.empty else default_expected
                
                # Use average consumption per student
                avg_consumption_per_student = 0.4  # Default average consumption per student in kg
                
                if not meal_prep_df.empty and 'actual_consumption' in meal_prep_df.columns:
                    # Calculate from historical data if available
                    meal_data = meal_prep_df[
                        (meal_prep_df['day'] == current_day) & 
                        (meal_prep_df['meal_type'] == meal_type) &
                        (meal_prep_df['expected_students'] > 0)
                    ]
                    
                    if not meal_data.empty:
                        meal_data['consumption_per_student'] = meal_data['actual_consumption'] / meal_data['expected_students']
                        avg_consumption_per_student = meal_data['consumption_per_student'].mean()
                
                # Calculate predicted quantity
                predicted_quantity = max(0, round(expected * avg_consumption_per_student, 2))
                
                # Get menu item description if available
                meal_description = "Standard meal"
                if not menu_df.empty:
                    menu_item = menu_df[(menu_df['day'] == current_day) & (menu_df['meal_type'] == meal_type)]
                    if not menu_item.empty:
                        meal_description = menu_item.iloc[0]['description']
                
                # Store prediction
                day_predictions[meal_type] = {
                    'predicted_quantity': predicted_quantity,
                    'expected_students': int(round(expected)),
                    'menu_description': meal_description,
                    'note': 'Estimate based on average consumption (no model available)'
                }
        
        # Add predictions for this day
        weekly_predictions[date_str] = {
            'day': current_day,
            'meals': day_predictions
        }
    
    return weekly_predictions
