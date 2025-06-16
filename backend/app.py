import os
import datetime
from flask import Flask, render_template
from config import config

def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config[config_name])
    
    # Initialize database
    from models import db
    db.init_app(app)
    
    # Import route blueprints
    from routes.dashboard import dashboard_bp
    from routes.courses import courses_bp
    from routes.instructors import instructors_bp
    from routes.students import students_bp
    from routes.classrooms import classrooms_bp
    from routes.timeslots import timeslots_bp
    from routes.scheduler import scheduler_bp
    from routes.conflicts import conflicts_bp
    from routes.materials import materials_bp
    from routes.data_import import data_import_bp
    
    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(instructors_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(classrooms_bp)
    app.register_blueprint(timeslots_bp)
    app.register_blueprint(scheduler_bp)
    app.register_blueprint(conflicts_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(data_import_bp)
    
    # Context processor for templates
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.datetime.now().year}
    
    # User guide route
    @app.route('/user_guide')
    def user_guide():
        return render_template('user_guide.html')
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Ensure the uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        from models import db, TimeSlot
        db.create_all()
        
        # Create sample data if database is empty
        if not TimeSlot.query.first():
            from utils.sample_data import create_sample_data
            create_sample_data(db)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
