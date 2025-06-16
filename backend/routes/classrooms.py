from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Classroom, Activity

classrooms_bp = Blueprint('classrooms', __name__)

@classrooms_bp.route('/classrooms')
def classrooms():
    classrooms = Classroom.query.all()
    return render_template('classrooms.html', classrooms=classrooms)

@classrooms_bp.route('/add_classroom', methods=['GET', 'POST'])
def add_classroom():
    if request.method == 'POST':
        name = request.form['name']
        capacity = int(request.form['capacity'])
        
        # Check if classroom name already exists
        existing_classroom = Classroom.query.filter_by(name=name).first()
        if existing_classroom:
            flash('Classroom name already exists!', 'danger')
            return redirect(url_for('classrooms.add_classroom'))
        
        classroom = Classroom()
        classroom.name = name
        classroom.capacity = capacity
        db.session.add(classroom)
        
        # Log activity
        activity = Activity()
        activity.description = f"Added new classroom: {name} (Capacity: {capacity})"
        activity.icon = "fas fa-door-open"
        db.session.add(activity)
        
        db.session.commit()
        flash('Classroom added successfully!', 'success')
        return redirect(url_for('classrooms.classrooms'))
    
    return render_template('add_classroom.html')

@classrooms_bp.route('/edit_classroom/<int:classroom_id>', methods=['GET', 'POST'])
def edit_classroom(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    
    if request.method == 'POST':
        name = request.form['name']
        capacity = int(request.form['capacity'])
          # Check if classroom name already exists (excluding current classroom)
        existing_classroom = Classroom.query.filter(Classroom.name == name, Classroom.id != classroom_id).first()
        if existing_classroom:
            flash('Classroom name already exists!', 'danger')
            return redirect(url_for('classrooms.edit_classroom', classroom_id=classroom_id))
        
        classroom.name = name
        classroom.capacity = capacity
        
        # Log activity
        activity = Activity()
        activity.description = f"Updated classroom: {classroom.name}"
        activity.icon = "fas fa-edit"
        db.session.add(activity)
        
        db.session.commit()
        flash('Classroom updated successfully!', 'success')
        return redirect(url_for('classrooms.classrooms'))
    
    return render_template('edit_classroom.html', classroom=classroom)

@classrooms_bp.route('/delete_classroom/<int:classroom_id>', methods=['POST'])
def delete_classroom(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    
    # Check if classroom has assigned courses
    if classroom.courses:
        flash('Cannot delete classroom with assigned courses!', 'danger')
        return redirect(url_for('classrooms.classrooms'))
    
    # Log activity
    activity = Activity()
    activity.description = f"Deleted classroom: {classroom.name}"
    activity.icon = "fas fa-trash"
    db.session.add(activity)
    
    db.session.delete(classroom)
    db.session.commit()
    flash('Classroom deleted successfully!', 'success')
    return redirect(url_for('classrooms.classrooms'))
