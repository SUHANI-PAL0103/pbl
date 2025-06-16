#!/usr/bin/env python
"""
University Timetable Scheduler Application
==========================================

This is the main entry point for the University Timetable Scheduler application.
Run this script to start the Flask development server.

Usage:
    python run.py

The application will be available at: http://127.0.0.1:5000
"""

import os
from app import create_app

def main():
    """Main function to start the application"""
    # Create the Flask app
    app = create_app('development')
    
    # Ensure the uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create database tables if they don't exist
    with app.app_context():
        from models import db, TimeSlot
        db.create_all()
        
        # Import and create sample data if database is empty
        if not TimeSlot.query.first():
            print("Creating sample data...")
            from utils.sample_data import create_sample_data
            create_sample_data(db)
            print("Sample data created successfully!")
    
    print("Starting University Timetable Scheduler...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask development server
    app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
