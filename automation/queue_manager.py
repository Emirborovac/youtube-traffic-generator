from datetime import datetime
from database.db import db
from database.models import Video, Session
from automation.cookie_parser import get_available_cookies
from automation.video_handler import VideoHandler
from automation.shorts_handler import ShortsHandler
from config import Config
import json
import threading
import time

class QueueManager:
    """Manages video processing queue with max 10 concurrent sessions"""
    
    def __init__(self, app=None):
        self.running = False
        self.active_sessions = {}  # {session_id: thread}
        self.lock = threading.Lock()
        self.app = app
    
    def start(self):
        """Start queue manager"""
        self.running = True
        print("✓ Queue manager started")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_queue, daemon=True)
        monitor_thread.start()
    
    def stop(self):
        """Stop queue manager"""
        self.running = False
        print("✓ Queue manager stopped")
    
    def _monitor_queue(self):
        """Monitor queue and process sessions"""
        while self.running:
            try:
                # Check active sessions count
                with self.lock:
                    active_count = len(self.active_sessions)
                
                # If we have capacity, start new sessions
                if active_count < Config.MAX_CONCURRENT_SESSIONS:
                    available_slots = Config.MAX_CONCURRENT_SESSIONS - active_count
                    self._start_pending_sessions(available_slots)
                
                # Clean up finished threads
                self._cleanup_finished_sessions()
                
                # Sleep before next check
                time.sleep(2)
                
            except Exception as e:
                print(f"Error in queue monitor: {str(e)}")
                time.sleep(5)
    
    def _start_pending_sessions(self, count):
        """Start pending sessions up to count"""
        if not self.app:
            return
            
        try:
            with self.app.app_context():
                # Get available cookies
                available_cookies = get_available_cookies()
                
                if not available_cookies:
                    print("⚠ No cookie files found in cookies_store/")
                    return
                
                # Get pending sessions from active videos
                pending_sessions = (
                    Session.query
                    .join(Video)
                    .filter(
                        Session.status == 'pending',
                        Video.status == 'active'
                    )
                    .limit(count)
                    .all()
                )
                
                if not pending_sessions:
                    return
                
                print(f"→ Starting {len(pending_sessions)} sessions")
                
                if not pending_sessions:
                    return
                
                if not pending_sessions:
                    return
            
                for session in pending_sessions:
                    # Assign cookie (round-robin)
                    cookie_file = available_cookies[session.id % len(available_cookies)]
                    session.cookie_file = cookie_file
                    db.session.commit()
                    
                    # Start session thread
                    thread = threading.Thread(
                        target=self._execute_session,
                        args=(session.id,),
                        daemon=True
                    )
                    
                    with self.lock:
                        self.active_sessions[session.id] = thread
                    
                    thread.start()
                    print(f"✓ Started session {session.id} with cookie {cookie_file}")
                
        except Exception as e:
            print(f"Error starting sessions: {str(e)}")
    
    def _execute_session(self, session_id):
        """Execute a single session"""
        if not self.app:
            return
            
        try:
            # Get session data within app context
            with self.app.app_context():
                session = Session.query.get(session_id)
                if not session:
                    return
                
                video = session.video
                video_url = video.url
                video_type = video.video_type
                cookie_file = session.cookie_file
                
                # Update session status
                session.status = 'running'
                session.started_at = datetime.utcnow()
                db.session.commit()
                
                print(f"→ Executing session {session_id} for {video_type}: {video_url}")
            
            # Execute automation (outside app context with local variables)
            if video_type == 'video':
                handler = VideoHandler(video_url, cookie_file)
            else:
                handler = ShortsHandler(video_url, cookie_file)
            
            success, logs = handler.execute()
            
            # Update database (inside app context)
            with self.app.app_context():
                session = Session.query.get(session_id)
                video = session.video
                
                session.completed_at = datetime.utcnow()
                session.logs = json.dumps(logs)
                
                if success:
                    session.status = 'success'
                    video.views_completed += 1
                    print(f"✓ Session {session_id} completed successfully")
                else:
                    session.status = 'failed'
                    session.error_message = "Automation failed - check logs"
                    print(f"✗ Session {session_id} failed")
                
                # Check if video is completed
                if video.views_completed >= video.views_requested:
                    video.status = 'completed'
                    print(f"✓ Video {video.id} completed all {video.views_requested} views")
                
                video.updated_at = datetime.utcnow()
                db.session.commit()
            
        except Exception as e:
            print(f"Error executing session {session_id}: {str(e)}")
            
            # Update session as failed
            if self.app:
                try:
                    with self.app.app_context():
                        session = Session.query.get(session_id)
                        if session:
                            session.status = 'failed'
                            session.error_message = str(e)
                            session.completed_at = datetime.utcnow()
                            db.session.commit()
                except:
                    pass
        
        finally:
            # Remove from active sessions
            with self.lock:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
    
    def _cleanup_finished_sessions(self):
        """Remove finished threads from active sessions"""
        with self.lock:
            finished = [
                session_id for session_id, thread in self.active_sessions.items()
                if not thread.is_alive()
            ]
            
            for session_id in finished:
                del self.active_sessions[session_id]
    
    def get_status(self):
        """Get queue manager status"""
        with self.lock:
            active_count = len(self.active_sessions)
            active_session_ids = list(self.active_sessions.keys())
        
        pending_count = Session.query.filter_by(status='pending').count()
        
        return {
            'active_sessions': active_count,
            'pending_sessions': pending_count,
            'max_concurrent': Config.MAX_CONCURRENT_SESSIONS,
            'active_session_ids': active_session_ids
        }

