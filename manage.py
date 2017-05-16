# coding=utf-8
from app import create_app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.ioloop import IOLoop
from app import db
from app.models.models import Role

app = create_app("default")
define("port", default=5000, type=int)
define("cmd", default="runserver")


def runserver():
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(options.port)
    print "Server runing on http://0.0.0.0:%d" % options.port
    IOLoop.instance().start()


def create_db():
    with app.app_context():
        db.create_all()
        Role.insert_roles()   # 创建角色

if __name__ == '__main__':
    options.parse_command_line()
    if options.cmd == "runserver":
        runserver()
    elif options.cmd == "create_db":
        create_db()

