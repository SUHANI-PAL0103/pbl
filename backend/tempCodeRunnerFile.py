

def main():
    """Main function to start the application"""
    # Create the Flask app
    app = create_app('development')
    
    # Ensure the uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create database tables if they don't exist
    with app.app_context():