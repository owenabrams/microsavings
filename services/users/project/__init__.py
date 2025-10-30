"""Flask application factory."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt


# Instantiate extensions
db = SQLAlchemy()
cors = CORS()
bcrypt = Bcrypt()


def create_app(script_info=None):
    """Application factory pattern."""
    
    # Instantiate the app
    app = Flask(__name__)
    
    # Set config
    app_settings = os.getenv('APP_SETTINGS', 'project.config.DevelopmentConfig')
    app.config.from_object(app_settings)
    
    # Set up extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    bcrypt.init_app(app)
    
    # Register blueprints
    from project.api.auth import auth_blueprint
    from project.api.savings_groups import savings_groups_blueprint
    from project.api.members import members_blueprint
    from project.api.group_settings import group_settings_blueprint
    from project.api.saving_types import saving_types_blueprint
    from project.api.member_profile import member_profile_blueprint
    from project.api.ping import ping_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    app.register_blueprint(savings_groups_blueprint, url_prefix='/api/savings-groups')
    app.register_blueprint(group_settings_blueprint, url_prefix='/api/groups')
    app.register_blueprint(saving_types_blueprint, url_prefix='/api')
    app.register_blueprint(member_profile_blueprint, url_prefix='/api')
    app.register_blueprint(members_blueprint, url_prefix='/api/members')
    app.register_blueprint(ping_blueprint)
    
    # Shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}
    
    return app

