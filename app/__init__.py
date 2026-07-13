import os
from flask import Flask
from flask_login import LoginManager
from app.models import db, User, Achievement

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=None):
    app = Flask(__name__)
    
    if config_class is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.auth.routes import auth
    from app.main.routes import main
    from app.study.routes import study
    from app.questions.routes import questions

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(main)
    app.register_blueprint(study, url_prefix='/study')
    app.register_blueprint(questions, url_prefix='/questions')

    # Seed Default Achievements & Ensure DB is created
    with app.app_context():
        db.create_all()
        seed_achievements()

    return app

def seed_achievements():
    default_achievements = [
        {"name": "First Step", "description": "Review your first question.", "badge_icon": "🌱", "type": "questions_answered", "threshold": 1},
        {"name": "Scholar", "description": "Review 25 questions.", "badge_icon": "📚", "type": "questions_answered", "threshold": 25},
        {"name": "Sage", "description": "Review 100 questions.", "badge_icon": "🧠", "type": "questions_answered", "threshold": 100},
        {"name": "Streak Starter", "description": "Reach a 3-day study streak.", "badge_icon": "🔥", "type": "streak", "threshold": 3},
        {"name": "Consistent Learner", "description": "Reach a 7-day study streak.", "badge_icon": "⚡", "type": "streak", "threshold": 7},
        {"name": "XP Starter", "description": "Accumulate 100 XP.", "badge_icon": "⭐", "type": "xp", "threshold": 100},
        {"name": "XP Titan", "description": "Accumulate 1000 XP.", "badge_icon": "👑", "type": "xp", "threshold": 1000}
    ]
    for ach_data in default_achievements:
        ach = Achievement.query.filter_by(name=ach_data["name"]).first()
        if not ach:
            new_ach = Achievement(
                name=ach_data["name"],
                description=ach_data["description"],
                badge_icon=ach_data["badge_icon"],
                type=ach_data["type"],
                threshold=ach_data["threshold"]
            )
            db.session.add(new_ach)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
