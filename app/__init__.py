import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置 - 使用 PostgreSQL (Render)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render 提供的 PostgreSQL URL 格式
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # 本地开发使用 SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gaming_room.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 注册 Blueprint
    from app.routes.home import home_bp
    from app.routes.rooms import rooms_bp
    from app.routes.timer import timer_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(timer_bp)
    
    # 创建表
    with app.app_context():
        from app import models
        db.create_all()
    
    return app

# 在包级别暴露 WSGI 可调用对象，方便 gunicorn / flask 解析 app:app
app = create_app()

