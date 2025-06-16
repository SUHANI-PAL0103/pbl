import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Course, Instructor, Student, Classroom, TimeSlot, Activity

scheduler_bp = Blueprint('scheduler', __name__)

@scheduler_bp.route('/scheduler')
def scheduler_view():
    return render_template('scheduler.html')

@scheduler_bp.route('/run_scheduler', methods=['POST'])
def run_scheduler():
    try:
        import networkx as nx
    except ImportError:
        flash('NetworkX library is required for scheduling. Please install it with: pip install networkx', 'danger')
        return redirect(url_for('scheduler.scheduler_view'))
    
    # Get all courses
    courses = Course.query.all()
    
    # Get all time slots
    time_slots = TimeSlot.query.all()
    if not time_slots:
        flash('No time slots available. Please add time slots first.', 'warning')
        return redirect(url_for('scheduler.scheduler_view'))
    
    # Get all classrooms
    classrooms = Classroom.query.all()
    if not classrooms:
        flash('No classrooms available. Please add classrooms first.', 'warning')
        return redirect(url_for('scheduler.scheduler_view'))
    
    # Build conflict graph
    G = nx.Graph()
    
    # Add nodes (courses)
    for course in courses:
        G.add_node(course.id, course=course)
    
    # Add edges for student conflicts
    for student in Student.query.all():
        student_courses = student.courses
        for i, course1 in enumerate(student_courses):
            for course2 in student_courses[i+1:]:
                G.add_edge(course1.id, course2.id, weight=1)
    
    # Add edges for instructor conflicts
    for instructor in Instructor.query.all():
        instructor_courses = Course.query.filter_by(instructor_id=instructor.id).all()
        for i, course1 in enumerate(instructor_courses):
            for course2 in instructor_courses[i+1:]:
                G.add_edge(course1.id, course2.id, weight=10)
    
    # Precompute degrees for sorting
    node_degrees = dict(G.degree())
    
    # Sort courses by degree (number of conflicts)
    courses_by_degree = sorted(G.nodes(), key=lambda x: node_degrees[x], reverse=True)
    
    # Run graph coloring algorithm (assign time slots)
    colors = {}  # course_id -> time_slot_id
    
    for course_id in courses_by_degree:
        # Get all neighbors of this course
        neighbors = list(G.neighbors(course_id))
        
        # Get the colors (time slots) already assigned to neighbors
        neighbor_colors = set(colors.get(neighbor) for neighbor in neighbors if neighbor in colors)
        
        # Find the first available color (time slot)
        for time_slot in time_slots:
            if time_slot.id not in neighbor_colors:
                colors[course_id] = time_slot.id
                break
    
    # Assign classrooms based on capacity needs
    for course_id in courses_by_degree:
        course = Course.query.get(course_id)
        student_count = len(course.students)
        
        # Find suitable classroom (with enough capacity)
        suitable_classrooms = [c for c in classrooms if c.capacity >= student_count]
        
        # Sort by capacity (to minimize waste)
        suitable_classrooms.sort(key=lambda x: x.capacity)
        
        # Find a classroom that's not already assigned to another course in this time slot
        assigned_classroom = None
        time_slot_id = colors.get(course_id)
        
        if time_slot_id:
            for classroom in suitable_classrooms:
                # Check if classroom is already used at this time
                is_used = Course.query.filter(
                    Course.classroom_id == classroom.id,
                    Course.time_slot_id == time_slot_id,
                    Course.id != course.id
                ).first()
                
                if not is_used:
                    assigned_classroom = classroom
                    break
            
            # Update course with time slot and classroom
            course.time_slot_id = time_slot_id
            course.classroom_id = assigned_classroom.id if assigned_classroom else None
    
    # Log activity
    activity = Activity(
        description="Generated timetable using scheduler",
        icon="fas fa-magic"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    # Count unscheduled courses
    unscheduled = sum(1 for course in courses if not course.time_slot_id)
    
    if unscheduled:
        flash(f'Timetable generated with {unscheduled} unscheduled courses. You may need to manually assign these.', 'warning')
    else:
        flash('Timetable generated successfully!', 'success')
    
    return redirect(url_for('scheduler.timetable'))

@scheduler_bp.route('/reset_schedule', methods=['POST'])
def reset_schedule():
    # Reset all course assignments
    Course.query.update({Course.time_slot_id: None, Course.classroom_id: None})
    
    # Log activity
    activity = Activity(
        description="Reset all course schedules",
        icon="fas fa-trash-alt"
    )
    db.session.add(activity)
    
    db.session.commit()
    flash('Schedule has been reset. All courses are now unscheduled.', 'success')
    return redirect(url_for('scheduler.timetable'))

@scheduler_bp.route('/unscheduled')
def unscheduled_courses():
    # Get all unscheduled courses
    courses = Course.query.filter_by(time_slot_id=None).all()
    return render_template('unscheduled.html', courses=courses)

@scheduler_bp.route('/timetable')
def timetable():    # Check for unscheduled courses
    unscheduled_count = Course.query.filter_by(time_slot_id=None).count()
    if unscheduled_count > 0:
        flash(f'There are {unscheduled_count} unscheduled courses. View them in the Unscheduled Courses section.', 'warning')
    
    # Get data for timetable display
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_slots = TimeSlot.query.order_by(TimeSlot.day, TimeSlot.start_time).all()
    courses = Course.query.all()
    instructors = Instructor.query.all()
    classrooms = Classroom.query.all()    # Group time slots by day
    time_slots_by_day = {}
    for day in days:
        time_slots_by_day[day] = [ts for ts in time_slots if ts.day == day]
    
    return render_template('timetable.html',
                          days=days, 
                          time_slots=time_slots,
                          time_slots_by_day=time_slots_by_day,
                          courses=courses,
                          instructors=instructors,
                          classrooms=classrooms)

@scheduler_bp.route('/export_timetable')
def export_timetable():
    import csv
    from io import StringIO
    from flask import Response
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Course Code', 'Course Name', 'Instructor', 'Day', 'Start Time', 'End Time', 'Classroom'])
    
    # Write data
    courses = Course.query.all()
    for course in courses:
        instructor_name = course.instructor.name if course.instructor else 'No Instructor'
        day = course.time_slot.day if course.time_slot else 'Not Scheduled'
        start_time = course.time_slot.start_time.strftime('%H:%M') if course.time_slot else ''
        end_time = course.time_slot.end_time.strftime('%H:%M') if course.time_slot else ''
        classroom = course.classroom.name if course.classroom else 'No Classroom'
        
        writer.writerow([
            course.code, 
            course.name, 
            instructor_name,
            day,
            start_time,
            end_time,
            classroom
        ])
    
    # Prepare response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=timetable.csv"}
    )

