import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from utils import read_csv, get_students_count, get_today_attendance_count, format_date
from config import STUDENTS_CSV, ATTENDANCE_CSV, MENU_CSV, MEAL_PREPARATION_CSV, MEAL_TYPES, DAYS_OF_WEEK
from auth import login_required
from prediction import predict_meal_attendance, train_prediction_model, train_food_prediction_model, predict_food_quantity_for_week

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """Display the main dashboard."""
    # Get basic metrics
    total_students = get_students_count()
    breakfast_count = get_today_attendance_count('Breakfast')
    lunch_count = get_today_attendance_count('Lunch')
    dinner_count = get_today_attendance_count('Dinner')
    
    # Get current date in a readable format
    today = format_date(datetime.now().strftime("%Y-%m-%d"))
    
    # Check if there are any predictions available
    predictions_available = False
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    attendance_prediction = predict_meal_attendance(tomorrow)
    if attendance_prediction and any(attendance_prediction.values()):
        predictions_available = True
    
    return render_template('dashboard.html',
                          total_students=total_students,
                          breakfast_count=breakfast_count,
                          lunch_count=lunch_count,
                          dinner_count=dinner_count,
                          today=today,
                          predictions_available=predictions_available)

@analytics_bp.route('/analytics')
@login_required
def analytics():
    """Display the analytics page."""
    # Read data from CSV files
    students_df = read_csv(STUDENTS_CSV)
    attendance_df = read_csv(ATTENDANCE_CSV)
    menu_df = read_csv(MENU_CSV)
    meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
    
    # Check if data is available
    data_available = not (students_df.empty or attendance_df.empty)
    
    # Calculate total wastage statistics
    wastage_stats = {}
    if not (attendance_df.empty or meal_prep_df.empty):
        # First, extract meal_type from meal_name in meal_prep_df
        def extract_meal_type(meal_name):
            if 'Break' in meal_name:
                return 'Breakfast'
            elif 'Lunch' in meal_name:
                return 'Lunch'
            elif 'Dinner' in meal_name:
                return 'Dinner'
            return 'Unknown'
        
        meal_prep_df['meal_type'] = meal_prep_df['meal_name'].apply(extract_meal_type)
        
        # Now merge attendance with meal preparation data
        merged_data = pd.merge(
            attendance_df,
            meal_prep_df,
            left_on=['date', 'meal_type'],
            right_on=['date', 'meal_type'],
            how='inner'
        )
        
        if not merged_data.empty:
            # Calculate total wastage per meal
            wastage_by_meal = merged_data.groupby(['date', 'meal_type']).agg({
                'leftover_weight': 'sum',
                'quantity_prepared': 'first',
                'expected_students': 'first'
            }).reset_index()
            
            wastage_by_meal['wastage_percentage'] = (wastage_by_meal['leftover_weight'] / 
                                                    wastage_by_meal['quantity_prepared'] * 100)
            
            # Total wastage
            total_wastage = wastage_by_meal['leftover_weight'].sum()
            total_prepared = wastage_by_meal['quantity_prepared'].sum()
            wastage_percentage = (total_wastage / total_prepared * 100) if total_prepared > 0 else 0
            
            wastage_stats = {
                'total_wastage': f"{total_wastage:.2f} kg",
                'total_prepared': f"{total_prepared:.2f} kg",
                'wastage_percentage': f"{wastage_percentage:.2f}%",
                'wastage_by_meal': wastage_by_meal.to_dict('records')
            }
    
    # Student wastage statistics
    student_wastage = []
    if not (attendance_df.empty or students_df.empty):
        # Merge attendance with student data
        student_data = pd.merge(
            attendance_df,
            students_df,
            left_on='student_id',
            right_on='id',
            how='inner'
        )
        
        if not student_data.empty:
            # Calculate total wastage per student
            student_wastage_data = student_data.groupby(['student_id', 'name', 'roll_number']).agg({
                'leftover_weight': 'sum'
            }).reset_index()
            
            # Sort by wastage (highest first)
            student_wastage_data = student_wastage_data.sort_values('leftover_weight', ascending=False)
            
            student_wastage = student_wastage_data.head(10).to_dict('records')
    
    # Calculate meal type wastage for pie chart
    meal_type_wastage = []
    if not attendance_df.empty:
        meal_wastage = attendance_df.groupby('meal_type').agg({
            'leftover_weight': 'sum'
        }).reset_index()
        
        meal_type_wastage = meal_wastage.to_dict('records')
    
    # Historical wastage data for line chart (last 30 days)
    dates = []
    wastage_values = []
    
    if not attendance_df.empty:
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Filter data within date range
        date_range = [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(31)
        ]
        
        # Calculate daily wastage
        for date in date_range:
            daily_wastage = attendance_df[attendance_df['date'] == date]['leftover_weight'].sum()
            dates.append(date)
            wastage_values.append(float(daily_wastage))
    
    # Tomorrow's predictions
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    attendance_prediction = predict_meal_attendance(tomorrow)
    
    return render_template('analytics.html',
                          data_available=data_available,
                          wastage_stats=wastage_stats,
                          student_wastage=student_wastage,
                          meal_type_wastage=meal_type_wastage,
                          dates=json.dumps(dates),
                          wastage_values=json.dumps(wastage_values),
                          attendance_prediction=attendance_prediction)

