import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for many-to-many relationship between students and courses
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class Course(db.Model):
    __tablename__ = 'course'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slot.id'))
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))
    
    # Relationships
    instructor = db.relationship('Instructor', back_populates='courses')
    time_slot = db.relationship('TimeSlot', back_populates='courses')
    classroom = db.relationship('Classroom', back_populates='courses')
    students = db.relationship('Student', secondary='enrollments', back_populates='courses')
    materials = db.relationship('CourseMaterial', back_populates='course', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'

class Instructor(db.Model):
    __tablename__ = 'instructor'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100))
    
    # Relationships
    courses = db.relationship('Course', back_populates='instructor')
    
    def __repr__(self):
        return f'<Instructor {self.name}>'

class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relationships
    courses = db.relationship('Course', secondary='enrollments', back_populates='students')
    
    def __repr__(self):
        return f'<Student {self.name}>'

class Classroom(db.Model):
    __tablename__ = 'classroom'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    courses = db.relationship('Course', back_populates='classroom')
    
    def __repr__(self):
        return f'<Classroom {self.name} (Capacity: {self.capacity})>'

class TimeSlot(db.Model):
    __tablename__ = 'time_slot'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    # Relationships
    courses = db.relationship('Course', back_populates='time_slot')
    
    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    def __repr__(self):
        return f'<TimeSlot {self.__str__()}>'

class CourseMaterial(db.Model):
    __tablename__ = 'course_material'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.datetime.now)
    
    # Relationships
    course = db.relationship('Course', back_populates='materials')
    
    def __repr__(self):
        return f'<CourseMaterial {self.name} for {self.course.code}>'

class Activity(db.Model):
    __tablename__ = 'activity'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    user = db.Column(db.String(100), default="System")
    icon = db.Column(db.String(50), default="fas fa-info-circle")
    
    @property
    def time(self):
        return self.timestamp.strftime("%m/%d/%Y, %H:%M")
    
    def __repr__(self):
        return f'<Activity {self.description}>'
