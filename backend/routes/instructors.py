from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Instructor, Activity

instructors_bp = Blueprint('instructors', __name__)

@instructors_bp.route('/instructors')
def instructors():
    instructors = Instructor.query.all()
    return render_template('instructors.html', instructors=instructors)

@instructors_bp.route('/add_instructor', methods=['GET', 'POST'])
def add_instructor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form.get('department', '')
        
        # Check if instructor email already exists
        existing_instructor = Instructor.query.filter_by(email=email).first()
        if existing_instructor:
            flash('Instructor email already exists!', 'danger')
            return redirect(url_for('instructors.add_instructor'))
        
        instructor = Instructor()
        instructor.name = name
        instructor.email = email
        instructor.department = department
        db.session.add(instructor)
        
        # Log activity
        activity = Activity()
        activity.description = f"Added new instructor: {name}"
        activity.icon = "fas fa-chalkboard-teacher"
        db.session.add(activity)
        
        db.session.commit()
        flash('Instructor added successfully!', 'success')
        return redirect(url_for('instructors.instructors'))
    
    return render_template('add_instructor.html')

@instructors_bp.route('/edit_instructor/<int:instructor_id>', methods=['GET', 'POST'])
def edit_instructor(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form.get('department', '')
          # Check if instructor email already exists (excluding current instructor)
        existing_instructor = Instructor.query.filter(Instructor.email == email, Instructor.id != instructor_id).first()
        if existing_instructor:
            flash('Instructor email already exists!', 'danger')
            return redirect(url_for('instructors.edit_instructor', instructor_id=instructor_id))
        
        instructor.name = name
        instructor.email = email
        instructor.department = department
        
        # Log activity
        activity = Activity()
        activity.description = f"Updated instructor: {instructor.name}"
        activity.icon = "fas fa-edit"
        db.session.add(activity)
        
        db.session.commit()
        flash('Instructor updated successfully!', 'success')
        return redirect(url_for('instructors.instructors'))
    
    return render_template('edit_instructor.html', instructor=instructor)

@instructors_bp.route('/delete_instructor/<int:instructor_id>', methods=['POST'])
def delete_instructor(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    
    # Check if instructor has assigned courses
    if instructor.courses:
        flash('Cannot delete instructor with assigned courses!', 'danger')
        return redirect(url_for('instructors.instructors'))
    
    # Log activity
    activity = Activity()
    activity.description = f"Deleted instructor: {instructor.name}"
    activity.icon = "fas fa-trash"
    db.session.add(activity)
    
    db.session.delete(instructor)
    db.session.commit()
    flash('Instructor deleted successfully!', 'success')
    return redirect(url_for('instructors.instructors'))
