from datetime import datetime
from app import db

class Achievement(db.Model):
    """Achievement definition model"""
    __tablename__ = 'achievements'
    
    achievement_id = db.Column(db.Integer, primary_key=True)
    achievement_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    badge_icon = db.Column(db.String(100))
    requirement_type = db.Column(db.String(50))
    requirement_value = db.Column(db.Integer)
    xp_reward = db.Column(db.Integer, default=50)
    
    # Relationship
    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy='dynamic')
    
    @staticmethod
    def initialize_achievements():
        """Create default achievements if they don't exist"""
        default_achievements = [
            {
                'achievement_name': 'First Steps',
                'description': 'Complete your first task',
                'badge_icon': '🎯',
                'requirement_type': 'tasks_completed',
                'requirement_value': 1,
                'xp_reward': 10
            },
            {
                'achievement_name': 'Task Master',
                'description': 'Complete 10 tasks',
                'badge_icon': '⭐',
                'requirement_type': 'tasks_completed',
                'requirement_value': 10,
                'xp_reward': 50
            },
            {
                'achievement_name': 'Century Club',
                'description': 'Complete 100 tasks',
                'badge_icon': '💯',
                'requirement_type': 'tasks_completed',
                'requirement_value': 100,
                'xp_reward': 500
            },
            {
                'achievement_name': 'Week Warrior',
                'description': 'Maintain a 7-day streak',
                'badge_icon': '🔥',
                'requirement_type': 'streak',
                'requirement_value': 7,
                'xp_reward': 75
            },
            {
                'achievement_name': 'Month Master',
                'description': 'Maintain a 30-day streak',
                'badge_icon': '🏆',
                'requirement_type': 'streak',
                'requirement_value': 30,
                'xp_reward': 300
            },
            {
                'achievement_name': 'Level 5',
                'description': 'Reach level 5',
                'badge_icon': '🎖️',
                'requirement_type': 'level',
                'requirement_value': 5,
                'xp_reward': 100
            },
            {
                'achievement_name': 'Level 10',
                'description': 'Reach level 10',
                'badge_icon': '👑',
                'requirement_type': 'level',
                'requirement_value': 10,
                'xp_reward': 250
            },
            {
                'achievement_name': 'Pet Caretaker',
                'description': 'Feed your pet 10 times',
                'badge_icon': '🍖',
                'requirement_type': 'pet_fed',
                'requirement_value': 10,
                'xp_reward': 50
            },
            {
                'achievement_name': 'Evolution Master',
                'description': 'Evolve your pet to final stage',
                'badge_icon': '🐉',
                'requirement_type': 'evolution_stage',
                'requirement_value': 5,
                'xp_reward': 500
            },
            {
                'achievement_name': 'Early Bird',
                'description': 'Complete a task 3+ days before deadline',
                'badge_icon': '🐦',
                'requirement_type': 'early_completion',
                'requirement_value': 1,
                'xp_reward': 25
            }
        ]
        
        for ach_data in default_achievements:
            # Check if achievement already exists
            existing = Achievement.query.filter_by(
                achievement_name=ach_data['achievement_name']
            ).first()
            
            if not existing:
                achievement = Achievement(**ach_data)
                db.session.add(achievement)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing achievements: {e}")
    
    def to_dict(self):
        """Convert achievement to dictionary"""
        return {
            'achievement_id': self.achievement_id,
            'achievement_name': self.achievement_name,
            'description': self.description,
            'badge_icon': self.badge_icon,
            'requirement_type': self.requirement_type,
            'requirement_value': self.requirement_value,
            'xp_reward': self.xp_reward
        }
    
    def __repr__(self):
        return f'<Achievement {self.achievement_name}>'


class UserAchievement(db.Model):
    """User achievement unlock tracking"""
    __tablename__ = 'user_achievements'
    
    user_achievement_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.achievement_id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert user achievement to dictionary"""
        return {
            'user_achievement_id': self.user_achievement_id,
            'achievement': self.achievement.to_dict(),
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None
        }
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id}:{self.achievement_id}>'
        