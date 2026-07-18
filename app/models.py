from datetime import datetime
from app import db


# 预设的房间主题（颜色 + emoji）。新建房间循环使用
ROOM_THEMES = [
    {"color": "blue",   "emoji": "🎮"},
    {"color": "purple", "emoji": "🍓"},
    {"color": "green",  "emoji": "🌿"},
    {"color": "yellow", "emoji": "⚡"},
    {"color": "pink",   "emoji": "🌸"},
    {"color": "red",    "emoji": "🎀"},
    {"color": "cyan",   "emoji": "❄️"},
    {"color": "orange", "emoji": "🔥"},
    {"color": "violet", "emoji": "💜"},
    {"color": "teal",   "emoji": "🌊"},
]


def pick_theme(index: int) -> dict:
    return ROOM_THEMES[index % len(ROOM_THEMES)]


class Room(db.Model):
    """包间表"""

    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    console_type = db.Column(db.String(50), default="主机游戏")
    hourly_rate = db.Column(db.Float, default=30.0)
    is_active = db.Column(db.Boolean, default=True)
    # 主题色 + emoji（用于卡片装饰）
    theme_color = db.Column(db.String(20), default="blue")
    theme_emoji = db.Column(db.String(8), default="🎮")
    sort_order = db.Column(db.Integer, default=0)  # 越小越靠前

    sessions = db.relationship(
        "Session", backref="room", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "console_type": self.console_type,
            "hourly_rate": self.hourly_rate,
            "is_active": self.is_active,
            "theme_color": self.theme_color,
            "theme_emoji": self.theme_emoji,
        }


class Session(db.Model):
    """计时会话表"""

    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    customer_name = db.Column(db.String(50), default="散客")
    party_size = db.Column(db.Integer, default=2)  # 人数
    notes = db.Column(db.String(200), default="")  # 备注
    planned_minutes = db.Column(db.Integer, default=120)  # 计划时长（分钟）
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="active")  # active / ended

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "customer_name": self.customer_name,
            "party_size": self.party_size,
            "notes": self.notes or "",
            "planned_minutes": self.planned_minutes,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "duration_minutes": self.get_duration_minutes(),
        }

    def get_duration_minutes(self) -> int:
        if not self.start_time:
            return 0
        end = self.end_time if self.end_time else datetime.utcnow()
        return int((end - self.start_time).total_seconds() / 60)

    def get_planned_end(self):
        """预计结束时间：开始时间 + 计划时长（即便未结束也可估算）"""
        if not self.start_time:
            return None
        from datetime import timedelta

        return self.start_time + timedelta(minutes=self.planned_minutes or 120)

    def get_remaining_minutes(self) -> int:
        """剩余分钟数（负数表示已超时）"""
        if not self.start_time or self.status != "active":
            return 0
        end = self.get_planned_end()
        if not end:
            return 0
        return int((end - datetime.utcnow()).total_seconds() / 60)

    def get_progress(self) -> float:
        """进度 0~1"""
        plan = self.planned_minutes or 120
        if plan <= 0:
            return 0
        return min(max(self.get_duration_minutes() / plan, 0), 1)

    def get_cost(self):
        if self.room:
            hours = self.get_duration_minutes() / 60
            return round(hours * self.room.hourly_rate, 2)
        return 0


class Setting(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)

    def to_dict(self):
        return {"key": self.key, "value": self.value}