@scheduler_bp.route('/assign_course/<int:course_id>', methods=['GET', 'POST'])
def assign_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        time_slot_id = request.form.get('time_slot_id')
        classroom_id = request.form.get('classroom_id')
        
        course.time_slot_id = time_slot_id if time_slot_id else None
        course.classroom_id = classroom_id if classroom_id else None
        
        # Log activity
        activity = Activity(
            description=f"Assigned course {course.code} to a time slot and classroom",
            icon="fas fa-tasks"
        )
        db.session.add(activity)
        
        db.session.commit()
        flash('Course assigned successfully!', 'success')
        return redirect(url_for('courses.courses'))
    
    time_slots = TimeSlot.query.all()
    classrooms = Classroom.query.all()
    
    # Check for potential conflicts
    conflicts = []
    if course.instructor_id and course.time_slot_id:
        # Check for instructor conflicts
        instructor_conflicts = Course.query.filter(
            Course.instructor_id == course.instructor_id,
            Course.time_slot_id == course.time_slot_id,
            Course.id != course.id
        ).all()
        if instructor_conflicts:
            conflicts.append(f"Instructor {course.instructor.name} is already teaching another course at this time")
    
    # Check for student conflicts
    if course.time_slot_id:
        for student in course.students:
            conflicting_courses = [c for c in student.courses 
                                 if c.time_slot_id == course.time_slot_id and c.id != course.id]
            if conflicting_courses:
                conflicts.append(f"Student {student.name} has another course at this time")
    
    return render_template('assign_course.html', 
                          course=course, 
                          time_slots=time_slots, 
                          classrooms=classrooms,
                          conflicts=conflicts)
