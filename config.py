# coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    项目的配置文件类，配置可以都多种选择，```Config```为基类，
    配置公共部分
    """
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    pass


class TestingConfig(Config):
    pass


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,

    "default": DevelopmentConfig
}
