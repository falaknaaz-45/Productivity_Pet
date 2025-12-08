from datetime import datetime
from app import db
from config import Config

class Pet(db.Model):
    """Pet model representing user's virtual companion"""
    __tablename__ = 'pets'
    
    pet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_name = db.Column(db.String(50), nullable=False)
    species = db.Column(db.String(50), default='Dragon')
    evolution_stage = db.Column(db.Integer, default=1)
    health = db.Column(db.Integer, default=100)
    happiness = db.Column(db.Integer, default=100)
    hunger = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_fed = db.Column(db.DateTime)
    
    def update_health(self, amount):
        """Update pet health within bounds"""
        self.health = max(0, min(Config.MAX_HEALTH, self.health + amount))
    
    def update_happiness(self, amount):
        """Update pet happiness within bounds"""
        self.happiness = max(0, min(Config.MAX_HAPPINESS, self.happiness + amount))
    
    def update_hunger(self, amount):
        """Update pet hunger within bounds"""
        self.hunger = max(0, min(Config.MAX_HUNGER, self.hunger + amount))
    
    def feed_pet(self):
        """Feed the pet, reducing hunger"""
        self.update_hunger(-Config.HUNGER_DECREASE_ON_FEED)
        self.update_happiness(10)
        self.last_fed = datetime.utcnow()
    
    def check_evolution(self):
        """Check if pet should evolve based on user XP"""
        user_xp = self.owner.total_xp
        
        for stage in sorted(Config.EVOLUTION_REQUIREMENTS.keys(), reverse=True):
            if user_xp >= Config.EVOLUTION_REQUIREMENTS[stage]:
                if stage > self.evolution_stage:
                    self.evolution_stage = stage
                    return True, stage
                break
        
        return False, self.evolution_stage
    
    def get_mood_status(self):
        """Return mood emoji based on health and happiness"""
        avg_stat = (self.health + self.happiness) / 2
        
        if avg_stat >= 80:
            return 'happy', '😊'
        elif avg_stat >= 60:
            return 'content', '😐'
        elif avg_stat >= 40:
            return 'sad', '😞'
        elif avg_stat >= 20:
            return 'sick', '😷'
        else:
            return 'critical', '💀'
    
    def get_stage_name(self):
        """Get evolution stage name"""
        stage_names = {
            1: 'Egg',
            2: 'Baby',
            3: 'Teen',
            4: 'Adult',
            5: 'Legendary'
        }
        return stage_names.get(self.evolution_stage, 'Unknown')
    
    def needs_attention(self):
        """Check if pet needs immediate attention"""
        return self.health < 30 or self.happiness < 30 or self.hunger > 70
    
    def get_pet_age_days(self):
        """Calculate pet age in days"""
        if self.created_at:
            return (datetime.utcnow() - self.created_at).days
        return 0
    
    def to_dict(self):
        """Convert pet object to dictionary"""
        mood_status, mood_emoji = self.get_mood_status()
        
        return {
            'pet_id': self.pet_id,
            'pet_name': self.pet_name,
            'species': self.species,
            'evolution_stage': self.evolution_stage,
            'stage_name': self.get_stage_name(),
            'health': self.health,
            'happiness': self.happiness,
            'hunger': self.hunger,
            'mood_status': mood_status,
            'mood_emoji': mood_emoji,
            'needs_attention': self.needs_attention(),
            'age_days': self.get_pet_age_days(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_fed': self.last_fed.isoformat() if self.last_fed else None
        }
    
    def __repr__(self):
        return f'<Pet {self.pet_name} (Stage {self.evolution_stage})>'
        