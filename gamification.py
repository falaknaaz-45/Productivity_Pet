from app import db
from app.models.achievement import Achievement, UserAchievement
from app.models.activity_log import ActivityLog
from app.models.task import Task
from config import Config

class GamificationEngine:
    """Handles all gamification logic"""
    
    def process_task_completion(self, user, task, xp_earned):
        """Process task completion: award XP, update pet, check achievements"""
        result = {
            'leveled_up': False,
            'new_level': user.level,
            'pet_status': {},
            'achievements_unlocked': []
        }
        
        # Award XP and check level up
        leveled_up = user.add_xp(xp_earned)
        result['leveled_up'] = leveled_up
        result['new_level'] = user.level
        
        # Update streak
        user.update_streak()
        
        # Update pet stats
        if user.pet:
            user.pet.update_health(Config.HEALTH_INCREASE_ON_TASK)
            user.pet.update_happiness(Config.HAPPINESS_INCREASE_ON_TASK)
            user.pet.update_hunger(5)  # Pet gets a bit hungry
            
            result['pet_status'] = {
                'health': user.pet.health,
                'happiness': user.pet.happiness,
                'hunger': user.pet.hunger,
                'mood': user.pet.get_mood_status()[0]
            }
        
        # Check for new achievements
        new_achievements = self.check_achievements(user)
        result['achievements_unlocked'] = new_achievements
        
        # Log activity
        ActivityLog.log_activity(
            user_id=user.user_id,
            activity_type='task_completed',
            description=f'Completed: {task.title}',
            xp_earned=xp_earned
        )
        
        if leveled_up:
            ActivityLog.log_activity(
                user_id=user.user_id,
                activity_type='level_up',
                description=f'Reached level {user.level}!',
                xp_earned=50
            )
        
        return result
    
    def check_achievements(self, user):
        """Check and unlock new achievements"""
        unlocked_achievements = []
        
        # Get all achievements
        all_achievements = Achievement.query.all()
        
        # Get already unlocked achievement IDs
        unlocked_ids = [ua.achievement_id for ua in user.achievements.all()]
        
        # Get user stats
        completed_tasks = Task.query.filter_by(user_id=user.user_id, status='Completed').count()
        
        for achievement in all_achievements:
            # Skip if already unlocked
            if achievement.achievement_id in unlocked_ids:
                continue
            
            # Check if requirements are met
            requirement_met = False
            
            if achievement.requirement_type == 'tasks_completed':
                requirement_met = completed_tasks >= achievement.requirement_value
            
            elif achievement.requirement_type == 'streak':
                requirement_met = user.current_streak >= achievement.requirement_value
            
            elif achievement.requirement_type == 'level':
                requirement_met = user.level >= achievement.requirement_value
            
            elif achievement.requirement_type == 'evolution_stage':
                if user.pet:
                    requirement_met = user.pet.evolution_stage >= achievement.requirement_value
            
            elif achievement.requirement_type == 'pet_fed':
                # Count pet feeding activities
                feed_count = ActivityLog.query.filter_by(
                    user_id=user.user_id,
                    activity_type='pet_fed'
                ).count()
                requirement_met = feed_count >= achievement.requirement_value
            
            # Unlock achievement
            if requirement_met:
                user_achievement = UserAchievement(
                    user_id=user.user_id,
                    achievement_id=achievement.achievement_id
                )
                db.session.add(user_achievement)
                
                # Award XP reward
                user.add_xp(achievement.xp_reward)
                
                # Log achievement unlock
                ActivityLog.log_activity(
                    user_id=user.user_id,
                    activity_type='achievement_unlocked',
                    description=f'Unlocked: {achievement.achievement_name}',
                    xp_earned=achievement.xp_reward
                )
                
                unlocked_achievements.append(achievement.to_dict())
        
        return unlocked_achievements
    
    def process_overdue_tasks(self, user):
        """Process penalty for overdue tasks"""
        from datetime import datetime
        
        # Find overdue tasks
        overdue_tasks = Task.query.filter(
            Task.user_id == user.user_id,
            Task.status == 'Pending',
            Task.deadline < datetime.utcnow()
        ).all()
        
        if not overdue_tasks:
            return
        
        # Apply penalty to pet
        if user.pet:
            for task in overdue_tasks:
                user.pet.update_health(-Config.HEALTH_DECREASE_ON_OVERDUE)
                user.pet.update_happiness(-Config.HAPPINESS_DECREASE_ON_OVERDUE)
                
                # Log activity
                ActivityLog.log_activity(
                    user_id=user.user_id,
                    activity_type='task_overdue',
                    description=f'Overdue: {task.title} - Pet health decreased'
                )