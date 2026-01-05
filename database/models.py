from datetime import datetime
from database.db import db

class Video(db.Model):
    """Video model - represents a YouTube video/shorts to process"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    video_type = db.Column(db.String(10), nullable=False)  # 'video' or 'shorts'
    views_requested = db.Column(db.Integer, nullable=False)
    views_completed = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, active, paused, stopped, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    sessions = db.relationship('Session', backref='video', lazy=True, cascade='all, delete-orphan')
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.views_requested == 0:
            return 0
        return int((self.views_completed / self.views_requested) * 100)
    
    @property
    def active_sessions_count(self):
        """Count active sessions"""
        return Session.query.filter_by(
            video_id=self.id,
            status='running'
        ).count()
    
    def to_dict(self):
        """Convert to dictionary for API"""
        return {
            'id': self.id,
            'url': self.url,
            'video_type': self.video_type,
            'views_requested': self.views_requested,
            'views_completed': self.views_completed,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'active_sessions': self.active_sessions_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Session(db.Model):
    """Session model - represents a single view session"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    cookie_file = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, running, success, failed
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    logs = db.Column(db.Text)  # JSON string of step logs
    
    def to_dict(self):
        """Convert to dictionary for API"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'cookie_file': self.cookie_file,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'logs': self.logs
        }


