# coding=utf-8
from flask import Flask
from flask_bootstrap import Bootstrap
from config import config

bootstrap = Bootstrap()


def create_app(config_name):
    # 创建Flask实例，并进行初始化
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
