import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, TimeSlot, Activity

timeslots_bp = Blueprint('timeslots', __name__)

@timeslots_bp.route('/timeslots')
def timeslots():
    timeslots = TimeSlot.query.order_by(TimeSlot.day, TimeSlot.start_time).all()
    return render_template('timeslots.html', timeslots=timeslots)

@timeslots_bp.route('/add_timeslot', methods=['GET', 'POST'])
def add_timeslot():
    if request.method == 'POST':
        day = request.form['day']
        start_time = datetime.datetime.strptime(request.form['start_time'], '%H:%M').time()
        end_time = datetime.datetime.strptime(request.form['end_time'], '%H:%M').time()
        
        # Check if timeslot already exists
        existing_timeslot = TimeSlot.query.filter_by(
            day=day,
            start_time=start_time,
            end_time=end_time
        ).first()
        if existing_timeslot:
            flash('This time slot already exists!', 'danger')
            return redirect(url_for('timeslots.add_timeslot'))
        
        # Validate that start time is before end time
        if start_time >= end_time:
            flash('Start time must be before end time!', 'danger')
            return redirect(url_for('timeslots.add_timeslot'))
        
        timeslot = TimeSlot()
        timeslot.day = day
        timeslot.start_time = start_time
        timeslot.end_time = end_time
        db.session.add(timeslot)
        
        # Log activity
        activity = Activity()
        activity.description = f"Added new time slot: {day} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        activity.icon = "fas fa-clock"
        db.session.add(activity)
        
        db.session.commit()
        flash('Time slot added successfully!', 'success')
        return redirect(url_for('timeslots.timeslots'))
    
    return render_template('add_timeslot.html')

@timeslots_bp.route('/delete_timeslot/<int:timeslot_id>', methods=['POST'])
def delete_timeslot(timeslot_id):
    timeslot = TimeSlot.query.get_or_404(timeslot_id)
    
    # Check if timeslot has assigned courses
    if timeslot.courses:
        flash('Cannot delete time slot with assigned courses!', 'danger')
        return redirect(url_for('timeslots.timeslots'))
    
    # Log activity
    activity = Activity()
    activity.description = f"Deleted time slot: {timeslot}"
    activity.icon = "fas fa-trash"
    db.session.add(activity)
    
    db.session.delete(timeslot)
    db.session.commit()
    flash('Time slot deleted successfully!', 'success')
    return redirect(url_for('timeslots.timeslots'))

@timeslots_bp.route('/edit_timeslot/<int:timeslot_id>', methods=['GET', 'POST'])
def edit_timeslot(timeslot_id):
    timeslot = TimeSlot.query.get_or_404(timeslot_id)
    
    if request.method == 'POST':
        day = request.form['day']
        start_time = datetime.datetime.strptime(request.form['start_time'], '%H:%M').time()
        end_time = datetime.datetime.strptime(request.form['end_time'], '%H:%M').time()
        
        # Validate that start time is before end time
        if start_time >= end_time:
            flash('Start time must be before end time!', 'danger')
            return redirect(url_for('timeslots.edit_timeslot', timeslot_id=timeslot_id))
        
        # Check if another timeslot with same details exists (excluding current one)
        existing_timeslot = TimeSlot.query.filter(
            TimeSlot.id != timeslot_id,
            TimeSlot.day == day,
            TimeSlot.start_time == start_time,
            TimeSlot.end_time == end_time
        ).first()
        if existing_timeslot:
            flash('Another time slot with these details already exists!', 'danger')
            return redirect(url_for('timeslots.edit_timeslot', timeslot_id=timeslot_id))
        
        # Update timeslot
        old_description = str(timeslot)
        timeslot.day = day
        timeslot.start_time = start_time
        timeslot.end_time = end_time
        
        # Log activity
        activity = Activity()
        activity.description = f"Updated time slot from {old_description} to {timeslot}"
        activity.icon = "fas fa-edit"
        db.session.add(activity)
        
        db.session.commit()
        flash('Time slot updated successfully!', 'success')
        return redirect(url_for('timeslots.timeslots'))
    
    return render_template('edit_timeslot.html', timeslot=timeslot)
