import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import inspect, text

db = SQLAlchemy()
migrate = Migrate()


def _ensure_schema(app):
    """补齐新字段。兼容已有数据库（Render PostgreSQL + 老 SQLite）。"""
    with app.app_context():
        # 先尝试创建缺失的表
        db.create_all()
        insp = inspect(db.engine)
        engine = db.engine
        dialect = engine.dialect.name

        def has_col(table, col):
            try:
                cols = insp.get_columns(table)
            except Exception:
                return False
            return any(c["name"] == col for c in cols)

        def add_col_if_missing(table, col, decl):
            if has_col(table, col):
                return
            sql = f"ALTER TABLE {table} ADD COLUMN {col} {decl}"
            try:
                with engine.begin() as conn:
                    conn.execute(text(sql))
            except Exception as e:
                # 忽略 "重复添加" 等
                app.logger.warning("schema upgrade skip %s.%s: %s", table, col, e)

        # SQLite 与 PostgreSQL 的默认值语法不一致，使用 IF NOT EXISTS / DEFAULT 兼容
        if dialect == "sqlite":
            add_col_if_missing("rooms", "theme_color", "VARCHAR(20) DEFAULT 'blue'")
            add_col_if_missing("rooms", "theme_emoji", "VARCHAR(8) DEFAULT '🎮'")
            add_col_if_missing("rooms", "sort_order", "INTEGER DEFAULT 0")
            add_col_if_missing("sessions", "party_size", "INTEGER DEFAULT 2")
            add_col_if_missing("sessions", "notes", "VARCHAR(200) DEFAULT ''")
            add_col_if_missing("sessions", "planned_minutes", "INTEGER DEFAULT 120")
        else:
            add_col_if_missing("rooms", "theme_color", "VARCHAR(20) DEFAULT 'blue'")
            add_col_if_missing("rooms", "theme_emoji", "VARCHAR(8) DEFAULT '🎮'")
            add_col_if_missing("rooms", "sort_order", "INTEGER DEFAULT 0")
            add_col_if_missing("sessions", "party_size", "INTEGER DEFAULT 2")
            add_col_if_missing("sessions", "notes", "VARCHAR(200) DEFAULT ''")
            add_col_if_missing("sessions", "planned_minutes", "INTEGER DEFAULT 120")


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Render PostgreSQL URL 兼容
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gaming_room.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.home import home_bp
    from app.routes.rooms import rooms_bp
    from app.routes.timer import timer_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(timer_bp)

    with app.app_context():
        from app import models  # noqa: F401  必须 import 让 SQLAlchemy 知道 mapper
        _ensure_schema(app)

    return app


# gunicorn / flask 入口
app = create_app()
