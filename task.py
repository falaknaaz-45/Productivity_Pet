from datetime import datetime
from app import db
from config import Config

class Task(db.Model):
    """Task model for user to-do items"""
    __tablename__ = 'tasks'
    
    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(20), default='Pending')
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    points_value = db.Column(db.Integer)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50))
    
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)
        # Auto-calculate points if not provided
        if self.points_value is None:
            self.points_value = self.calculate_points()
    
    def calculate_points(self):
        """Calculate points based on priority"""
        priority_points = {
            'Low': Config.POINTS_LOW_PRIORITY,
            'Medium': Config.POINTS_MEDIUM_PRIORITY,
            'High': Config.POINTS_HIGH_PRIORITY
        }
        return priority_points.get(self.priority, Config.POINTS_MEDIUM_PRIORITY)
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.deadline and self.status != 'Completed':
            return datetime.utcnow() > self.deadline
        return False
    
    def mark_complete(self):
        """Mark task as complete and return XP earned"""
        if self.status == 'Completed':
            return 0  # Already completed
        
        self.status = 'Completed'
        self.completed_at = datetime.utcnow()
        
        # Bonus points for completing before deadline
        bonus = 0
        if self.deadline and self.completed_at < self.deadline:
            days_early = (self.deadline - self.completed_at).days
            if days_early >= 2:
                bonus = 5  # Bonus for completing 2+ days early
        
        return self.points_value + bonus
    
    def days_until_deadline(self):
        """Calculate days remaining until deadline"""
        if self.deadline:
            delta = self.deadline - datetime.utcnow()
            return delta.days
        return None
    
    def get_priority_color(self):
        """Get color code for priority"""
        colors = {
            'Low': 'green',
            'Medium': 'orange',
            'High': 'red'
        }
        return colors.get(self.priority, 'gray')
    
    def to_dict(self):
        """Convert task object to dictionary"""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'points_value': self.points_value,
            'is_overdue': self.is_overdue(),
            'days_until_deadline': self.days_until_deadline(),
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern
        }
    
    def __repr__(self):
        return f'<Task {self.title} ({self.priority})>'
        