@analytics_bp.route('/generate_predictions', methods=['POST'])
@login_required
def generate_predictions():
    """Generate predictions for future meal attendance."""
    # Train the prediction model
    train_result = train_prediction_model()
    
    if train_result:
        flash('Predictions generated successfully', 'success')
    else:
        flash('Insufficient data to generate predictions', 'warning')
    
    return redirect(url_for('analytics.dashboard'))

@analytics_bp.route('/api/food_waste_data')
@login_required
def food_waste_data():
    """API endpoint for food waste data."""
    attendance_df = read_csv(ATTENDANCE_CSV)
    
    if attendance_df.empty:
        return jsonify({
            'dates': [],
            'values': []
        })
    
    # Get all unique dates from attendance data
    attendance_dates = attendance_df['date'].unique()
    
    # Sort dates to get the most recent ones
    attendance_dates.sort()
    
    # Get the last 7 days of data (or all if less than 7)
    dates_to_show = attendance_dates[-7:] if len(attendance_dates) >= 7 else attendance_dates
    
    # Calculate daily wastage
    dates = []
    values = []
    
    for date in dates_to_show:
        daily_wastage = attendance_df[attendance_df['date'] == date]['leftover_weight'].sum()
        dates.append(date)
        values.append(float(daily_wastage))
        
    # Format dates for display
    formatted_dates = [format_date(date) for date in dates]
    
    return jsonify({
        'dates': dates,
        'formatted_dates': formatted_dates,
        'values': values
    })

@analytics_bp.route('/api/todays_waste_analysis')
@login_required
def todays_waste_analysis():
    """API endpoint for today's waste analysis."""
    attendance_df = read_csv(ATTENDANCE_CSV)
    meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if attendance_df.empty or meal_prep_df.empty:
        return jsonify({
            'available': False,
            'message': 'No waste data available for today'
        })
    
    # Today's attendance with leftover weights
    today_attendance = attendance_df[attendance_df['date'] == today]
    
    if today_attendance.empty:
        return jsonify({
            'available': False,
            'message': 'No waste data available for today'
        })
    
    # Calculate waste by meal type
    waste_by_meal = today_attendance.groupby('meal_type').agg({
        'leftover_weight': 'sum'
    }).reset_index()
    
    # Merge with meal preparation if available
    today_prep = meal_prep_df[meal_prep_df['date'] == today]
    
    if not today_prep.empty:
        # Extract meal_type from meal_name
        def extract_meal_type(meal_name):
            if 'Break' in meal_name:
                return 'Breakfast'
            elif 'Lunch' in meal_name:
                return 'Lunch'
            elif 'Dinner' in meal_name:
                return 'Dinner'
            return 'Unknown'
        
        today_prep['meal_type'] = today_prep['meal_name'].apply(extract_meal_type)
        
        # Now merge
        merged_data = pd.merge(
            waste_by_meal,
            today_prep,
            on='meal_type',
            how='left'
        )
        
        if not merged_data.empty and 'quantity_prepared' in merged_data.columns:
            # Ensure we're using the right leftover_weight column
            if 'leftover_weight_x' in merged_data.columns and 'leftover_weight_y' in merged_data.columns:
                # We have duplicate column names, use the first one (from waste_by_meal)
                merged_data['wastage_percentage'] = (merged_data['leftover_weight_x'] / 
                                                  merged_data['quantity_prepared'] * 100)
                waste_by_meal = merged_data[['meal_type', 'leftover_weight_x', 'quantity_prepared', 'wastage_percentage']]
                waste_by_meal = waste_by_meal.rename(columns={'leftover_weight_x': 'leftover_weight'})
            elif 'leftover_weight' in merged_data.columns:
                # Direct use of leftover_weight if not duplicated
                merged_data['wastage_percentage'] = (merged_data['leftover_weight'] / 
                                                  merged_data['quantity_prepared'] * 100)
                waste_by_meal = merged_data[['meal_type', 'leftover_weight', 'quantity_prepared', 'wastage_percentage']]
    
    return jsonify({
        'available': True,
        'waste_by_meal': waste_by_meal.to_dict('records'),
        'total_waste': today_attendance['leftover_weight'].sum()
    })

