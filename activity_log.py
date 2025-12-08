from datetime import datetime
from app import db

class ActivityLog(db.Model):
    """Activity log for tracking user actions"""
    __tablename__ = 'activity_log'
    
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    activity_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    xp_earned = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def log_activity(user_id, activity_type, description, xp_earned=0):
        """Create a new activity log entry"""
        log = ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            xp_earned=xp_earned
        )
        db.session.add(log)
        return log
    
    def to_dict(self):
        """Convert activity log to dictionary"""
        return {
            'log_id': self.log_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'xp_earned': self.xp_earned,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<ActivityLog {self.activity_type} at {self.timestamp}>'
        