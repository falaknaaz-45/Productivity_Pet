from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.user import User
from app.models.task import Task
from app.models.activity_log import ActivityLog
from app.services.gamification import GamificationEngine

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks for current user"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get filter parameters
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        
        # Build query
        query = Task.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        if priority:
            query = query.filter_by(priority=priority)
        
        tasks = query.order_by(Task.deadline.asc()).all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks],
            'total': len(tasks)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        # Parse deadline if provided
        deadline = None
        if 'deadline' in data and data['deadline']:
            try:
                deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid deadline format. Use ISO 8601'}), 400
        
        # Create task
        task = Task(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            category=data.get('category'),
            priority=data.get('priority', 'Medium'),
            deadline=deadline,
            is_recurring=data.get('is_recurring', False),
            recurrence_pattern=data.get('recurrence_pattern')
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Log activity
        ActivityLog.log_activity(
            user_id=user_id,
            activity_type='task_created',
            description=f'Created task: {task.title}'
        )
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'task': task.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'category' in data:
            task.category = data['category']
        if 'priority' in data:
            task.priority = data['priority']
            task.points_value = task.calculate_points()
        if 'deadline' in data:
            if data['deadline']:
                task.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            else:
                task.deadline = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
@jwt_required()
def complete_task(task_id):
    """Mark task as complete"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        if task.status == 'Completed':
            return jsonify({'error': 'Task already completed'}), 400
        
        # Mark task complete and get XP
        xp_earned = task.mark_complete()
        
        # Use gamification engine to process completion
        gamification = GamificationEngine()
        result = gamification.process_task_completion(user, task, xp_earned)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task completed successfully!',
            'task': task.to_dict(),
            'xp_earned': xp_earned,
            'leveled_up': result['leveled_up'],
            'new_level': result['new_level'],
            'pet_status': result['pet_status'],
            'achievements_unlocked': result['achievements_unlocked']
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """Get task statistics for current user"""
    try:
        user_id = int(get_jwt_identity())
        
        total_tasks = Task.query.filter_by(user_id=user_id).count()
        completed_tasks = Task.query.filter_by(user_id=user_id, status='Completed').count()
        pending_tasks = Task.query.filter_by(user_id=user_id, status='Pending').count()
        
        # Get overdue tasks
        overdue_tasks = Task.query.filter(
            Task.user_id == user_id,
            Task.status == 'Pending',
            Task.deadline < datetime.utcnow()
        ).count()
        
        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return jsonify({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': round(completion_rate, 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500