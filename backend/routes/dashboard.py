from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Course, Instructor, Student, Classroom, TimeSlot, Activity

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    stats = {
        'courses': Course.query.count(),
        'instructors': Instructor.query.count(),
        'students': Student.query.count(),
        'classrooms': Classroom.query.count(),
        'scheduled_courses': Course.query.filter(Course.time_slot_id.isnot(None)).count()
    }
    
    activities = Activity.query.order_by(Activity.timestamp.desc()).limit(10).all()
    
    # For quick update form
    courses_for_upload = Course.query.all()
    instructors_for_upload = Instructor.query.all()
    classrooms_for_upload = Classroom.query.all()
    timeslots_for_upload = TimeSlot.query.all()
    
    return render_template('index.html', 
                          stats=stats, 
                          activities=activities,
                          courses_for_upload=courses_for_upload,
                          instructors_for_upload=instructors_for_upload,
                          classrooms_for_upload=classrooms_for_upload,
                          timeslots_for_upload=timeslots_for_upload)

@dashboard_bp.route('/dashboard')
def dashboard():
    return redirect(url_for('dashboard.index'))
