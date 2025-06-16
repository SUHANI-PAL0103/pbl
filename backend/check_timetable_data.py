from app import app
from models import db, Course, TimeSlot, Classroom, Instructor

with app.app_context():
    print("=== TIMETABLE DEBUG ===")
    
    time_slots = TimeSlot.query.order_by(TimeSlot.day, TimeSlot.start_time).all()
    courses = Course.query.all()
    
    print(f"Total time slots: {len(time_slots)}")
    print(f"Total courses: {len(courses)}")
    
    print("\n=== TIME SLOTS ===")
    for ts in time_slots:
        print(f"ID: {ts.id}, Day: {ts.day}, Time: {ts.start_time} - {ts.end_time}")
    
    print("\n=== COURSES WITH ASSIGNMENTS ===")
    scheduled_count = 0
    for course in courses:
        if course.time_slot_id:
            scheduled_count += 1
            print(f"{course.code}: Time Slot ID {course.time_slot_id}, Classroom ID {course.classroom_id}")
        else:
            print(f"{course.code}: UNSCHEDULED")
    
    print(f"\nScheduled courses: {scheduled_count}/{len(courses)}")
    
    # Check time periods generation
    time_periods = []
    for time_slot in time_slots:
        time_key = time_slot.start_time.strftime('%H:%M') + ' - ' + time_slot.end_time.strftime('%H:%M')
        if time_key not in time_periods:
            time_periods.append(time_key)
    
    print(f"\nUnique time periods: {time_periods}")
