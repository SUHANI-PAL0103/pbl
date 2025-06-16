#!/usr/bin/env python3
"""
Database debug script to check and recreate sample data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Course, Instructor, Student, Classroom, TimeSlot, Activity
from utils.sample_data import create_sample_data

def check_database():
    """Check what's currently in the database"""
    with app.app_context():
        print("=== DATABASE STATUS ===")
        print(f"TimeSlots: {TimeSlot.query.count()}")
        print(f"Classrooms: {Classroom.query.count()}")
        print(f"Instructors: {Instructor.query.count()}")
        print(f"Students: {Student.query.count()}")
        print(f"Courses: {Course.query.count()}")
        print(f"Activities: {Activity.query.count()}")
        
        print("\n=== TIME SLOTS ===")
        for ts in TimeSlot.query.all()[:10]:  # Show first 10
            print(f"  {ts}")
        
        print("\n=== CLASSROOMS ===")
        for classroom in Classroom.query.all():
            print(f"  {classroom}")
        
        print("\n=== COURSES ===")
        for course in Course.query.all():
            print(f"  {course.code}: {course.name} - Time: {course.time_slot} - Room: {course.classroom}")

def recreate_sample_data():
    """Delete all data and recreate sample data"""
    with app.app_context():
        print("Deleting all existing data...")
        
        # Delete in correct order to avoid foreign key issues
        Activity.query.delete()
        Course.query.delete()
        Student.query.delete()
        Instructor.query.delete()
        Classroom.query.delete()
        TimeSlot.query.delete()
        
        db.session.commit()
        print("All data deleted.")
        
        print("Creating sample data...")
        create_sample_data(db)
        db.session.commit()
        print("Sample data created successfully!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'recreate':
        recreate_sample_data()
    
    check_database()
