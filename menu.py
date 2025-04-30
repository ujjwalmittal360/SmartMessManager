import pandas as pd
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from utils import read_csv, write_csv, get_next_id, get_current_date, get_today_attendance_count, get_current_day_of_week, get_current_meal_type
from config import MENU_CSV, DAYS_OF_WEEK, MEAL_TYPES, ATTENDANCE_CSV
from auth import login_required, admin_required

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu', methods=['GET', 'POST'])
@login_required
def view_menu():
    """View and manage the weekly menu."""
    menu_df = read_csv(MENU_CSV)
    days = DAYS_OF_WEEK
    meal_types = MEAL_TYPES
    
    # Organize menu by day and meal type
    menu_by_day = {}
    for day in days:
        menu_by_day[day] = {}
        for meal_type in meal_types:
            menu_by_day[day][meal_type] = None
    
    if not menu_df.empty:
        for _, row in menu_df.iterrows():
            day = row.get('day')
            meal_type = row.get('meal_type')
            if day in menu_by_day and meal_type in menu_by_day[day]:
                menu_by_day[day][meal_type] = {
                    'id': row.get('id'),
                    'meal_name': row.get('meal_name'),
                    'description': row.get('description')
                }
    
    return render_template('menu.html', 
                          menu_by_day=menu_by_day, 
                          days=days, 
                          meal_types=meal_types)

@menu_bp.route('/menu/add', methods=['GET', 'POST'])
@admin_required
def add_menu_item():
    """Add a new menu item."""
    days = DAYS_OF_WEEK
    meal_types = MEAL_TYPES
    
    if request.method == 'POST':
        day = request.form.get('day')
        meal_type = request.form.get('meal_type')
        description = request.form.get('description')
        
        if not day or not meal_type or not description:
            flash('Please fill in all fields', 'danger')
            return render_template('menu_add.html', days=days, meal_types=meal_types)
        
        # Generate meal_name (e.g., Mon_Breakfast_1)
        meal_name = f"{day[:3]}_{meal_type[:5]}_{get_next_id(MENU_CSV)}"
        
        # Read existing menu
        menu_df = read_csv(MENU_CSV)
        
        # Check if a menu item already exists for this day and meal type
        if not menu_df.empty:
            existing_item = menu_df[(menu_df['day'] == day) & (menu_df['meal_type'] == meal_type)]
            if not existing_item.empty:
                flash(f'A menu item already exists for {day} {meal_type}. Edit or delete it first.', 'danger')
                return render_template('menu_add.html', days=days, meal_types=meal_types)
        
        # Create new menu item
        new_menu_item = {
            'id': get_next_id(MENU_CSV),
            'day': day,
            'meal_type': meal_type,
            'meal_name': meal_name,
            'description': description
        }
        
        # Add to dataframe
        if menu_df.empty:
            menu_df = pd.DataFrame([new_menu_item])
        else:
            menu_df = pd.concat([menu_df, pd.DataFrame([new_menu_item])], ignore_index=True)
        
        # Save to CSV
        if write_csv(menu_df, MENU_CSV):
            flash(f'Menu item for {day} {meal_type} added successfully', 'success')
            return redirect(url_for('menu.view_menu'))
        else:
            flash('Error adding menu item', 'danger')
    
    return render_template('menu_add.html', days=days, meal_types=meal_types)

