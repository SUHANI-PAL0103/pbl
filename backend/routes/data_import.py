import csv
import os
from flask import Blueprint, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from models import db, Course, Instructor, Student, Classroom, TimeSlot, CourseMaterial, Activity

data_import_bp = Blueprint('data_import', __name__)

@data_import_bp.route('/quick_update', methods=['POST'])
def quick_update():
    update_type = request.form.get('type')
    entity_id = request.form.get('id')
    
    if not update_type or not entity_id:
        flash('Missing required data', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        # Handle quick updates for different entity types
        if update_type == 'course':
            course = Course.query.get(entity_id)
            name = request.form.get('name')
            code = request.form.get('code')
            
            if course and name and code:
                course.name = name
                course.code = code
                activity = Activity(
                    description=f"Quick updated course: {course.name}",
                    icon="fas fa-edit"
                )
                db.session.add(activity)
                db.session.commit()
                flash('Course updated successfully', 'success')
        
        elif update_type == 'instructor':
            instructor = Instructor.query.get(entity_id)
            name = request.form.get('name')
            email = request.form.get('email')
            
            if instructor and name and email:
                instructor.name = name
                instructor.email = email
                activity = Activity(
                    description=f"Quick updated instructor: {instructor.name}",
                    icon="fas fa-edit"
                )
                db.session.add(activity)
                db.session.commit()
                flash('Instructor updated successfully', 'success')
        
        elif update_type == 'classroom':
            classroom = Classroom.query.get(entity_id)
            name = request.form.get('name')
            capacity = request.form.get('capacity')
            
            if classroom and name and capacity:
                classroom.name = name
                classroom.capacity = int(capacity)
                activity = Activity(
                    description=f"Quick updated classroom: {classroom.name}",
                    icon="fas fa-edit"
                )
                db.session.add(activity)
                db.session.commit()
                flash('Classroom updated successfully', 'success')
    
    except Exception as e:
        flash(f'Error updating {update_type}: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard.index'))

@data_import_bp.route('/upload', methods=['POST'])
def upload_data():
    # Check if any file was uploaded
    if 'fileUpload' not in request.files and 'pdfFileUpload' not in request.files:
        flash('No file provided', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # CSV data import
    if 'fileUpload' in request.files:
        file = request.files['fileUpload']
        filename = file.filename
        
        if not filename:
            flash('No file selected', 'danger')
            return redirect(url_for('dashboard.index'))
        
        if filename.endswith('.csv'):
            data_type = request.form.get('dataType', '')  # Default to empty string
            
            try:
                csv_data = []
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                csv_data = list(reader)
                
                if not csv_data:
                    flash('CSV file is empty', 'danger')
                    return redirect(url_for('dashboard.index'))
                
                headers = csv_data[0]
                rows = csv_data[1:]
                
                # Process based on data type
                if data_type == 'courses':
                    import_courses(headers, rows)
                elif data_type == 'instructors':
                    import_instructors(headers, rows)
                elif data_type == 'students':
                    import_students(headers, rows)
                elif data_type == 'classrooms':
                    import_classrooms(headers, rows)
                elif data_type == 'timeslots':
                    import_timeslots(headers, rows)
                elif data_type == 'enrollments':
                    import_enrollments(headers, rows)
                elif data_type == 'timetable':
                    import_timetable(headers, rows)
                else:
                    flash('Invalid data type selected', 'danger')
                    return redirect(url_for('dashboard.index'))
                
                # Log activity
                activity = Activity(
                    description=f"Imported {data_type} data from CSV",
                    icon="fas fa-file-import"
                )
                db.session.add(activity)
                db.session.commit()
                
                flash(f'Successfully imported {data_type} data', 'success')
                return redirect(url_for('dashboard.index'))
                
            except Exception as e:
                flash(f'Error processing CSV file: {str(e)}', 'danger')
                return redirect(url_for('dashboard.index'))
    
    # PDF document upload
    elif 'pdfFileUpload' in request.files:
        file = request.files['pdfFileUpload']
        if not file or file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('dashboard.index'))
        
        document_type = request.form.get('document_type', '')
        course_id = request.form.get('course_id')
        
        material_name_default = "Material"  # Default if document_type is None or empty
        if document_type:
            material_name_default = document_type.capitalize()
        material_name = request.form.get('material_name', material_name_default)
        
        if file and file.filename and allowed_file(file.filename, {'pdf'}):
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # If it's course material, add to database
                if document_type == 'course_material' and course_id:
                    material = CourseMaterial(
                        course_id=course_id,
                        name=material_name,
                        description="Uploaded from dashboard",
                        file_path=filename
                    )
                    db.session.add(material)
                    
                    # Log activity
                    activity = Activity(
                        description=f"Uploaded {document_type}: {material_name}",
                        icon="fas fa-file-pdf"
                    )
                    db.session.add(activity)
                    db.session.commit()
                    
                    flash('File uploaded successfully', 'success')
                    return redirect(url_for('dashboard.index'))
                else:
                    flash('Missing required data for course material', 'danger')
                    return redirect(url_for('dashboard.index'))
                    
            except Exception as e:
                flash(f'Error uploading file: {str(e)}', 'danger')
                return redirect(url_for('dashboard.index'))
        else:
            flash('Only PDF files are allowed', 'danger')
            return redirect(url_for('dashboard.index'))
        
    return redirect(url_for('dashboard.index'))

