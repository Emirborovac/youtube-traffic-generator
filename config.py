class Config:
    """Application configuration"""
    
    # Authentication - HARDCODED
    ADMIN_USERNAME = 'tubify@gmail.com'
    ADMIN_PASSWORD = 'Tubify@2026'
    
    # Flask
    SECRET_KEY = 'tubify-secret-key-change-in-production'
    DEBUG = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tubify.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Proxy - HARDCODED
    PROXY_SERVER = 'http://dc.decodo.com:10000'
    PROXY_USERNAME = 'sp3vk5ed5y'
    PROXY_PASSWORD = 'a7ExhnYi~Mu8Cfd36t'
    
    # Automation
    MAX_CONCURRENT_SESSIONS = 10
    WATCH_DURATION = 300  # 5 minutes
    
    # Paths
    COOKIES_STORE = 'cookies_store'
    LOGS_DIR = 'logs'
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        return True

