from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from config import Config

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    total_xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_task_date = db.Column(db.Date)
    
    # Relationships
    pet = db.relationship('Pet', backref='owner', uselist=False, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def add_xp(self, points):
        """Add XP and check for level up"""
        self.total_xp += points
        new_level = self.calculate_level()
        
        leveled_up = False
        if new_level > self.level:
            self.level = new_level
            leveled_up = True
        
        return leveled_up
    
    def calculate_level(self):
        """Calculate level based on total XP"""
        for level in sorted(Config.LEVEL_THRESHOLDS.keys(), reverse=True):
            if self.total_xp >= Config.LEVEL_THRESHOLDS[level]:
                return level
        return 1
    
    def update_streak(self):
        """Update daily streak counter"""
        today = datetime.utcnow().date()
        
        if self.last_task_date is None:
            # First task ever
            self.current_streak = 1
            self.last_task_date = today
        elif self.last_task_date == today:
            # Already completed task today
            pass
        elif (today - self.last_task_date).days == 1:
            # Consecutive day
            self.current_streak += 1
            self.last_task_date = today
            
            # Update longest streak
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            # Streak broken
            self.current_streak = 1
            self.last_task_date = today
    
    def xp_to_next_level(self):
        """Calculate XP needed for next level"""
        next_level = self.level + 1
        if next_level in Config.LEVEL_THRESHOLDS:
            return Config.LEVEL_THRESHOLDS[next_level] - self.total_xp
        return 0
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_xp': self.total_xp,
            'level': self.level,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'xp_to_next_level': self.xp_to_next_level()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
        