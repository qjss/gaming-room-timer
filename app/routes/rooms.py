from flask import Blueprint, jsonify, request
from app import db
from app.models import Room

rooms_bp = Blueprint('rooms', __name__)

@rooms_bp.route('/api/rooms', methods=['GET'])
def get_rooms():
    """
    获取所有包间
    """
    rooms = Room.query.filter_by(is_active=True).all()
    return jsonify([room.to_dict() for room in rooms])

@rooms_bp.route('/api/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """
    获取单个包间
    """
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict())

@rooms_bp.route('/api/rooms', methods=['POST'])
def create_room():
    """
    创建新包间
    """
    data = request.json
    room = Room(
        name=data.get('name'),
        console_type=data.get('console_type', 'PS5'),
        hourly_rate=data.get('hourly_rate', 30.0)
    )
    db.session.add(room)
    db.session.commit()
    return jsonify(room.to_dict()), 201

@rooms_bp.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """
    更新包间信息
    """
    room = Room.query.get_or_404(room_id)
    data = request.json
    
    if 'name' in data:
        room.name = data['name']
    if 'console_type' in data:
        room.console_type = data['console_type']
    if 'hourly_rate' in data:
        room.hourly_rate = data['hourly_rate']
    if 'is_active' in data:
        room.is_active = data['is_active']
    
    db.session.commit()
    return jsonify(room.to_dict())

@rooms_bp.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """
    删除包间（软删除）
    """
    room = Room.query.get_or_404(room_id)
    room.is_active = False
    db.session.commit()
    return jsonify({'message': 'Room deleted'})

@rooms_bp.route('/api/rooms/init', methods=['POST'])
def init_rooms():
    """
    初始化默认包间
    """
    default_rooms = [
        {'name': '包间1', 'console_type': 'PS5', 'hourly_rate': 30.0},
        {'name': '包间2', 'console_type': 'PS5', 'hourly_rate': 30.0},
        {'name': '包间3', 'console_type': 'Xbox', 'hourly_rate': 30.0},
        {'name': '包间4', 'console_type': 'Switch', 'hourly_rate': 25.0},
    ]
    
    for room_data in default_rooms:
        existing = Room.query.filter_by(name=room_data['name']).first()
        if not existing:
            room = Room(**room_data)
            db.session.add(room)
    
    db.session.commit()
    return jsonify({'message': 'Rooms initialized'})
