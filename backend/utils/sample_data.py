import datetime
import logging # Added import
from models import Course, Instructor, Student, Classroom, TimeSlot, Activity

def create_sample_data(db):
    """Create sample data for testing the application"""

    # Configure logging (can be done once at application startup too)
    logging.basicConfig(level=logging.INFO)
    
    # Create sample time slots
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_periods = [
        ('08:00', '09:30'),
        ('09:45', '11:15'),
        ('11:30', '13:00'),
        ('14:00', '15:30'),
        ('15:45', '17:15')
    ]
    
    for day in days:
        for start_str, end_str in time_periods:
            start_time = datetime.datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.datetime.strptime(end_str, '%H:%M').time()
            
            timeslot = TimeSlot()
            timeslot.day = day
            timeslot.start_time = start_time
            timeslot.end_time = end_time
            db.session.add(timeslot)
    
    # Create sample classrooms
    classrooms_data = [
        ('Room A101', 60),
        ('Room B202', 70),
        ('Room C303', 60),
        ('Lab CS1', 40),
        ('Seminar Hall', 120)
    ]
    
    
    for name, capacity in classrooms_data:
        classroom = Classroom()
        classroom.name = name
        classroom.capacity = capacity
        db.session.add(classroom)
    
    # Create sample instructors
    instructors_data = [
        ('Dr. Rajesh Kumar', 'rajesh.kumar@university.edu', 'Computer Science & Engineering'),
        ('Prof. Priya Sharma', 'priya.sharma@university.edu', 'Mathematics'),
        ('Dr. Anil Patel', 'anil.patel@university.edu', 'Electronics Engineering'),
        ('Prof. Sunita Singh', 'sunita.singh@university.edu', 'Mechanical Engineering'),
        ('Dr. Vijay Mehta', 'vijay.mehta@university.edu', 'Communication Skills')
    ]
    
    for name, email, department in instructors_data:
        instructor = Instructor()
        instructor.name = name
        instructor.email = email
        instructor.department = department
        db.session.add(instructor)
    
    # Commit to get IDs for instructors (and timeslots, classrooms)
    db.session.commit()
    
    # Map instructor emails to their IDs
    instructor_email_to_id = {instructor.email: instructor.id for instructor in Instructor.query.all()}
    
    # Create sample courses with instructor emails
    courses_data = [
        ('CSE101', 'Introduction to Programming', 'rajesh.kumar@university.edu'),
        ('MAT101', 'Engineering Mathematics I', 'priya.sharma@university.edu'),
        ('ECE101', 'Basic Electronics Engineering', 'anil.patel@university.edu'),
        ('MECH101', 'Engineering Mechanics', 'sunita.singh@university.edu'),
        ('HUM101', 'Communication Skills', 'vijay.mehta@university.edu'),
        ('CSE201', 'Data Structures and Algorithms', 'rajesh.kumar@university.edu'),
        ('MAT201', 'Engineering Mathematics II', 'priya.sharma@university.edu')
    ]
    
    for code, name, instructor_email in courses_data:
        instructor_id = instructor_email_to_id.get(instructor_email)
        if instructor_id: # Ensure instructor was found
            course = Course()
            course.code = code
            course.name = name
            course.instructor_id = instructor_id
            db.session.add(course)
        else:
            logging.warning(f"Instructor email {instructor_email} not found for course {code}. Skipping course.")

    # Create sample students
    students_data = [
        ('Aarav Sharma', 'aarav.sharma@student.edu'),
        ('Priya Patel', 'priya.patel@student.edu'),
        ('Rohan Kumar', 'rohan.kumar@student.edu'),
        ('Sneha Reddy', 'sneha.reddy@student.edu'),
        ('Vikram Singh', 'vikram.singh@student.edu')
    ]

    for name, email in students_data: # Added loop to create student objects
        student = Student()
        student.name = name
        student.email = email
        db.session.add(student)
    
    # Commit to get IDs for courses and students
    db.session.commit()
    
    # Build mappings from student name/email and course code to their IDs
    students = Student.query.all()
    courses = Course.query.all()
    student_map = {s.name: s for s in students} # Using name as key, ensure names are unique or use email
    course_map = {c.code: c for c in courses}
    
    # Sample enrollments using names and course codes
    enrollments_data = [
        ('Aarav Sharma', ['CSE101', 'MAT101', 'ECE101']),
        ('Priya Patel', ['CSE101', 'MECH101', 'HUM101']),
        ('Rohan Kumar', ['MAT101', 'ECE101', 'CSE201']),
        ('Sneha Reddy', ['MECH101', 'HUM101', 'MAT201']),
        ('Vikram Singh', ['CSE101', 'CSE201', 'MAT201'])
    ]
    
    for student_name, course_codes in enrollments_data:
        student = student_map.get(student_name)
        if student:
            for code in course_codes:
                course = course_map.get(code)
                if course and course not in student.courses:
                    student.courses.append(course) # This modifies the student's courses relationship
        else:
            logging.warning(f"Student {student_name} not found for enrollment. Skipping.")
    
    # Create welcome activity
    activity = Activity()
    activity.description = "Welcome to University Timetable Scheduler! Sample data has been loaded."
    activity.icon = "fas fa-star"
    db.session.add(activity) # Add activity to session
    
    # Commit enrollments and activity
    db.session.commit()
    
    logging.info("Sample data created successfully!")
    # Removed redundant db.session.commit() and print()
