# University Timetable Scheduler - Backend

This is the backend for the University Timetable Scheduler application built with Flask and SQLAlchemy.

## Features

- **Course Management**: Add, edit, delete, and view courses
- **Instructor Management**: Manage instructor information and assignments
- **Student Management**: Handle student enrollments and course registrations
- **Classroom Management**: Manage classroom capacity and availability
- **Time Slot Management**: Define available time periods for classes
- **Automatic Scheduling**: Graph coloring algorithm for conflict-free timetable generation
- **Conflict Detection**: Identify and visualize scheduling conflicts
- **Course Materials**: Upload and manage course materials (PDF, DOC, etc.)
- **Data Import/Export**: CSV import/export functionality
- **Activity Logging**: Track all system activities

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── config.py             # Configuration settings
├── run.py                # Application startup script
├── requirements.txt      # Python dependencies
├── routes/               # Route handlers (blueprints)
│   ├── __init__.py
│   ├── dashboard.py      # Dashboard and main page routes
│   ├── courses.py        # Course management routes
│   ├── instructors.py    # Instructor management routes
│   ├── students.py       # Student management routes
│   ├── classrooms.py     # Classroom management routes
│   ├── timeslots.py      # Time slot management routes
│   ├── scheduler.py      # Scheduling algorithm routes
│   ├── conflicts.py      # Conflict detection routes
│   ├── materials.py      # Course materials routes
│   └── data_import.py    # Data import/export routes
├── utils/                # Utility functions
│   ├── __init__.py
│   └── sample_data.py    # Sample data creation
└── uploads/              # File upload directory (created automatically)
```

## Installation

1. **Install Python** (3.8 or higher)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Access the application**:
   Open your browser and go to: http://127.0.0.1:5000

## Database Models

### Core Models

- **Course**: Course information (code, name, instructor, time slot, classroom)
- **Instructor**: Instructor details (name, email, department)
- **Student**: Student information and course enrollments
- **Classroom**: Classroom details (name, capacity)
- **TimeSlot**: Time periods (day, start time, end time)
- **CourseMaterial**: File attachments for courses
- **Activity**: System activity logging

### Relationships

- Course ↔ Instructor (Many-to-One)
- Course ↔ Student (Many-to-Many)
- Course ↔ TimeSlot (Many-to-One)
- Course ↔ Classroom (Many-to-One)
- Course ↔ CourseMaterial (One-to-Many)

## API Endpoints

### Dashboard
- `GET /` - Main dashboard
- `POST /quick_update` - Quick update form

### Course Management
- `GET /courses` - List all courses
- `GET /add_course` - Add course form
- `POST /add_course` - Create new course
- `GET /edit_course/<id>` - Edit course form
- `POST /edit_course/<id>` - Update course
- `POST /delete_course/<id>` - Delete course
- `GET /assign_course/<id>` - Assign course form
- `POST /assign_course/<id>` - Assign time slot and classroom

### Instructor Management
- `GET /instructors` - List all instructors
- `GET /add_instructor` - Add instructor form
- `POST /add_instructor` - Create new instructor
- `GET /edit_instructor/<id>` - Edit instructor form
- `POST /edit_instructor/<id>` - Update instructor
- `POST /delete_instructor/<id>` - Delete instructor

### Student Management
- `GET /students` - List all students
- `GET /add_student` - Add student form
- `POST /add_student` - Create new student
- `GET /edit_student/<id>` - Edit student form
- `POST /edit_student/<id>` - Update student
- `POST /delete_student/<id>` - Delete student
- `GET /enroll_student/<id>` - Student enrollment form
- `POST /enroll_student/<id>` - Update student enrollments

### Classroom Management
- `GET /classrooms` - List all classrooms
- `GET /add_classroom` - Add classroom form
- `POST /add_classroom` - Create new classroom
- `GET /edit_classroom/<id>` - Edit classroom form
- `POST /edit_classroom/<id>` - Update classroom
- `POST /delete_classroom/<id>` - Delete classroom

### Time Slot Management
- `GET /timeslots` - List all time slots
- `GET /add_timeslot` - Add time slot form
- `POST /add_timeslot` - Create new time slot
- `POST /delete_timeslot/<id>` - Delete time slot

### Scheduling
- `GET /scheduler` - Scheduler interface
- `POST /run_scheduler` - Run automatic scheduling algorithm
- `POST /reset_schedule` - Reset all course schedules
- `GET /timetable` - View generated timetable
- `GET /export_timetable` - Export timetable as CSV

### Conflict Management
- `GET /conflicts` - View all conflicts
- `GET /graph` - View conflict graph visualization

### Course Materials
- `GET /course_materials/<course_id>` - Course materials page
- `POST /course_materials/<course_id>` - Upload course material
- `GET /download_material/<id>` - Download material file
- `POST /delete_material/<id>` - Delete course material

### Data Import/Export
- `POST /upload` - Import CSV data or upload files

## Scheduling Algorithm

The application uses a **graph coloring algorithm** for automatic timetable generation:

1. **Conflict Graph Construction**:
   - Nodes represent courses
   - Edges represent conflicts (shared students or instructors)

2. **Graph Coloring**:
   - Colors represent time slots
   - Algorithm assigns different colors to connected nodes
   - Ensures no conflicts in the final schedule

3. **Classroom Assignment**:
   - Assigns appropriate classrooms based on capacity requirements
   - Ensures no double-booking of classrooms

## File Upload

Supported file types for course materials:
- PDF (.pdf)
- Word Documents (.doc, .docx)
- Text Files (.txt)
- PowerPoint (.ppt, .pptx)

Maximum file size: 16MB

## CSV Import/Export

### Import Formats

**Courses** (courses.csv):
```csv
code,name,instructor_email
CS101,Introduction to Computer Science,john.smith@university.edu
MATH201,Calculus I,sarah.johnson@university.edu
```

**Instructors** (instructors.csv):
```csv
name,email,department
Dr. John Smith,john.smith@university.edu,Computer Science
Prof. Sarah Johnson,sarah.johnson@university.edu,Mathematics
```

**Students** (students.csv):
```csv
name,email
Alice Johnson,alice.johnson@student.edu
Bob Smith,bob.smith@student.edu
```

**Classrooms** (classrooms.csv):
```csv
name,capacity
Room A101,30
Room B202,50
```

**Time Slots** (timeslots.csv):
```csv
day,start_time,end_time
Monday,08:00,09:30
Monday,09:45,11:15
```

**Enrollments** (enrollments.csv):
```csv
student_email,course_code
alice.johnson@student.edu,CS101
alice.johnson@student.edu,MATH201
```

### Export Format

The timetable can be exported as CSV with the following format:
```csv
Course Code,Course Name,Instructor,Day,Start Time,End Time,Classroom
CS101,Introduction to Computer Science,Dr. John Smith,Monday,08:00,09:30,Room A101
```

## Development

### Adding New Features

1. **Models**: Add new models to `models.py`
2. **Routes**: Create new route files in the `routes/` directory
3. **Templates**: Add corresponding HTML templates
4. **Blueprints**: Register new blueprints in `app.py`

### Database Migration

If you modify the models, you may need to delete the existing database file (`timetable.db`) to recreate it with the new schema.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed (`pip install -r requirements.txt`)
2. **File Upload Issues**: Check that the `uploads/` directory has write permissions
3. **Database Issues**: Delete `timetable.db` to recreate the database with sample data
4. **NetworkX/Matplotlib Issues**: Install with `pip install networkx matplotlib` for scheduling and graph features

### Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **NetworkX**: Graph algorithms for scheduling
- **Matplotlib**: Graph visualization
- **Werkzeug**: File upload handling

## License

This project is for educational purposes.
