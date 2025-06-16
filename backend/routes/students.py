from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Student, Course, Activity

students_bp = Blueprint('students', __name__)

@students_bp.route('/students')
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@students_bp.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # Check if student email already exists
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            flash('Student email already exists!', 'danger')
            return redirect(url_for('students.add_student'))
        
        student = Student()
        student.name = name
        student.email = email
        db.session.add(student)
        
        # Log activity
        activity = Activity()
        activity.description = f"Added new student: {name}"
        activity.icon = "fas fa-user-graduate"
        db.session.add(activity)
        
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('students.students'))
    
    return render_template('add_student.html')

@students_bp.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # Check if student email already exists (excluding current student)
        existing_student = Student.query.filter(Student.email == email, Student.id != student_id).first()
        if existing_student:
            flash('Student email already exists!', 'danger')
            return redirect(url_for('students.edit_student', student_id=student_id))
        student.email = email
        
        # Log activity
        activity = Activity()
        activity.description = f"Updated student: {student.name}"
        activity.icon = "fas fa-edit"
        db.session.add(activity)
        
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('students.students'))
    
    return render_template('edit_student.html', student=student)

    return render_template('edit_student.html', student=student)

@students_bp.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Log activity
    activity = Activity()
    activity.description = f"Deleted student: {student.name}"
    activity.icon = "fas fa-trash"
    db.session.add(activity)
    
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students.students'))

@students_bp.route('/enroll_student/<int:student_id>', methods=['GET', 'POST'])
def enroll_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        # Clear current enrollments
        student.courses = []
        
        # Add new enrollments
        course_ids = request.form.getlist('course_ids')
        for course_id in course_ids:
            course = Course.query.get(course_id)
            if course:
                student.courses.append(course)
        
        # Log activity
        activity = Activity()
        activity.description = f"Updated enrollments for student: {student.name}"
        activity.icon = "fas fa-user-plus"
        db.session.add(activity)
        
        db.session.commit()
        flash('Student enrollments updated successfully!', 'success')
        return redirect(url_for('students.students'))
    
    courses = Course.query.all()
    return render_template('enroll_student.html', student=student, courses=courses)
