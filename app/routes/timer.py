from datetime import datetime
from flask import Blueprint, jsonify, request
from app import db
from app.models import Room, Session

timer_bp = Blueprint("timer", __name__)


def _serialize_session(session: Session):
    """对外序列化：附带房间名称、剩余分钟、进度、预计结束。"""
    d = session.to_dict()
    if session.room:
        d["room_name"] = session.room.name
        d["hourly_rate"] = session.room.hourly_rate
        d["theme_color"] = session.room.theme_color
        d["theme_emoji"] = session.room.theme_emoji
    d["cost"] = session.get_cost()
    d["remaining_minutes"] = session.get_remaining_minutes()
    d["progress"] = session.get_progress()
    planned_end = session.get_planned_end()
    d["planned_end"] = planned_end.isoformat() if planned_end else None
    return d


@timer_bp.route("/api/sessions", methods=["GET"])
def get_sessions():
    """所有会话（默认按开始时间倒序，最多 50 条）。"""
    active_only = request.args.get("active", "false").lower() == "true"

    if active_only:
        sessions = Session.query.filter_by(status="active").all()
    else:
        sessions = (
            Session.query.order_by(Session.start_time.desc()).limit(50).all()
        )
    return jsonify([_serialize_session(s) for s in sessions])


@timer_bp.route("/api/sessions/<int:session_id>", methods=["GET"])
def get_session(session_id):
    session = Session.query.get_or_404(session_id)
    return jsonify(_serialize_session(session))


@timer_bp.route("/api/rooms/<int:room_id>/start", methods=["POST"])
def start_session(room_id):
    """开始一次新会话，支持人数/时长/备注/开始时间（默认现在）。"""
    room = Room.query.get_or_404(room_id)
    if Session.query.filter_by(room_id=room_id, status="active").first():
        return jsonify({"error": "该包间已有进行中的会话，请先结账"}), 400

    data = request.json or {}
    party_size = int(data.get("party_size") or 2)
    planned_minutes = int(data.get("planned_minutes") or 120)
    notes = (data.get("notes") or "").strip()[:200]
    customer_name = (data.get("customer_name") or "散客").strip()[:50]

    # 支持自定义开始时间（用于"提前预约"），否则用现在
    start_time = datetime.utcnow()
    if data.get("start_time"):
        try:
            start_time = datetime.fromisoformat(data["start_time"])
        except ValueError:
            return jsonify({"error": "开始时间格式错误，应为 ISO8601"}), 400

    session = Session(
        room_id=room_id,
        customer_name=customer_name,
        party_size=party_size,
        planned_minutes=planned_minutes,
        notes=notes,
        start_time=start_time,
        status="active",
    )
    db.session.add(session)
    db.session.commit()
    return jsonify(_serialize_session(session)), 201


@timer_bp.route("/api/sessions/<int:session_id>/end", methods=["POST"])
def end_session(session_id):
    """强制结束（结账）。"""
    session = Session.query.get_or_404(session_id)
    if session.status != "active":
        return jsonify({"error": "会话已结束"}), 400

    session.end_time = datetime.utcnow()
    session.status = "ended"
    db.session.commit()
    return jsonify(_serialize_session(session))


@timer_bp.route("/api/sessions/<int:session_id>/extend", methods=["POST"])
def extend_session(session_id):
    """延长预计结束时间。"""
    session = Session.query.get_or_404(session_id)
    if session.status != "active":
        return jsonify({"error": "只能延长进行中的会话"}), 400

    data = request.json or {}
    add_minutes = int(data.get("minutes") or 0)
    if add_minutes <= 0:
        return jsonify({"error": "minutes 必须为正整数"}), 400

    session.planned_minutes = (session.planned_minutes or 0) + add_minutes
    db.session.commit()
    return jsonify(_serialize_session(session))


@timer_bp.route("/api/sessions/<int:session_id>", methods=["PUT"])
def edit_session(session_id):
    """编辑会话（人数 / 备注 / 计划时长）。"""
    session = Session.query.get_or_404(session_id)
    if session.status != "active":
        return jsonify({"error": "只能编辑进行中的会话"}), 400

    data = request.json or {}
    if "party_size" in data:
        session.party_size = max(1, int(data["party_size"]))
    if "notes" in data:
        session.notes = (data["notes"] or "")[:200]
    if "planned_minutes" in data:
        session.planned_minutes = max(1, int(data["planned_minutes"]))
    if "customer_name" in data:
        session.customer_name = (data["customer_name"] or "散客")[:50]

    db.session.commit()
    return jsonify(_serialize_session(session))


@timer_bp.route("/api/rooms/<int:room_id>/status", methods=["GET"])
def get_room_status(room_id):
    room = Room.query.get_or_404(room_id)
    active = Session.query.filter_by(room_id=room_id, status="active").first()
    if active:
        return jsonify(
            {
                "room_id": room_id,
                "in_use": True,
                "session": _serialize_session(active),
            }
        )
    return jsonify({"room_id": room_id, "in_use": False, "hourly_rate": room.hourly_rate})


def _sorted_queue():
    """返回所有包间的实时状态，按剩余时间正序（最少剩余排前面 = 即将腾出），空房置底。"""
    rooms = Room.query.filter_by(is_active=True).order_by(Room.sort_order, Room.id).all()
    result = []

    for room in rooms:
        active = Session.query.filter_by(room_id=room.id, status="active").first()
        info = {
            "room": room.to_dict(),
            "in_use": False,
            "session": None,
            "remaining_minutes": None,
        }
        if active:
            info["in_use"] = True
            info["session"] = _serialize_session(active)
            info["remaining_minutes"] = active.get_remaining_minutes()
        result.append(info)

    # 使用中按剩余时间升序（最少剩余在前），空闲置底并保持原顺序
    in_use = [r for r in result if r["in_use"]]
    idle = [r for r in result if not r["in_use"]]
    in_use.sort(key=lambda r: r["remaining_minutes"])
    return in_use + idle


@timer_bp.route("/api/rooms/status/all", methods=["GET"])
def get_all_rooms_status():
    """所有房间当前状态概览，自动按剩余时间排队。"""
    return jsonify(_sorted_queue())


@timer_bp.route("/api/queue", methods=["GET"])
def queue():
    """对外暴露的排队接口（同 status/all），便于前端轮询。"""
    items = _sorted_queue()
    empty = sum(1 for r in items if not r["in_use"])
    return jsonify(
        {
            "rooms": items,
            "empty_count": empty,
            "in_use_count": len(items) - empty,
            "server_time": datetime.utcnow().isoformat(),
        }
    )


@timer_bp.route("/api/statistics", methods=["GET"])
def get_statistics():
    from sqlalchemy import func

    today = datetime.utcnow().date()
    today_sessions = Session.query.filter(
        func.date(Session.start_time) == today, Session.status == "ended"
    ).all()
    today_income = sum(s.get_cost() for s in today_sessions)
    active_count = Session.query.filter_by(status="active").count()
    idle_count = Room.query.filter_by(is_active=True).count() - active_count

    return jsonify(
        {
            "today_sessions": len(today_sessions),
            "today_income": today_income,
            "active_sessions": active_count,
            "idle_rooms": max(idle_count, 0),
            "total_rooms": Room.query.filter_by(is_active=True).count(),
        }
    )
