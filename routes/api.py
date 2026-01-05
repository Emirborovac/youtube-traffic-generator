from flask import Blueprint, request, jsonify
from routes.auth import login_required
from database.db import db
from database.models import Video, Session
from datetime import datetime
import re

api_bp = Blueprint('api', __name__, url_prefix='/api')

def validate_youtube_url(url):
    """Validate if URL is a YouTube link"""
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/',
        r'youtube\.com/watch\?v=',
        r'youtube\.com/shorts/',
        r'youtu\.be/'
    ]
    
    for pattern in youtube_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

def detect_video_type(url):
    """Detect if URL is video or shorts"""
    if '/shorts/' in url.lower():
        return 'shorts'
    return 'video'

@api_bp.route('/videos', methods=['GET'])
@login_required
def get_videos():
    """Get all videos"""
    status_filter = request.args.get('status')
    search = request.args.get('search')
    
    query = Video.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.filter(Video.url.contains(search))
    
    videos = query.order_by(Video.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'videos': [video.to_dict() for video in videos]
    })

@api_bp.route('/videos', methods=['POST'])
@login_required
def create_video():
    """Add new video"""
    data = request.get_json()
    
    url = data.get('url', '').strip()
    video_type = data.get('video_type', '').strip()
    views_requested = data.get('views_requested', 0)
    
    # Validation
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    if not validate_youtube_url(url):
        return jsonify({'success': False, 'error': 'Invalid YouTube URL'}), 400
    
    if video_type not in ['video', 'shorts']:
        # Auto-detect if not provided
        video_type = detect_video_type(url)
    
    if views_requested < 1 or views_requested > 1000:
        return jsonify({'success': False, 'error': 'Views must be between 1 and 1000'}), 400
    
    # Create video
    video = Video(
        url=url,
        video_type=video_type,
        views_requested=views_requested,
        status='pending'
    )
    
    db.session.add(video)
    db.session.commit()
    
    # Create sessions for each view
    for i in range(views_requested):
        session_obj = Session(
            video_id=video.id,
            status='pending'
        )
        db.session.add(session_obj)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Video added successfully with {views_requested} views',
        'video': video.to_dict()
    })

@api_bp.route('/videos/<int:video_id>/status', methods=['PATCH'])
@login_required
def update_video_status(video_id):
    """Update video status (activate/pause/stop)"""
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['active', 'paused', 'stopped']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    video = Video.query.get_or_404(video_id)
    video.status = new_status
    video.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Video status updated to {new_status}',
        'video': video.to_dict()
    })

@api_bp.route('/videos/<int:video_id>', methods=['DELETE'])
@login_required
def delete_video(video_id):
    """Delete video"""
    video = Video.query.get_or_404(video_id)
    
    db.session.delete(video)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Video deleted successfully'
    })

@api_bp.route('/videos/<int:video_id>/sessions', methods=['GET'])
@login_required
def get_video_sessions(video_id):
    """Get sessions for a video"""
    video = Video.query.get_or_404(video_id)
    sessions = Session.query.filter_by(video_id=video_id).all()
    
    return jsonify({
        'success': True,
        'video': video.to_dict(),
        'sessions': [session.to_dict() for session in sessions]
    })

@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get dashboard statistics"""
    total_videos = Video.query.count()
    active_videos = Video.query.filter_by(status='active').count()
    completed_videos = Video.query.filter_by(status='completed').count()
    
    total_sessions = Session.query.count()
    running_sessions = Session.query.filter_by(status='running').count()
    pending_sessions = Session.query.filter_by(status='pending').count()
    successful_sessions = Session.query.filter_by(status='success').count()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_videos': total_videos,
            'active_videos': active_videos,
            'completed_videos': completed_videos,
            'total_sessions': total_sessions,
            'running_sessions': running_sessions,
            'pending_sessions': pending_sessions,
            'successful_sessions': successful_sessions
        }
    })

