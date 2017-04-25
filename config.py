# coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    项目的配置文件类，配置可以都多种选择，```Config```为基类，
    配置公共部分
    """
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True   # 开启自动commit
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'cl20141205@163.com'
    MAIL_PASSWORD = ''
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <cl20141205@163.com>'
    FLASKY_ADMIN = 'cl20141205@163.com'
    FLASKY_FOLLOWERS_PER_PAGE = 2
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class TestingConfig(Config):
    pass


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,

    "default": DevelopmentConfig
}
