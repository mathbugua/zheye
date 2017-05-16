# coding=utf-8
from flask_script import Manager, Shell
from app import create_app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.ioloop import IOLoop

app = create_app("default")
define("port", default=5000, type=int)
manager = Manager(app)
if __name__ == '__main__':
    # manager.run()
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(options.port)
    IOLoop.instance().start()
