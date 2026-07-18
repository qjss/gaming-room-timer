from datetime import datetime
from app import db

class Room(db.Model):
    """
    包间表
    """
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 包间名称，如"包间1"
    console_type = db.Column(db.String(50), default='PS5')  # 游戏机类型
    hourly_rate = db.Column(db.Float, default=30.0)  # 每小时价格
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    
    # 关系
    sessions = db.relationship('Session', backref='room', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'console_type': self.console_type,
            'hourly_rate': self.hourly_rate,
            'is_active': self.is_active
        }

class Session(db.Model):
    """
    计时会话表
    """
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    customer_name = db.Column(db.String(50), default='散客')  # 顾客名称
    start_time = db.Column(db.DateTime, default=datetime.utcnow)  # 开始时间
    end_time = db.Column(db.DateTime, nullable=True)  # 结束时间
    status = db.Column(db.String(20), default='active')  # active, ended
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'customer_name': self.customer_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'duration_minutes': self.get_duration_minutes()
        }
    
    def get_duration_minutes(self):
        if self.start_time:
            end = self.end_time if self.end_time else datetime.utcnow()
            return int((end - self.start_time).total_seconds() / 60)
        return 0
    
    def get_cost(self):
        if self.room:
            hours = self.get_duration_minutes() / 60
            return round(hours * self.room.hourly_rate, 2)
        return 0

class Setting(db.Model):
    """
    系统设置表
    """
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }
