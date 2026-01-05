from flask import Flask
from config import Config
from database.db import init_db
from routes.auth import auth_bp
from routes.views import views_bp
from routes.api import api_bp
from automation.queue_manager import QueueManager
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Validate configuration
try:
    Config.validate()
    print("✓ Configuration validated")
except Exception as e:
    print(f"✗ Configuration error: {str(e)}")
    exit(1)

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(views_bp)
app.register_blueprint(api_bp)

# Initialize queue manager with app context
queue_manager = QueueManager(app)

@app.before_request
def before_first_request():
    """Initialize queue manager on first request"""
    if not queue_manager.running:
        queue_manager.start()

@app.route('/health')
def health():
    """Health check endpoint"""
    status = queue_manager.get_status()
    return {
        'status': 'healthy',
        'queue': status
    }

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(Config.COOKIES_STORE, exist_ok=True)
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    print("\n" + "="*60)
    print(" 🚀 TUBIFY - YouTube Traffic Generator")
    print("="*60)
    print(f" Username: {Config.ADMIN_USERNAME}")
    print(f" Max Concurrent Sessions: {Config.MAX_CONCURRENT_SESSIONS}")
    print(f" Watch Duration: {Config.WATCH_DURATION}s")
    print("="*60 + "\n")
    
    # Start Flask app
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000, use_reloader=False)

