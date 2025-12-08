from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.pet import Pet
from app.models.activity_log import ActivityLog
from config import Config

pets_bp = Blueprint('pets', __name__)

@pets_bp.route('/', methods=['GET'])
@jwt_required()
def get_pet():
    """Get current user's pet"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or not user.pet:
            return jsonify({'error': 'Pet not found'}), 404
        
        pet = user.pet
        
        # Check for evolution
        evolved, new_stage = pet.check_evolution()
        if evolved:
            db.session.commit()
            
            # Log evolution
            ActivityLog.log_activity(
                user_id=user_id,
                activity_type='pet_evolved',
                description=f'{pet.pet_name} evolved to stage {new_stage}!',
                xp_earned=100
            )
            db.session.commit()
        
        return jsonify({
            'pet': pet.to_dict(),
            'evolved': evolved
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pets_bp.route('/feed', methods=['POST'])
@jwt_required()
def feed_pet():
    """Feed the pet (costs points)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or not user.pet:
            return jsonify({'error': 'Pet not found'}), 404
        
        pet = user.pet
        
        # Check if user has enough XP to feed
        feed_cost = Config.FEED_COST
        if user.total_xp < feed_cost:
            return jsonify({
                'error': f'Not enough XP. Need {feed_cost} XP to feed pet.',
                'current_xp': user.total_xp,
                'required_xp': feed_cost
            }), 400
        
        # Deduct XP and feed pet
        user.total_xp -= feed_cost
        pet.feed_pet()
        
        # Log activity
        ActivityLog.log_activity(
            user_id=user_id,
            activity_type='pet_fed',
            description=f'Fed {pet.pet_name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'message': f'{pet.pet_name} has been fed!',
            'pet': pet.to_dict(),
            'xp_spent': feed_cost,
            'remaining_xp': user.total_xp
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pets_bp.route('/rename', methods=['PUT'])
@jwt_required()
def rename_pet():
    """Rename the pet"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or not user.pet:
            return jsonify({'error': 'Pet not found'}), 404
        
        data = request.get_json()
        
        if 'pet_name' not in data:
            return jsonify({'error': 'pet_name is required'}), 400
        
        new_name = data['pet_name'].strip()
        if not new_name or len(new_name) < 2:
            return jsonify({'error': 'Pet name must be at least 2 characters'}), 400
        
        old_name = user.pet.pet_name
        user.pet.pet_name = new_name
        
        # Log activity
        ActivityLog.log_activity(
            user_id=user_id,
            activity_type='pet_renamed',
            description=f'Renamed pet from {old_name} to {new_name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Pet renamed successfully',
            'pet': user.pet.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pets_bp.route('/evolution', methods=['GET'])
@jwt_required()
def get_evolution_status():
    """Get pet evolution status and requirements"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or not user.pet:
            return jsonify({'error': 'Pet not found'}), 404
        
        pet = user.pet
        current_stage = pet.evolution_stage
        
        # Find next evolution stage
        next_stage = current_stage + 1
        next_stage_xp = Config.EVOLUTION_REQUIREMENTS.get(next_stage, None)
        
        return jsonify({
            'current_stage': current_stage,
            'stage_name': pet.get_stage_name(),
            'user_xp': user.total_xp,
            'next_stage': next_stage if next_stage_xp else None,
            'next_stage_xp': next_stage_xp,
            'xp_needed': max(0, next_stage_xp - user.total_xp) if next_stage_xp else 0,
            'can_evolve': user.total_xp >= next_stage_xp if next_stage_xp else False,
            'is_max_stage': next_stage_xp is None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pets_bp.route('/history', methods=['GET'])
@jwt_required()
def get_pet_history():
    """Get pet care history"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get pet-related activities
        activities = ActivityLog.query.filter_by(user_id=user_id).filter(
            ActivityLog.activity_type.in_(['pet_fed', 'pet_evolved', 'pet_renamed'])
        ).order_by(ActivityLog.timestamp.desc()).limit(20).all()
        
        return jsonify({
            'activities': [activity.to_dict() for activity in activities]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500