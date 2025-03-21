from flask import request, jsonify
from app.api import bp
from app.models import Goal
from app.extensions import db
from flask_jwt_extended import jwt_required
from app.services.auth_service import AuthService
from datetime import datetime

@bp.route('/goals', methods=['GET'])
@jwt_required()
def get_goals():
    current_user = AuthService.get_current_user()
    
    # Build query with tenant isolation
    goals = Goal.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    return jsonify({
        'goals': [
            {
                'id': str(goal.id),
                'title': goal.title,
                'description': goal.description,
                'target_date': goal.target_date.isoformat() if goal.target_date else None,
                'status': goal.status,  
                'created_at': goal.created_at.isoformat(),
                'updated_at': goal.updated_at.isoformat(),
                'initiative_count': goal.initiatives.count()
            } for goal in goals
        ]
    })

@bp.route('/goals', methods=['POST'])
@jwt_required()
def create_goal():
    current_user = AuthService.get_current_user()
    data = request.get_json() or {}
    
    # Validate required fields
    if 'title' not in data:
        return jsonify({'error': 'Missing required field: title'}), 400
    
    # Process target_date if provided
    target_date = None
    if 'target_date' in data and data['target_date']:
        try:
            target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Create goal
    goal = Goal(
        tenant_id=current_user.tenant_id,
        title=data['title'],
        description=data.get('description', ''),
        target_date=target_date,
        status=data.get('status', 'In Progress')  # Handle status
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return jsonify({
        'id': str(goal.id),
        'title': goal.title,
        'description': goal.description,
        'target_date': goal.target_date.isoformat() if goal.target_date else None,
        'status': goal.status,  # Include status
        'created_at': goal.created_at.isoformat(),
        'updated_at': goal.updated_at.isoformat()
    }), 201

@bp.route('/goals/<uuid:goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    current_user = AuthService.get_current_user()
    goal = Goal.query.get_or_404(goal_id)
    
    # Check tenant isolation
    AuthService.ensure_user_tenant_match(current_user, goal)
    
    data = request.get_json() or {}
    
    # Update fields if provided
    if 'title' in data:
        goal.title = data['title']
    
    if 'description' in data:
        goal.description = data['description']
    
    if 'target_date' in data:
        if data['target_date'] is None:
            goal.target_date = None
        else:
            try:
                goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if 'status' in data:
        goal.status = data['status']  # Update status if provided
    
    db.session.commit()
    
    return jsonify({
        'id': str(goal.id),
        'title': goal.title,
        'description': goal.description,
        'target_date': goal.target_date.isoformat() if goal.target_date else None,
        'status': goal.status,  # Include status
        'created_at': goal.created_at.isoformat(),
        'updated_at': goal.updated_at.isoformat()
    })

@bp.route('/goals/<uuid:goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    current_user = AuthService.get_current_user()
    goal = Goal.query.get_or_404(goal_id)
    
    # Check tenant isolation
    AuthService.ensure_user_tenant_match(current_user, goal)
    
    db.session.delete(goal)
    db.session.commit()
    
    return '', 204