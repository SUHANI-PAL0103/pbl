import os
import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from werkzeug.utils import secure_filename
from models import db, Course, CourseMaterial, Activity

materials_bp = Blueprint('materials', __name__)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@materials_bp.route('/course_materials/<int:course_id>', methods=['GET', 'POST'])
def course_materials(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        material_name = request.form['material_name']
        material_description = request.form.get('material_description', '')
        
        # Handle file upload
        if 'material_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['material_file']
        if not file.filename:  # Handles None or empty string for filename
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        # If we reach here, file.filename is a non-empty string.
        # A FileStorage object ('file') is always truthy if it exists.
        if allowed_file(file.filename, {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx'}):
            # Save the file
            filename = secure_filename(f"{course.code}_{material_name}_{int(time.time())}.{file.filename.rsplit('.', 1)[1].lower()}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Create material record
            material = CourseMaterial()
            material.course_id = course.id
            material.name = material_name
            material.description = material_description
            material.file_path = filename
            db.session.add(material)
            
            # Log activity
            activity = Activity()
            activity.description = f"Added material '{material_name}' to course {course.code}"
            activity.icon = "fas fa-file-pdf"
            db.session.add(activity)
            
            db.session.commit()
            flash('Course material uploaded successfully!', 'success')
            return redirect(url_for('materials.course_materials', course_id=course.id))
        else:
            flash('Invalid file type. Allowed types: PDF, DOC, DOCX, TXT, PPT, PPTX', 'danger')
    
    materials = CourseMaterial.query.filter_by(course_id=course.id).all()
    return render_template('course_materials.html', course=course, materials=materials)

@materials_bp.route('/download_material/<int:material_id>')
def download_material(material_id):
    material = CourseMaterial.query.get_or_404(material_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], material.file_path)
    
    if not os.path.exists(file_path):
        flash('File not found on server!', 'danger')
        return redirect(url_for('materials.course_materials', course_id=material.course_id))
    
    # Log activity
    # Log activity
    activity = Activity()
    activity.description = f"Downloaded material '{material.name}' from course {material.course.code}"
    activity.icon = "fas fa-download"
    db.session.add(activity)
    db.session.commit()
    return send_file(file_path, as_attachment=True, download_name=f"{material.name}.{material.file_path.split('.')[-1]}")

@materials_bp.route('/delete_material/<int:material_id>', methods=['POST'])
def delete_material(material_id):
    material = CourseMaterial.query.get_or_404(material_id)
    course_id = material.course_id
    
    # Delete the file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], material.file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass  # Continue even if file deletion fails
    
    # Store details for logging before deleting the material object,
    # as accessing them after deletion might lead to errors.
    material_name_for_log = material.name
    course_code_for_log = material.course.code

    # Delete the material record from the database
    db.session.delete(material)
    
    # Log activity
    activity = Activity()
    activity.description = f"Deleted material '{material_name_for_log}' from course {course_code_for_log}"
    activity.icon = "fas fa-trash"
    db.session.add(activity)
    
    # Commit the session to save changes (deletion of material and addition of activity log)
    db.session.commit()
    
    flash('Course material deleted successfully!', 'success')
    return redirect(url_for('materials.course_materials', course_id=course_id))
