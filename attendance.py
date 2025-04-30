import os
import pandas as pd
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from utils import (
    read_csv, write_csv, get_next_id, get_current_date, get_current_time, 
    get_current_meal_type, get_current_day_of_week, get_current_day_meal,
    get_meal_name_from_menu
)
from config import STUDENTS_CSV, ATTENDANCE_CSV, STUDENT_IMAGES_DIR, MEAL_TYPES
from face_recognition_utils import detect_face, recognize_face, decode_base64_image
from auth import login_required

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
def take_attendance():
    """Take attendance using face recognition."""
    meal_types = MEAL_TYPES
    
    # Get current day and meal type based on time
    current_day = get_current_day_of_week()
    current_meal = get_current_meal_type()
    
    # Get the corresponding meal name from the menu
    current_meal_name = get_meal_name_from_menu(current_day, current_meal)
    
    if request.method == 'POST':
        image_data = request.form.get('image_data')
        meal_type = request.form.get('meal_type', current_meal)
        leftover_weight = request.form.get('leftover_weight', '0')
        
        if not image_data:
            flash('Please capture an image', 'danger')
            return render_template('attendance.html', 
                                  meal_types=meal_types, 
                                  current_meal=current_meal,
                                  current_day=current_day,
                                  current_meal_name=current_meal_name)
        
        # Try to convert leftover weight to float
        try:
            leftover_weight = float(leftover_weight)
        except ValueError:
            flash('Leftover weight must be a number', 'danger')
            return render_template('attendance.html', 
                                  meal_types=meal_types, 
                                  current_meal=current_meal,
                                  current_day=current_day,
                                  current_meal_name=current_meal_name)
        
        # Decode base64 image
        img = decode_base64_image(image_data)
        if img is None:
            flash('Error processing the captured image', 'danger')
            return render_template('attendance.html', 
                                  meal_types=meal_types, 
                                  current_meal=current_meal,
                                  current_day=current_day,
                                  current_meal_name=current_meal_name)
        
        # Detect face in the image
        face_img, face_rect = detect_face(img)
        if face_img is None:
            flash('No face detected in the image. Please try again.', 'danger')
            return render_template('attendance.html', 
                                  meal_types=meal_types, 
                                  current_meal=current_meal,
                                  current_day=current_day,
                                  current_meal_name=current_meal_name)
        
        # Recognize the face
        student_id = recognize_face(face_img, STUDENT_IMAGES_DIR)
        if not student_id:
            flash('Student not recognized. Please try again or register the student.', 'danger')
            return render_template('attendance.html', 
                                  meal_types=meal_types, 
                                  current_meal=current_meal,
                                  current_day=current_day,
                                  current_meal_name=current_meal_name)
        
        # Get student information
        students_df = read_csv(STUDENTS_CSV)
        if students_df.empty:
            flash('Error: No students registered in the system', 'danger')
            return render_template('attendance.html', 
                                  meal_types=meal_types, 
                                  current_meal=current_meal,
                                  current_day=current_day,
                                  current_meal_name=current_meal_name)
        
        student = students_df[students_df['id'] == int(student_id)]
        if student.empty:
            flash('Error: Student not found in the database', 'danger')
            return render_template('attendance.html', 
                                  meal_types=meal_types, 
                                  current_meal=current_meal,
                                  current_day=current_day,
                                  current_meal_name=current_meal_name)
        
        student_name = student.iloc[0]['name']
        student_roll = student.iloc[0]['roll_number']
        
        # Read attendance data
        attendance_df = read_csv(ATTENDANCE_CSV)
        
        # Check if student already attended this meal today
        today = get_current_date()
        if not attendance_df.empty:
            existing_attendance = attendance_df[
                (attendance_df['student_id'] == int(student_id)) & 
                (attendance_df['date'] == today) & 
                (attendance_df['meal_type'] == meal_type)
            ]
            
            if not existing_attendance.empty:
                flash(f'{student_name} already attended {meal_type} today. Updating leftover weight.', 'warning')
                
                # Update leftover weight
                idx = existing_attendance.index[0]
                attendance_df.at[idx, 'leftover_weight'] = leftover_weight
                
                if write_csv(attendance_df, ATTENDANCE_CSV):
                    flash(f'Updated leftover weight for {student_name}', 'success')
                else:
                    flash('Error updating attendance record', 'danger')
                
                return render_template('attendance.html', 
                                      meal_types=meal_types, 
                                      current_meal=current_meal,
                                      current_day=current_day,
                                      current_meal_name=current_meal_name,
                                      student_name=student_name, 
                                      student_roll=student_roll)
        
        # Create new attendance record
        attendance_id = get_next_id(ATTENDANCE_CSV)
        current_time = get_current_time()
        
        new_attendance = {
            'id': attendance_id,
            'student_id': int(student_id),
            'date': today,
            'time': current_time,
            'meal_type': meal_type,
            'leftover_weight': leftover_weight
        }
        
        # Add to dataframe
        if attendance_df.empty:
            attendance_df = pd.DataFrame([new_attendance])
        else:
            attendance_df = pd.concat([attendance_df, pd.DataFrame([new_attendance])], ignore_index=True)
        
        # Save to CSV
        if write_csv(attendance_df, ATTENDANCE_CSV):
            flash(f'Attendance recorded for {student_name} ({student_roll}) for {meal_type}', 'success')
        else:
            flash('Error recording attendance', 'danger')
        
        return render_template('attendance.html', 
                              meal_types=meal_types, 
                              current_meal=current_meal,
                              current_day=current_day,
                              current_meal_name=current_meal_name,
                              student_name=student_name, 
                              student_roll=student_roll)
    
    return render_template('attendance.html', 
                          meal_types=meal_types, 
                          current_meal=current_meal,
                          current_day=current_day,
                          current_meal_name=current_meal_name)

