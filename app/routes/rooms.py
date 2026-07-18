from flask import Blueprint, jsonify, request
from app import db
from app.models import Room, ROOM_THEMES, pick_theme

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/api/rooms", methods=["GET"])
def get_rooms():
    rooms = Room.query.filter_by(is_active=True).order_by(Room.sort_order, Room.id).all()
    return jsonify([r.to_dict() for r in rooms])


@rooms_bp.route("/api/rooms/<int:room_id>", methods=["GET"])
def get_room(room_id):
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict())


@rooms_bp.route("/api/rooms", methods=["POST"])
def create_room():
    data = request.json or {}
    # 主题：根据总房间数自动分配，也可显式覆盖
    existing = Room.query.count()
    theme = pick_theme(existing)
    room = Room(
        name=data.get("name") or f"包间{existing + 1}",
        console_type=data.get("console_type", "主机游戏"),
        hourly_rate=data.get("hourly_rate", 30.0),
        theme_color=data.get("theme_color") or theme["color"],
        theme_emoji=data.get("theme_emoji") or theme["emoji"],
        sort_order=data.get("sort_order", existing),
    )
    db.session.add(room)
    db.session.commit()
    return jsonify(room.to_dict()), 201


@rooms_bp.route("/api/rooms/<int:room_id>", methods=["PUT"])
def update_room(room_id):
    room = Room.query.get_or_404(room_id)
    data = request.json or {}

    for f in ("name", "console_type", "hourly_rate", "theme_color", "theme_emoji", "sort_order"):
        if f in data:
            setattr(room, f, data[f])
    if "is_active" in data:
        room.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify(room.to_dict())


@rooms_bp.route("/api/rooms/<int:room_id>", methods=["DELETE"])
def delete_room(room_id):
    """软删除。"""
    room = Room.query.get_or_404(room_id)
    room.is_active = False
    db.session.commit()
    return jsonify({"message": "Room deleted", "id": room_id})


@rooms_bp.route("/api/rooms/init", methods=["POST"])
def init_rooms():
    """初始化 6 个默认包间，每个分配独立主题色。"""
    presets = [
        ("1号房（蜡笔小新）", 30.0),
        ("2号房（草莓熊）",   30.0),
        ("3号房（皮卡丘）",   30.0),
        ("4号房（库洛米）",   30.0),
        ("5号房（Hello Kitty）", 30.0),
        ("6号房（初音未来）", 30.0),
        ("7号房（海贼王）",   35.0),
        ("8号房（火影忍者）", 35.0),
    ]

    created = 0
    existing_count = Room.query.count()
    for i, (name, rate) in enumerate(presets):
        if Room.query.filter_by(name=name).first():
            continue
        theme = pick_theme(existing_count + i)
        room = Room(
            name=name,
            console_type="主机游戏",
            hourly_rate=rate,
            theme_color=theme["color"],
            theme_emoji=theme["emoji"],
            sort_order=existing_count + i,
        )
        db.session.add(room)
        created += 1
    db.session.commit()
    return jsonify({"message": f"包间已初始化，新增 {created} 间", "created": created})