@analytics_bp.route('/weekly_food_predictions')
@login_required
def weekly_food_predictions():
    """Display food quantity predictions for the upcoming week."""
    # Check if there's an existing model, if not, train one
    week_predictions = predict_food_quantity_for_week()
    
    if not week_predictions:
        # Try to train the model
        train_success = train_food_prediction_model()
        if train_success:
            week_predictions = predict_food_quantity_for_week()
            if not week_predictions:
                flash('Could not generate predictions. Not enough historical data available.', 'warning')
        else:
            flash('Could not train the prediction model. Please ensure you have sufficient historical data.', 'warning')
    
    # Organize data by day for better display
    days_data = {}
    
    if week_predictions:
        for date, data in week_predictions.items():
            day = data['day']
            
            if day not in days_data:
                days_data[day] = {
                    'date': format_date(date),
                    'meals': data['meals']
                }
    
    return render_template('weekly_predictions.html',
                         predictions_available=bool(week_predictions),
                         days_data=days_data,
                         meal_types=MEAL_TYPES,
                         days_of_week=DAYS_OF_WEEK)

@analytics_bp.route('/generate_food_predictions', methods=['POST'])
@login_required
def generate_food_predictions():
    """Generate predictions for food quantities."""
    # Train the food prediction model
    train_result = train_food_prediction_model()
    
    if train_result:
        flash('Food quantity predictions generated successfully', 'success')
    else:
        flash('Insufficient data to generate food quantity predictions', 'warning')
    
    return redirect(url_for('analytics.weekly_food_predictions'))

@analytics_bp.route('/analysis_dashboard')
@login_required
def analysis_dashboard():
    """Display comprehensive analytics dashboard with charts and insights."""
    # Read data from CSV files
    students_df = read_csv(STUDENTS_CSV)
    attendance_df = read_csv(ATTENDANCE_CSV)
    menu_df = read_csv(MENU_CSV)
    meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
    
    # Check if data is available
    data_available = not (students_df.empty or attendance_df.empty or meal_prep_df.empty)
    
    if not data_available:
        flash('Insufficient data for analytics dashboard. Please record student attendance and meal preparation data.', 'warning')
        return render_template('analysis_dashboard.html', data_available=False)
    
    # Process data for different sections
    attendance_data = process_attendance_data(attendance_df)
    consumption_data = process_consumption_data(meal_prep_df)
    prediction_data = process_prediction_data(meal_prep_df, attendance_df)
    
    # Return all data for rendering in template
    return render_template('analysis_dashboard.html',
                         data_available=data_available,
                         attendance_data=json.dumps(attendance_data),
                         consumption_data=json.dumps(consumption_data),
                         prediction_data=json.dumps(prediction_data),
                         meal_types=MEAL_TYPES)

def process_attendance_data(attendance_df):
    """Process attendance data for charts and analysis."""
    attendance_data = {}
    
    if not attendance_df.empty:
        # Convert date to datetime
        attendance_df['date'] = pd.to_datetime(attendance_df['date'])
        
        # Add day of week
        attendance_df['day_of_week'] = attendance_df['date'].dt.dayofweek
        attendance_df['day_name'] = attendance_df['day_of_week'].apply(lambda x: DAYS_OF_WEEK[x])
        
        # Get last 30 days data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        recent_attendance = attendance_df[attendance_df['date'] >= start_date]
        
        if not recent_attendance.empty:
            # Process daily attendance by meal type
            daily_attendance = process_daily_attendance(recent_attendance)
            attendance_data.update(daily_attendance)
            
            # Process average attendance by day of week
            avg_by_day = process_avg_attendance_by_day(recent_attendance)
            attendance_data.update(avg_by_day)
    
    return attendance_data

