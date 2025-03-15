from flask import request, jsonify
from app.api import bp
from app.models import Initiative, Goal
from app.extensions import db
from flask_jwt_extended import jwt_required
from app.services.auth_service import AuthService
import uuid

@bp.route('/initiatives', methods=['GET'])
@jwt_required()
def get_initiatives():
    current_user = AuthService.get_current_user()
    
    # Optional query parameters
    goal_id = request.args.get('goal_id')
    status = request.args.get('status')
    
    # Build query with tenant isolation
    query = Initiative.query.filter_by(tenant_id=current_user.tenant_id)
    
    # Apply filters if provided
    if goal_id:
        try:
            goal_uuid = uuid.UUID(goal_id)
            query = query.filter_by(goal_id=goal_uuid)
        except ValueError:
            return jsonify({'error': 'Invalid goal_id format'}), 400
    
    if status:
        valid_statuses = ['active', 'planned', 'completed']
        if status not in valid_statuses:
            return jsonify({'error': f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        query = query.filter_by(status=status)
    
    # Order by priority (highest first) and then by creation date
    initiatives = query.order_by(Initiative.priority.desc(), Initiative.created_at).all()
    
    return jsonify({
        'initiatives': [
            {
                'id': str(initiative.id),
                'title': initiative.title,
                'description': initiative.description,
                'status': initiative.status,
                'priority': initiative.priority,
                'goal_id': str(initiative.goal_id) if initiative.goal_id else None,
                'created_at': initiative.created_at.isoformat(),
                'updated_at': initiative.updated_at.isoformat()
            } for initiative in initiatives
        ]
    })

@bp.route('/initiatives/<uuid:initiative_id>', methods=['GET'])
@jwt_required()
def get_initiative(initiative_id):
    current_user = AuthService.get_current_user()
    
    initiative = Initiative.query.get_or_404(initiative_id)
    
    # Check tenant isolation
    AuthService.ensure_user_tenant_match(current_user, initiative)
    
    return jsonify({
        'id': str(initiative.id),
        'title': initiative.title,
        'description': initiative.description,
        'status': initiative.status,
        'priority': initiative.priority,
        'goal_id': str(initiative.goal_id) if initiative.goal_id else None,
        'created_at': initiative.created_at.isoformat(),
        'updated_at': initiative.updated_at.isoformat()
    })

@bp.route('/initiatives', methods=['POST'])
@jwt_required()
def create_initiative():
    current_user = AuthService.get_current_user()
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['title', 'status', 'priority']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate status
    valid_statuses = ['active', 'planned', 'completed']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
    
    # Validate priority
    try:
        priority = int(data['priority'])
        if not 1 <= priority <= 5:
            return jsonify({'error': 'Priority must be between 1 and 5'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Priority must be an integer between 1 and 5'}), 400
    
    # Check goal if provided
    goal = None
    if 'goal_id' in data and data['goal_id']:
        try:
            goal_id = uuid.UUID(data['goal_id'])
            goal = Goal.query.get(goal_id)
            if not goal:
                return jsonify({'error': 'Goal not found'}), 404
            
            # Ensure goal is from the same tenant
            AuthService.ensure_user_tenant_match(current_user, goal)
        except ValueError:
            return jsonify({'error': 'Invalid goal_id format'}), 400
    
    # Create initiative
    initiative = Initiative(
        tenant_id=current_user.tenant_id,
        title=data['title'],
        description=data.get('description', ''),
        status=data['status'],
        priority=priority,
        goal_id=goal.id if goal else None
    )
    
    db.session.add(initiative)
    db.session.commit()
    
    return jsonify({
        'id': str(initiative.id),
        'title': initiative.title,
        'description': initiative.description,
        'status': initiative.status,
        'priority': initiative.priority,
        'goal_id': str(initiative.goal_id) if initiative.goal_id else None,
        'created_at': initiative.created_at.isoformat(),
        'updated_at': initiative.updated_at.isoformat()
    }), 201

@bp.route('/initiatives/<uuid:initiative_id>', methods=['PUT'])
@jwt_required()
def update_initiative(initiative_id):
    current_user = AuthService.get_current_user()
    initiative = Initiative.query.get_or_404(initiative_id)
    
    # Check tenant isolation
    AuthService.ensure_user_tenant_match(current_user, initiative)
    
    data = request.get_json() or {}
    
    # Update fields if provided
    if 'title' in data:
        initiative.title = data['title']
    
    if 'description' in data:
        initiative.description = data['description']
    
    if 'status' in data:
        valid_statuses = ['active', 'planned', 'completed']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        initiative.status = data['status']
    
    if 'priority' in data:
        try:
            priority = int(data['priority'])
            if not 1 <= priority <= 5:
                return jsonify({'error': 'Priority must be between 1 and 5'}), 400
            initiative.priority = priority
        except (ValueError, TypeError):
            return jsonify({'error': 'Priority must be an integer between 1 and 5'}), 400
    
    if 'goal_id' in data:
        if data['goal_id'] is None:
            initiative.goal_id = None
        else:
            try:
                goal_id = uuid.UUID(data['goal_id'])
                goal = Goal.query.get(goal_id)
                if not goal:
                    return jsonify({'error': 'Goal not found'}), 404
                
                # Ensure goal is from the same tenant
                AuthService.ensure_user_tenant_match(current_user, goal)
                initiative.goal_id = goal.id
            except ValueError:
                return jsonify({'error': 'Invalid goal_id format'}), 400
    
    db.session.commit()
    
    return jsonify({
        'id': str(initiative.id),
        'title': initiative.title,
        'description': initiative.description,
        'status': initiative.status,
        'priority': initiative.priority,
        'goal_id': str(initiative.goal_id) if initiative.goal_id else None,
        'created_at': initiative.created_at.isoformat(),
        'updated_at': initiative.updated_at.isoformat()
    })

@bp.route('/initiatives/<uuid:initiative_id>', methods=['DELETE'])
@jwt_required()
def delete_initiative(initiative_id):
    current_user = AuthService.get_current_user()
    initiative = Initiative.query.get_or_404(initiative_id)
    
    # Check tenant isolation
    AuthService.ensure_user_tenant_match(current_user, initiative)
    
    db.session.delete(initiative)
    db.session.commit()
    
    return '', 204