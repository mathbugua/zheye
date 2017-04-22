# coding=utf-8
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login_register"


def create_app(config_name):
    # 创建Flask实例，并进行初始化
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
