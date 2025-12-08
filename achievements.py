from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.achievement import Achievement, UserAchievement
from app.models.user import User

achievements_bp = Blueprint('achievements', __name__)

@achievements_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_achievements():
    """Get all available achievements with user's unlock status"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get all achievements
        all_achievements = Achievement.query.all()
        
        # Get user's unlocked achievements
        unlocked = UserAchievement.query.filter_by(user_id=user_id).all()
        unlocked_ids = [ua.achievement_id for ua in unlocked]
        
        # Build response
        achievements_list = []
        for achievement in all_achievements:
            ach_dict = achievement.to_dict()
            ach_dict['unlocked'] = achievement.achievement_id in unlocked_ids
            
            # Add unlock date if unlocked
            if ach_dict['unlocked']:
                user_ach = next(ua for ua in unlocked if ua.achievement_id == achievement.achievement_id)
                ach_dict['unlocked_at'] = user_ach.unlocked_at.isoformat()
            
            achievements_list.append(ach_dict)
        
        # Calculate progress
        total = len(all_achievements)
        unlocked_count = len(unlocked_ids)
        progress = (unlocked_count / total * 100) if total > 0 else 0
        
        return jsonify({
            'achievements': achievements_list,
            'total': total,
            'unlocked': unlocked_count,
            'progress': round(progress, 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@achievements_bp.route('/unlocked', methods=['GET'])
@jwt_required()
def get_unlocked_achievements():
    """Get user's unlocked achievements only"""
    try:
        user_id = int(get_jwt_identity())
        
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).order_by(
            UserAchievement.unlocked_at.desc()
        ).all()
        
        return jsonify({
            'achievements': [ua.to_dict() for ua in user_achievements],
            'total': len(user_achievements)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@achievements_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_achievement_progress():
    """Get progress towards unlocking achievements"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user stats
        from app.models.task import Task
        completed_tasks = Task.query.filter_by(user_id=user_id, status='Completed').count()
        
        # Get unlocked achievement IDs
        unlocked_ids = [ua.achievement_id for ua in user.achievements.all()]
        
        # Get all achievements
        all_achievements = Achievement.query.all()
        
        progress_list = []
        for achievement in all_achievements:
            if achievement.achievement_id in unlocked_ids:
                continue  # Skip already unlocked
            
            # Calculate progress based on requirement type
            current_value = 0
            if achievement.requirement_type == 'tasks_completed':
                current_value = completed_tasks
            elif achievement.requirement_type == 'streak':
                current_value = user.current_streak
            elif achievement.requirement_type == 'level':
                current_value = user.level
            elif achievement.requirement_type == 'evolution_stage':
                current_value = user.pet.evolution_stage if user.pet else 0
            
            progress_pct = min(100, (current_value / achievement.requirement_value * 100)) if achievement.requirement_value > 0 else 0
            
            progress_list.append({
                'achievement': achievement.to_dict(),
                'current_value': current_value,
                'required_value': achievement.requirement_value,
                'progress': round(progress_pct, 2)
            })
        
        return jsonify({
            'in_progress': progress_list
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500