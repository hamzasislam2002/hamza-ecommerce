from flask import Flask, render_template
from logging.handlers import RotatingFileHandler
import logging
from flask.logging import default_handler
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

database = SQLAlchemy(metadata=metadata)
db_migration = Migrate()
csrf_protection = CSRFProtect()
login = LoginManager()
login.login_view = "users.login"
mail = Mail()

def create_app():
    app = Flask(__name__)

    config_type = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object(config_type)

    initialize_extensions(app)
    register_blueprints(app)
    register_app_callbacks(app)
    register_error_pages(app)
    return app

def register_blueprints(app):
    from project.products import products_blueprint
    from project.users import users_blueprint

    app.register_blueprint(products_blueprint)
    app.register_blueprint(users_blueprint, url_prefix='/users')

def register_app_callbacks(app):
    @app.before_request
    def app_before_request():
        app.logger.info('Calling before_request() for the Flask application')

    @app.after_request
    def app_after_request(response):
        app.logger.info('Calling after_request() for the Flask application')
        return response

    @app.teardown_request
    def app_teardown_request(error=None):
        app.logger.info('Calling before_request() for the Flask application')

    @app.teardown_appcontext
    def app_teardown_appcontext(error=None):
        app.logger.info('Calling before_request() for the Flask application')

def register_error_pages(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('405.html'), 405
    
    @app.errorhandler(403)
    def page_forbidden(e):
        return render_template('403.html'), 403
    
def initialize_extensions(app):
    database.init_app(app)
    db_migration.init_app(app, database)
    csrf_protection.init_app(app)

    login.init_app(app)

    from project.models import User

    @login.user_loader
    def loaad_user(user_id):
        query = database.select(User).where(User.id == int(user_id))
        return database.session.execute(query).scalar_one()
    
    mail.init_app(app)