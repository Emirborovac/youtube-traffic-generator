from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Import models
        from database.models import Video, Session
        
        # Create tables
        db.create_all()
        
        print("✓ Database initialized successfully")


