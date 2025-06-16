from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Course, Instructor, Activity

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@courses_bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        instructor_id = request.form.get('instructor_id')
        
        # Check if course code already exists
        existing_course = Course.query.filter_by(code=code).first()
        if existing_course:
            flash('Course code already exists!', 'danger')
            return redirect(url_for('courses.add_course'))
        
        instructor_id = instructor_id if instructor_id else None
        
        course = Course()
        course.code = code
        course.name = name
        course.instructor_id = instructor_id
        db.session.add(course)
        
        # Log activity
        activity = Activity()
        activity.description = f"Added new course: {code} - {name}"
        activity.icon = "fas fa-book"
        db.session.add(activity)
        
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('courses.courses'))
    
    instructors = Instructor.query.all()
    return render_template('add_course.html', instructors=instructors)

@courses_bp.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        instructor_id = request.form.get('instructor_id')
        
        # Check if course code already exists (excluding current course)
        existing_course = Course.query.filter(Course.code == code, Course.id != course_id).first()
        if existing_course:
            flash('Course code already exists!', 'danger')
            return redirect(url_for('courses.edit_course', course_id=course_id))
        
        course.code = code
        course.name = name
        course.instructor_id = instructor_id if instructor_id else None
        
        # Log activity
        # Log activity
        activity = Activity()
        activity.description = f"Updated course: {course.code}"
        activity.icon = "fas fa-edit"
        db.session.add(activity)
        
        db.session.commit()
        return redirect(url_for('courses.courses'))
    
    instructors = Instructor.query.all()
    return render_template('edit_course.html', course=course, instructors=instructors)

@courses_bp.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Log activity
    activity = Activity()
    activity.description = f"Deleted course: {course.code} - {course.name}"
    activity.icon = "fas fa-trash"
    db.session.add(activity)
    
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses.courses'))

@courses_bp.route('/assign_course/<int:course_id>', methods=['GET', 'POST'])
def assign_course(course_id):
    from models import TimeSlot, Classroom
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        time_slot_id = request.form.get('time_slot_id')
        classroom_id = request.form.get('classroom_id')
        
        course.time_slot_id = time_slot_id if time_slot_id else None
        course.classroom_id = classroom_id if classroom_id else None
        
        # Log activity
        activity = Activity()
        activity.description = f"Assigned course {course.code} to schedule"
        activity.icon = "fas fa-calendar-plus"
        db.session.add(activity)
        
        db.session.commit()
        flash('Course assigned successfully!', 'success')
        return redirect(url_for('courses.courses'))
    
    time_slots = TimeSlot.query.all()
    classrooms = Classroom.query.all()
    return render_template('assign_course.html', course=course, time_slots=time_slots, classrooms=classrooms)
