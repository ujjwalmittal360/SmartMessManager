import os
import pandas as pd
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from utils import read_csv, write_csv, get_next_id, get_current_date, get_current_time
from config import STUDENTS_CSV, STUDENT_IMAGES_DIR
from face_recognition_utils import detect_face, save_face_image, decode_base64_image
from auth import login_required

student_bp = Blueprint('student', __name__)

@student_bp.route('/student/register', methods=['GET', 'POST'])
@login_required
def register_student():
    """Register a new student with face image capture."""
    if request.method == 'POST':
        name = request.form.get('name')
        roll_number = request.form.get('roll_number')
        image_data = request.form.get('image_data')
        
        if not name or not roll_number or not image_data:
            flash('Please provide name, roll number, and capture an image', 'danger')
            return render_template('student_registration.html')
        
        # Read existing students
        students_df = read_csv(STUDENTS_CSV)
        
        # Check if roll number already exists
        if not students_df.empty and 'roll_number' in students_df.columns:
            if (students_df['roll_number'] == roll_number).any():
                flash('A student with this roll number already exists', 'danger')
                return render_template('student_registration.html')
        
        # Decode base64 image
        img = decode_base64_image(image_data)
        if img is None:
            flash('Error processing the captured image', 'danger')
            return render_template('student_registration.html')
        
        # Detect face in the image
        face_img, face_rect = detect_face(img)
        if face_img is None:
            flash('No face detected in the image. Please try again.', 'danger')
            return render_template('student_registration.html')
        
        # Get next student ID
        student_id = get_next_id(STUDENTS_CSV)
        
        # Save face image
        image_path = save_face_image(face_img, student_id)
        if not image_path:
            flash('Error saving the student image', 'danger')
            return render_template('student_registration.html')
        
        # Create new student record
        new_student = {
            'id': student_id,
            'name': name,
            'roll_number': roll_number,
            'image_path': image_path,
            'registration_date': get_current_date()
        }
        
        # Add to dataframe
        if students_df.empty:
            students_df = pd.DataFrame([new_student])
        else:
            students_df = pd.concat([students_df, pd.DataFrame([new_student])], ignore_index=True)
        
        # Save to CSV
        if write_csv(students_df, STUDENTS_CSV):
            flash(f'Student {name} registered successfully', 'success')
            return redirect(url_for('student.students_list'))
        else:
            flash('Error registering student', 'danger')
    
    return render_template('student_registration.html')

@student_bp.route('/students')
@login_required
def students_list():
    """Display a list of all registered students."""
    students_df = read_csv(STUDENTS_CSV)
    students = []
    
    if not students_df.empty:
        students = students_df.to_dict('records')
    
    return render_template('students_list.html', students=students)

@student_bp.route('/student/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    """Delete a student."""
    students_df = read_csv(STUDENTS_CSV)
    
    if students_df.empty:
        flash('No students found', 'danger')
        return redirect(url_for('student.students_list'))
    
    # Find the student
    student = students_df[students_df['id'] == student_id]
    
    if student.empty:
        flash('Student not found', 'danger')
        return redirect(url_for('student.students_list'))
    
    # Get the image path
    image_path = student.iloc[0]['image_path']
    
    # Remove the image file
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
        except Exception as e:
            flash(f'Error removing student image: {e}', 'warning')
    
    # Remove the student from the dataframe
    students_df = students_df[students_df['id'] != student_id]
    
    # Save the updated dataframe
    if write_csv(students_df, STUDENTS_CSV):
        flash('Student deleted successfully', 'success')
    else:
        flash('Error deleting student', 'danger')
    
    return redirect(url_for('student.students_list'))

@student_bp.route('/student/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit a student's information."""
    students_df = read_csv(STUDENTS_CSV)
    
    if students_df.empty:
        flash('No students found', 'danger')
        return redirect(url_for('student.students_list'))
    
    # Find the student
    student_idx = students_df.index[students_df['id'] == student_id].tolist()
    
    if not student_idx:
        flash('Student not found', 'danger')
        return redirect(url_for('student.students_list'))
    
    student = students_df.iloc[student_idx[0]]
    
    if request.method == 'POST':
        name = request.form.get('name')
        roll_number = request.form.get('roll_number')
        image_data = request.form.get('image_data')
        
        if not name or not roll_number:
            flash('Please provide name and roll number', 'danger')
            return render_template('student_edit.html', student=student.to_dict())
        
        # Check if roll number already exists for another student
        other_student = students_df[(students_df['roll_number'] == roll_number) & (students_df['id'] != student_id)]
        if not other_student.empty:
            flash('Another student with this roll number already exists', 'danger')
            return render_template('student_edit.html', student=student.to_dict())
        
        # Update basic info
        students_df.at[student_idx[0], 'name'] = name
        students_df.at[student_idx[0], 'roll_number'] = roll_number
        
        # If new image is provided, update the face image
        if image_data:
            img = decode_base64_image(image_data)
            if img is not None:
                face_img, face_rect = detect_face(img)
                if face_img is not None:
                    # Save new face image
                    image_path = save_face_image(face_img, student_id)
                    if image_path:
                        students_df.at[student_idx[0], 'image_path'] = image_path
                    else:
                        flash('Error saving the new student image', 'warning')
                else:
                    flash('No face detected in the new image', 'warning')
            else:
                flash('Error processing the new image', 'warning')
        
        # Save the updated dataframe
        if write_csv(students_df, STUDENTS_CSV):
            flash('Student updated successfully', 'success')
            return redirect(url_for('student.students_list'))
        else:
            flash('Error updating student', 'danger')
    
    return render_template('student_edit.html', student=student.to_dict())