def process_daily_attendance(recent_attendance):
    """Process daily attendance data for line chart."""
    daily_attendance = recent_attendance.groupby(['date', 'meal_type']).size().reset_index(name='count')
    attendance_pivot = daily_attendance.pivot(index='date', columns='meal_type', values='count').reset_index()
    attendance_pivot = attendance_pivot.fillna(0)
    
    return {
        'dates': attendance_pivot['date'].dt.strftime('%Y-%m-%d').tolist(),
        'breakfast': attendance_pivot['Breakfast'].tolist() if 'Breakfast' in attendance_pivot else [],
        'lunch': attendance_pivot['Lunch'].tolist() if 'Lunch' in attendance_pivot else [],
        'dinner': attendance_pivot['Dinner'].tolist() if 'Dinner' in attendance_pivot else []
    }

def process_avg_attendance_by_day(recent_attendance):
    """Process average attendance by day of week for bar chart."""
    avg_by_day = recent_attendance.groupby(['day_name', 'meal_type']).size().reset_index(name='count')
    avg_by_day_pivot = avg_by_day.pivot(index='day_name', columns='meal_type', values='count').reset_index()
    avg_by_day_pivot = avg_by_day_pivot.fillna(0)
    
    # Reorder days correctly
    day_order = {day: i for i, day in enumerate(DAYS_OF_WEEK)}
    avg_by_day_pivot['day_order'] = avg_by_day_pivot['day_name'].map(day_order)
    avg_by_day_pivot = avg_by_day_pivot.sort_values('day_order')
    
    return {
        'days': avg_by_day_pivot['day_name'].tolist(),
        'avg_breakfast': avg_by_day_pivot['Breakfast'].tolist() if 'Breakfast' in avg_by_day_pivot else [],
        'avg_lunch': avg_by_day_pivot['Lunch'].tolist() if 'Lunch' in avg_by_day_pivot else [],
        'avg_dinner': avg_by_day_pivot['Dinner'].tolist() if 'Dinner' in avg_by_day_pivot else []
    }

def process_consumption_data(meal_prep_df):
    """Process meal preparation and consumption data for charts."""
    consumption_data = {}
    
    if not meal_prep_df.empty:
        # Convert date to datetime
        meal_prep_df['date'] = pd.to_datetime(meal_prep_df['date'])
        
        # Add day of week
        meal_prep_df['day_of_week'] = meal_prep_df['date'].dt.dayofweek
        meal_prep_df['day_name'] = meal_prep_df['day_of_week'].apply(lambda x: DAYS_OF_WEEK[x])
        
        # Calculate actual consumption
        if 'leftover_weight' in meal_prep_df.columns:
            meal_prep_df['consumed'] = meal_prep_df['quantity_prepared'] - meal_prep_df['leftover_weight']
            meal_prep_df['meal_type'] = meal_prep_df['meal_name'].apply(extract_meal_type)
            
            # Get last 30 days data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            recent_prep = meal_prep_df[meal_prep_df['date'] >= start_date]
            
            if not recent_prep.empty:
                # Process daily consumption
                daily_consumption = process_daily_consumption(recent_prep)
                consumption_data.update(daily_consumption)
                
                # Process meal type consumption
                meal_type_consumption = process_meal_type_consumption(recent_prep)
                consumption_data.update(meal_type_consumption)
                
                # Process consumption heatmap
                heatmap_data = process_consumption_heatmap(recent_prep)
                consumption_data.update(heatmap_data)
    
    return consumption_data

def process_daily_consumption(recent_prep):
    """Process daily consumption data for line chart."""
    daily_prep = recent_prep.groupby('date').agg({
        'quantity_prepared': 'sum',
        'consumed': 'sum',
        'leftover_weight': 'sum'
    }).reset_index()
    
    return {
        'dates': daily_prep['date'].dt.strftime('%Y-%m-%d').tolist(),
        'prepared': daily_prep['quantity_prepared'].tolist(),
        'consumed': daily_prep['consumed'].tolist(),
        'leftover': daily_prep['leftover_weight'].tolist()
    }

def process_meal_type_consumption(recent_prep):
    """Process meal type consumption data for bar chart."""
    meal_type_consumption = recent_prep.groupby('meal_type').agg({
        'quantity_prepared': 'sum',
        'consumed': 'sum',
        'leftover_weight': 'sum'
    }).reset_index()
    
    total_prepared = meal_type_consumption['quantity_prepared'].sum()
    total_consumed = meal_type_consumption['consumed'].sum()
    total_leftover = meal_type_consumption['leftover_weight'].sum()
    
    return {
        'meal_types': meal_type_consumption['meal_type'].tolist(),
        'meal_prepared': meal_type_consumption['quantity_prepared'].tolist(),
        'meal_consumed': meal_type_consumption['consumed'].tolist(),
        'meal_leftover': meal_type_consumption['leftover_weight'].tolist(),
        'total_prepared': total_prepared,
        'total_consumed': total_consumed,
        'total_leftover': total_leftover,
        'consumption_rate': (total_consumed / total_prepared * 100) if total_prepared > 0 else 0
    }