@menu_bp.route('/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
@admin_required
def edit_menu_item(menu_id):
    """Edit an existing menu item."""
    menu_df = read_csv(MENU_CSV)
    days = DAYS_OF_WEEK
    meal_types = MEAL_TYPES
    
    if menu_df.empty:
        flash('No menu items found', 'danger')
        return redirect(url_for('menu.view_menu'))
    
    # Find the menu item
    menu_item = menu_df[menu_df['id'] == menu_id]
    
    if menu_item.empty:
        flash('Menu item not found', 'danger')
        return redirect(url_for('menu.view_menu'))
    
    menu_item = menu_item.iloc[0]
    
    if request.method == 'POST':
        day = request.form.get('day')
        meal_type = request.form.get('meal_type')
        description = request.form.get('description')
        
        if not day or not meal_type or not description:
            flash('Please fill in all fields', 'danger')
            return render_template('menu_edit.html', menu_item=menu_item, days=days, meal_types=meal_types)
        
        # Check if a different menu item already exists for this day and meal type
        if not menu_df.empty:
            existing_item = menu_df[(menu_df['day'] == day) & 
                                    (menu_df['meal_type'] == meal_type) & 
                                    (menu_df['id'] != menu_id)]
            if not existing_item.empty:
                flash(f'Another menu item already exists for {day} {meal_type}', 'danger')
                return render_template('menu_edit.html', menu_item=menu_item, days=days, meal_types=meal_types)
        
        # Update menu item
        menu_df.loc[menu_df['id'] == menu_id, 'day'] = day
        menu_df.loc[menu_df['id'] == menu_id, 'meal_type'] = meal_type
        menu_df.loc[menu_df['id'] == menu_id, 'description'] = description
        
        # Only update meal_name if day or meal_type changed
        if day != menu_item['day'] or meal_type != menu_item['meal_type']:
            meal_name = f"{day[:3]}_{meal_type[:5]}_{menu_id}"
            menu_df.loc[menu_df['id'] == menu_id, 'meal_name'] = meal_name
        
        # Save to CSV
        if write_csv(menu_df, MENU_CSV):
            flash('Menu item updated successfully', 'success')
            return redirect(url_for('menu.view_menu'))
        else:
            flash('Error updating menu item', 'danger')
    
    return render_template('menu_edit.html', 
                          menu_item=menu_item.to_dict(), 
                          days=days, 
                          meal_types=meal_types)

@menu_bp.route('/menu/delete/<int:menu_id>', methods=['POST'])
@admin_required
def delete_menu_item(menu_id):
    """Delete a menu item."""
    menu_df = read_csv(MENU_CSV)
    
    if menu_df.empty:
        flash('No menu items found', 'danger')
        return redirect(url_for('menu.view_menu'))
    
    # Remove the menu item
    menu_df = menu_df[menu_df['id'] != menu_id]
    
    # Save the updated dataframe
    if write_csv(menu_df, MENU_CSV):
        flash('Menu item deleted successfully', 'success')
    else:
        flash('Error deleting menu item', 'danger')
    
    return redirect(url_for('menu.view_menu'))

@menu_bp.route('/meal_preparation', methods=['GET', 'POST'])
@login_required
def meal_preparation():
    """Record meal preparation data."""
    menu_df = read_csv(MENU_CSV)
    
    if menu_df.empty:
        flash('No menu items available. Please add menu items first.', 'danger')
        return redirect(url_for('menu.view_menu'))
    
    # Get all meal names for dropdown
    meal_options = menu_df[['meal_name', 'day', 'meal_type', 'description']].to_dict('records')
    
    # Get current day and meal type
    current_day = get_current_day_of_week()
    current_meal_type = get_current_meal_type()
    
    # Find the current meal in the menu options
    current_meal = None
    for meal in meal_options:
        if meal['day'] == current_day and meal['meal_type'] == current_meal_type:
            current_meal = meal
            break
    
    # Get the current date
    today = get_current_date()
    
    # Get the actual attendance count for today and the current meal type
    actual_attendance = get_today_attendance_count(current_meal_type)
    
    if request.method == 'POST':
        meal_name = request.form.get('meal_name')
        quantity_prepared = request.form.get('quantity_prepared')
        expected_students = request.form.get('expected_students')
        date = request.form.get('date')
        leftover_weight = request.form.get('leftover_weight', '0')
        
        if not meal_name or not quantity_prepared or not expected_students or not date:
            flash('Please fill in all fields', 'danger')
            return render_template('meal_preparation.html', 
                                 meal_options=meal_options, 
                                 current_meal=current_meal,
                                 today=today,
                                 actual_attendance=actual_attendance)
        
        try:
            quantity_prepared = float(quantity_prepared)
            expected_students = int(expected_students)
            leftover_weight = float(leftover_weight)
            
            if quantity_prepared <= 0:
                flash('Quantity prepared must be greater than zero', 'danger')
                return render_template('meal_preparation.html', 
                                     meal_options=meal_options, 
                                     current_meal=current_meal,
                                     today=today,
                                     actual_attendance=actual_attendance)
            
            if expected_students <= 0:
                flash('Expected students must be greater than zero', 'danger')
                return render_template('meal_preparation.html', 
                                     meal_options=meal_options, 
                                     current_meal=current_meal,
                                     today=today,
                                     actual_attendance=actual_attendance)
                
            # Calculate consumption (prepared - leftover)
            consumption = quantity_prepared - leftover_weight
            if consumption < 0:
                flash('Warning: Calculated consumption is negative. Please check your numbers.', 'warning')
                consumption = 0
                
        except ValueError:
            flash('Invalid quantity values', 'danger')
            return render_template('meal_preparation.html', 
                                 meal_options=meal_options, 
                                 current_meal=current_meal,
                                 today=today,
                                 actual_attendance=actual_attendance)
        
        # Read meal preparation data
        from config import MEAL_PREPARATION_CSV
        meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
        
        # Check if data already exists for this meal and date
        if not meal_prep_df.empty:
            existing_data = meal_prep_df[(meal_prep_df['meal_name'] == meal_name) & (meal_prep_df['date'] == date)]
            
            if not existing_data.empty:
                # Update existing record
                meal_prep_df.loc[(meal_prep_df['meal_name'] == meal_name) & (meal_prep_df['date'] == date), 
                                'quantity_prepared'] = quantity_prepared
                meal_prep_df.loc[(meal_prep_df['meal_name'] == meal_name) & (meal_prep_df['date'] == date), 
                                'expected_students'] = expected_students
                meal_prep_df.loc[(meal_prep_df['meal_name'] == meal_name) & (meal_prep_df['date'] == date), 
                                'leftover_weight'] = leftover_weight
                meal_prep_df.loc[(meal_prep_df['meal_name'] == meal_name) & (meal_prep_df['date'] == date), 
                                'actual_consumption'] = consumption
                meal_prep_df.loc[(meal_prep_df['meal_name'] == meal_name) & (meal_prep_df['date'] == date), 
                                'actual_attendance'] = actual_attendance
                
                if write_csv(meal_prep_df, MEAL_PREPARATION_CSV):
                    flash('Meal preparation data updated successfully', 'success')
                else:
                    flash('Error updating meal preparation data', 'danger')
                
                return redirect(url_for('menu.meal_preparation_history'))
        
        # Create new meal preparation record
        new_meal_prep = {
            'id': get_next_id(MEAL_PREPARATION_CSV),
            'meal_name': meal_name,
            'date': date,
            'quantity_prepared': quantity_prepared,
            'expected_students': expected_students,
            'leftover_weight': leftover_weight,
            'actual_consumption': consumption,
            'actual_attendance': actual_attendance
        }
        
        # Add to dataframe
        if meal_prep_df.empty:
            meal_prep_df = pd.DataFrame([new_meal_prep])
        else:
            meal_prep_df = pd.concat([meal_prep_df, pd.DataFrame([new_meal_prep])], ignore_index=True)
        
        # Save to CSV
        if write_csv(meal_prep_df, MEAL_PREPARATION_CSV):
            flash('Meal preparation data recorded successfully', 'success')
            return redirect(url_for('menu.meal_preparation_history'))
        else:
            flash('Error recording meal preparation data', 'danger')
    
    return render_template('meal_preparation.html', 
                         meal_options=meal_options, 
                         current_meal=current_meal,
                         today=today,
                         actual_attendance=actual_attendance)

@menu_bp.route('/meal_preparation/history')
@login_required
def meal_preparation_history():
    """View meal preparation history."""
    from config import MEAL_PREPARATION_CSV, ATTENDANCE_CSV
    meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
    attendance_df = read_csv(ATTENDANCE_CSV)
    menu_df = read_csv(MENU_CSV)
    
    if meal_prep_df.empty:
        return render_template('meal_preparation_history.html', meal_preps=[])
    
    # Extract meal type from meal name if not present
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
    
    # Convert date columns to datetime for proper merging
    meal_prep_df['date'] = pd.to_datetime(meal_prep_df['date'])
    if not attendance_df.empty:
        attendance_df['date'] = pd.to_datetime(attendance_df['date'])
    
    # Calculate actual attendance and leftover food from attendance data
    if not attendance_df.empty:
        # Group attendance by date and meal type
        attendance_stats = attendance_df.groupby(['date', 'meal_type']).agg({
            'student_id': 'count',
            'leftover_weight': 'sum'
        }).reset_index()
        attendance_stats = attendance_stats.rename(columns={
            'student_id': 'actual_attendance',
            'leftover_weight': 'total_leftover'
        })
        
        # Merge with meal preparation data
        meal_prep_df = pd.merge(
            meal_prep_df,
            attendance_stats,
            on=['date', 'meal_type'],
            how='left'
        )
        
        # Fill missing values with zeros
        meal_prep_df['actual_attendance'] = meal_prep_df['actual_attendance'].fillna(0)
        meal_prep_df['total_leftover'] = meal_prep_df['total_leftover'].fillna(0)
    else:
        # Add empty columns if no attendance data
        meal_prep_df['actual_attendance'] = 0
        meal_prep_df['total_leftover'] = 0
    
    # Merge with menu information
    if not menu_df.empty:
        merged_df = pd.merge(
            meal_prep_df,
            menu_df[['meal_name', 'day', 'meal_type', 'description']],
            on=['meal_name', 'meal_type'],
            how='left'
        )
    else:
        merged_df = meal_prep_df
        merged_df['day'] = ''
        merged_df['description'] = ''
    
    # Sort by date (newest first)
    merged_df = merged_df.sort_values('date', ascending=False)
    
    # Convert date back to string for template
    merged_df['date'] = merged_df['date'].dt.strftime('%Y-%m-%d')
    
    # Calculate total statistics
    total_prepared = merged_df['quantity_prepared'].sum()
    total_leftover = merged_df['total_leftover'].sum()
    total_actual = merged_df['actual_attendance'].sum()
    total_expected = merged_df['expected_students'].sum()
    
    # Add statistics to the template context
    meal_preps = merged_df.to_dict('records')
    stats = {
        'total_prepared': total_prepared,
        'total_leftover': total_leftover,
        'total_actual': total_actual,
        'total_expected': total_expected,
        'total_preparations': len(meal_preps)
    }
    
    return render_template('meal_preparation_history.html', meal_preps=meal_preps, stats=stats)

@menu_bp.route('/meal_preparation/delete/<int:prep_id>', methods=['POST'])
@admin_required
def delete_meal_preparation(prep_id):
    """Delete a meal preparation record."""
    from config import MEAL_PREPARATION_CSV
    meal_prep_df = read_csv(MEAL_PREPARATION_CSV)
    
    if meal_prep_df.empty:
        flash('No meal preparation records found', 'danger')
        return redirect(url_for('menu.meal_preparation_history'))
    
    # Remove the record
    meal_prep_df = meal_prep_df[meal_prep_df['id'] != prep_id]
    
    # Save the updated dataframe
    if write_csv(meal_prep_df, MEAL_PREPARATION_CSV):
        flash('Meal preparation record deleted successfully', 'success')
    else:
        flash('Error deleting meal preparation record', 'danger')
    
    return redirect(url_for('menu.meal_preparation_history'))
