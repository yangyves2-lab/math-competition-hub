
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-me-in-production"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///math_hub.db").replace("postgres://", "postgresql://", 1),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        ADMIN_EMAIL=os.getenv("ADMIN_EMAIL", "admin@example.com"),
        ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD", "change-me"),
        SEARCH_PROVIDER=os.getenv("SEARCH_PROVIDER", "duckduckgo"),
        SERPER_API_KEY=os.getenv("SERPER_API_KEY", ""),
    )
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    from .models import Competition, Edition, Paper, ChangeLog, SearchRun, Source
    from .routes import public_bp, admin_bp, api_bp, AdminUser

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser() if user_id == "admin" else None
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
    with app.app_context():
        db.create_all()
        seed_if_empty()
    return app

def seed_if_empty():
    from .models import Competition
    from datetime import datetime
    if Competition.query.count():
        return
    from .models import Edition, Source
    now=datetime.utcnow()
    c1=Competition(name="AMC 10/12", country="美國／台灣區", organizer="MAA / 台灣承辦單位", category="competition",
                    target="依當年度官方資格", official_url="https://maa.org/math-competitions/amc-10-12/",
                    description="American Mathematics Competitions 系列。實際台灣報名資訊以當年度承辦單位公告為準。",
                    first_seen=now,last_checked=now,updated_at=now)
    c2=Competition(name="UKMT Senior Mathematical Challenge", country="英國／國際", organizer="UK Mathematics Trust",
                    category="competition", target="依當年度官方資格", official_url="https://ukmt.org.uk/",
                    description="UKMT 高中階數學挑戰賽。各地區報名管道與資格依官方公告。",
                    first_seen=now,last_checked=now,updated_at=now)
    db.session.add_all([c1,c2]); db.session.commit()
