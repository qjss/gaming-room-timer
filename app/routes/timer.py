from datetime import datetime
from flask import Blueprint, jsonify, request
from app import db
from app.models import Room, Session

timer_bp = Blueprint('timer', __name__)

@timer_bp.route('/api/sessions', methods=['GET'])
def get_sessions():
    """"""
    获取所有会话
    """"""
    active_only = request.args.get('active', 'false').lower() == 'true'
    
    if active_only:
        sessions = Session.query.filter_by(status='active').all()
    else:
        sessions = Session.query.order_by(Session.start_time.desc()).limit(50).all()
    
    result = []
    for session in sessions:
        session_dict = session.to_dict()
        session_dict['room_name'] = session.room.name if session.room else None
        session_dict['cost'] = session.get_cost()
        result.append(session_dict)
    
    return jsonify(result)

@timer_bp.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """"""
    获取单个会话
    """"""
    session = Session.query.get_or_404(session_id)
    session_dict = session.to_dict()
    session_dict['room_name'] = session.room.name if session.room else None
    session_dict['cost'] = session.get_cost()
    return jsonify(session_dict)

@timer_bp.route('/api/rooms/<int:room_id>/start', methods=['POST'])
def start_session(room_id):
    """"""
    开始计时
    """"""
    room = Room.query.get_or_404(room_id)
    
    # 检查该包间是否已有活跃会话
    active_session = Session.query.filter_by(room_id=room_id, status='active').first()
    if active_session:
        return jsonify({'error': '该包间已有活跃会话'}), 400
    
    data = request.json or {}
    session = Session(
        room_id=room_id,
        customer_name=data.get('customer_name', '散客'),
        start_time=datetime.utcnow(),
        status='active'
    )
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.to_dict()), 201

@timer_bp.route('/api/sessions/<int:session_id>/end', methods=['POST'])
def end_session(session_id):
    """"""
    结束计时
    """"""
    session = Session.query.get_or_404(session_id)
    
    if session.status != 'active':
        return jsonify({'error': '会话已结束'}), 400
    
    session.end_time = datetime.utcnow()
    session.status = 'ended'
    db.session.commit()
    
    session_dict = session.to_dict()
    session_dict['room_name'] = session.room.name if session.room else None
    session_dict['cost'] = session.get_cost()
    
    return jsonify(session_dict)

@timer_bp.route('/api/rooms/<int:room_id>/status', methods=['GET'])
def get_room_status(room_id):
    """"""
    获取包间状态（是否在使用中）
    """"""
    room = Room.query.get_or_404(room_id)
    active_session = Session.query.filter_by(room_id=room_id, status='active').first()
    
    if active_session:
        return jsonify({
            'room_id': room_id,
            'in_use': True,
            'session': {
                **active_session.to_dict(),
                'room_name': room.name,
                'cost': active_session.get_cost()
            }
        })
    else:
        return jsonify({
            'room_id': room_id,
            'in_use': False,
            'hourly_rate': room.hourly_rate
        })

@timer_bp.route('/api/rooms/status/all', methods=['GET'])
def get_all_rooms_status():
    """"""
    获取所有包间的状态概览
    """"""
    rooms = Room.query.filter_by(is_active=True).all()
    result = []
    
    for room in rooms:
        active_session = Session.query.filter_by(room_id=room.id, status='active').first()
        
        room_info = {
            'room': room.to_dict(),
            'in_use': False,
            'session': None
        }
        
        if active_session:
            session_dict = active_session.to_dict()
            session_dict['room_name'] = room.name
            session_dict['cost'] = active_session.get_cost()
            room_info['in_use'] = True
            room_info['session'] = session_dict
        
        result.append(room_info)
    
    return jsonify(result)

@timer_bp.route('/api/statistics', methods=['GET'])
def get_statistics():
    """"""
    获取统计数据
    """"""
    from sqlalchemy import func
    
    # 今日会话数
    today = datetime.utcnow().date()
    today_sessions = Session.query.filter(
        func.date(Session.start_time) == today,
        Session.status == 'ended'
    ).all()
    
    # 今日收入
    today_income = sum(s.get_cost() for s in today_sessions)
    
    # 当前活跃会话
    active_count = Session.query.filter_by(status='active').count()
    
    return jsonify({
        'today_sessions': len(today_sessions),
        'today_income': today_income,
        'active_sessions': active_count
    })
