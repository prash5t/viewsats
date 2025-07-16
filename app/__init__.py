from flask import Flask
from flask.cli import load_dotenv
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    from app.extensions import db, scheduler
    db.init_app(app)
    scheduler.init_app(app)

    # Register blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Initialize database and scheduler
    with app.app_context():
        db.create_all()

        # Initialize scheduler
        from app.services import init_scheduler
        init_scheduler()

    return app