# Helper functions for CSV import
def import_courses(headers, rows):
    for row in rows:
        row_data = dict(zip(headers, row))
        course = Course()
        course.name = row_data.get('name', '').strip()
        course.code = row_data.get('code', '').strip()
        course.description = row_data.get('description', '').strip()
        course.credits = int(row_data.get('credits', 0))
        db.session.add(course)
    db.session.commit()

def import_instructors(headers, rows):
    for row in rows:
        row_data = dict(zip(headers, row))
        instructor = Instructor()
        instructor.name = row_data.get('name', '').strip()
        instructor.email = row_data.get('email', '').strip()
        instructor.department = row_data.get('department', '').strip()
        db.session.add(instructor)
    db.session.commit()

def import_students(headers, rows):
    for row in rows:
        row_data = dict(zip(headers, row))
        student = Student()
        student.name = row_data.get('name', '').strip()
        student.email = row_data.get('email', '').strip()
        student.roll_number = row_data.get('roll_number', '').strip()
        student.year = int(row_data.get('year', 1))
        db.session.add(student)
    db.session.commit()

def import_classrooms(headers, rows):
    for row in rows:
        row_data = dict(zip(headers, row))
        classroom = Classroom()
        classroom.name = row_data.get('name', '').strip()
        classroom.capacity = int(row_data.get('capacity', 0))
        classroom.building = row_data.get('building', '').strip()
        db.session.add(classroom)
    db.session.commit()

def import_timeslots(headers, rows):
    for row in rows:
        row_data = dict(zip(headers, row))
        timeslot = TimeSlot()
        timeslot.day = row_data.get('day', '').strip()
        timeslot.start_time = row_data.get('start_time', '').strip()
        timeslot.end_time = row_data.get('end_time', '').strip()
        db.session.add(timeslot)
    db.session.commit()

def import_enrollments(headers, rows):
    for row in rows:
        row_data = dict(zip(headers, row))
        student_id = row_data.get('student_id', '').strip()
        course_id = row_data.get('course_id', '').strip()
        
        if student_id and course_id:
            student = Student.query.get(student_id)
            course = Course.query.get(course_id)
            if student and course:
                student.courses.append(course)
    db.session.commit()

def import_timetable(headers, rows):
    for row in rows:
        row_data = dict(zip(headers, row))
        course_id = row_data.get('course_id', '').strip()
        instructor_id = row_data.get('instructor_id', '').strip()
        classroom_id = row_data.get('classroom_id', '').strip()
        timeslot_id = row_data.get('timeslot_id', '').strip()
        
        if all([course_id, instructor_id, classroom_id, timeslot_id]):
            course = Course.query.get(course_id)
            if course:
                course.instructor_id = instructor_id
                course.classroom_id = classroom_id
                course.time_slot_id = timeslot_id
                db.session.add(course)
    db.session.commit()

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