@attendance_bp.route('/attendance/history')
@login_required
def attendance_history():
    """View attendance history."""
    attendance_df = read_csv(ATTENDANCE_CSV)
    students_df = read_csv(STUDENTS_CSV)
    
    if attendance_df.empty or students_df.empty:
        return render_template('attendance_history.html', attendance_records=[])
    
    # Join attendance with student information
    merged_df = pd.merge(
        attendance_df,
        students_df[['id', 'name', 'roll_number']],
        left_on='student_id',
        right_on='id',
        suffixes=('', '_student')
    )
    
    # Sort by date and time (newest first)
    merged_df = merged_df.sort_values(by=['date', 'time'], ascending=[False, False])
    
    attendance_records = merged_df.to_dict('records')
    
    return render_template('attendance_history.html', attendance_records=attendance_records)

@attendance_bp.route('/attendance/delete/<int:attendance_id>', methods=['POST'])
@login_required
def delete_attendance(attendance_id):
    """Delete an attendance record."""
    attendance_df = read_csv(ATTENDANCE_CSV)
    
    if attendance_df.empty:
        flash('No attendance records found', 'danger')
        return redirect(url_for('attendance.attendance_history'))
    
    # Remove the record
    attendance_df = attendance_df[attendance_df['id'] != attendance_id]
    
    # Save the updated dataframe
    if write_csv(attendance_df, ATTENDANCE_CSV):
        flash('Attendance record deleted successfully', 'success')
    else:
        flash('Error deleting attendance record', 'danger')
    
    return redirect(url_for('attendance.attendance_history'))

@attendance_bp.route('/attendance/report')
@login_required
def attendance_report():
    """Generate attendance report."""
    attendance_df = read_csv(ATTENDANCE_CSV)
    students_df = read_csv(STUDENTS_CSV)
    
    if attendance_df.empty or students_df.empty:
        return render_template('attendance_report.html', daily_stats=[], student_stats=[])
    
    # Get date range for filtering
    from_date = request.args.get('from_date', get_current_date())
    to_date = request.args.get('to_date', get_current_date())
    
    # Filter by date range
    filtered_df = attendance_df[(attendance_df['date'] >= from_date) & (attendance_df['date'] <= to_date)]
    
    # Daily statistics
    daily_stats = filtered_df.groupby(['date', 'meal_type']).size().reset_index(name='count')
    daily_stats = daily_stats.sort_values(['date', 'meal_type'])
    
    # Student statistics
    student_stats = filtered_df.groupby('student_id').size().reset_index(name='attendance_count')
    student_stats = pd.merge(
        student_stats,
        students_df[['id', 'name', 'roll_number']],
        left_on='student_id',
        right_on='id'
    )
    student_stats = student_stats.sort_values('attendance_count', ascending=False)
    
    return render_template('attendance_report.html', 
                          daily_stats=daily_stats.to_dict('records'),
                          student_stats=student_stats.to_dict('records'),
                          from_date=from_date,
                          to_date=to_date)
