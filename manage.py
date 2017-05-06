# coding=utf-8
from flask_script import Manager, Shell
from app import create_app

app = create_app("default")
manager = Manager(app)
if __name__ == '__main__':
    manager.run()
