from flask import Flask, render_template
from app.extensions import db, migrate, jwt
from app.config import Config
from app.database import get_sync_engine

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Register blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    @app.route('/')
    def landing_page():
        return render_template('index.html')
    
    return app