def process_consumption_heatmap(recent_prep):
    """Process consumption data for heatmap visualization."""
    day_consumption = recent_prep.groupby(['day_name', 'meal_type']).agg({
        'consumed': 'mean',
        'quantity_prepared': 'mean',
        'leftover_weight': 'mean'
    }).reset_index()
    
    day_consumption['efficiency'] = (day_consumption['consumed'] / day_consumption['quantity_prepared'] * 100)
    day_consumption = day_consumption.fillna(0)
    
    efficiency_pivot = day_consumption.pivot(index='day_name', columns='meal_type', values='efficiency')
    
    # Reorder days correctly
    day_order = {day: i for i, day in enumerate(DAYS_OF_WEEK)}
    efficiency_pivot = efficiency_pivot.reset_index()
    efficiency_pivot['day_order'] = efficiency_pivot['day_name'].map(day_order)
    efficiency_pivot = efficiency_pivot.sort_values('day_order')
    efficiency_pivot = efficiency_pivot.drop('day_order', axis=1)
    efficiency_pivot = efficiency_pivot.set_index('day_name')
    
    # Convert to list of lists for heatmap
    heatmap_data = []
    for day in efficiency_pivot.index:
        row_data = []
        for meal in MEAL_TYPES:
            if meal in efficiency_pivot.columns:
                row_data.append(round(efficiency_pivot.loc[day, meal], 1))
            else:
                row_data.append(0)
        heatmap_data.append(row_data)
    
    return {
        'heatmap_days': efficiency_pivot.index.tolist(),
        'heatmap_data': heatmap_data
    }

def process_prediction_data(meal_prep_df, attendance_df):
    """Process prediction and trend data for charts."""
    prediction_data = {}
    
    if not meal_prep_df.empty and 'expected_students' in meal_prep_df.columns:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        recent_prep = meal_prep_df[meal_prep_df['date'] >= start_date]
        
        if not recent_prep.empty and 'leftover_weight' in recent_prep.columns:
            # Calculate actual and predicted consumption
            recent_prep['consumed'] = recent_prep['quantity_prepared'] - recent_prep['leftover_weight']
            recent_prep['consumption_per_student'] = recent_prep['consumed'] / recent_prep['expected_students']
            recent_prep = recent_prep.replace([np.inf, -np.inf], np.nan).dropna(subset=['consumption_per_student'])
            
            recent_prep['predicted_consumption'] = recent_prep['expected_students'] * recent_prep['consumption_per_student'].mean()
            
            # Prepare data for scatter plot
            prediction_data['actual'] = recent_prep['consumed'].tolist()
            prediction_data['predicted'] = recent_prep['predicted_consumption'].tolist()
            
            # Prepare data for time series comparison
            recent_prep = recent_prep.sort_values('date')
            prediction_data['dates'] = recent_prep['date'].dt.strftime('%Y-%m-%d').tolist()
            prediction_data['actual_ts'] = recent_prep['consumed'].tolist()
            prediction_data['predicted_ts'] = recent_prep['predicted_consumption'].tolist()
            
            # Process consumption rate distribution
            consumption_rates = recent_prep['consumption_per_student'].tolist()
            min_rate = min(consumption_rates)
            max_rate = max(consumption_rates)
            bins = np.linspace(min_rate, max_rate, 10)
            hist, bin_edges = np.histogram(consumption_rates, bins=bins)
            
            prediction_data['consumption_rate_bins'] = [f"{round(bin_edges[i], 2)}-{round(bin_edges[i+1], 2)}" for i in range(len(bin_edges)-1)]
            prediction_data['consumption_rate_counts'] = hist.tolist()
            
            # Process weekly attendance trends
            if not attendance_df.empty:
                attendance_df['week'] = attendance_df['date'].dt.isocalendar().week
                weekly_attendance = attendance_df.groupby('week').size().reset_index(name='count')
                
                prediction_data['weeks'] = weekly_attendance['week'].tolist()
                prediction_data['weekly_counts'] = weekly_attendance['count'].tolist()
    
    return prediction_data

def extract_meal_type(meal_name):
    """Extract meal type from meal name."""
    if 'Break' in meal_name:
        return 'Breakfast'
    elif 'Lunch' in meal_name:
        return 'Lunch'
    elif 'Dinner' in meal_name:
        return 'Dinner'
    return 'Unknown'
