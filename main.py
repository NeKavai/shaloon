import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.gen
from tornado.options import define, options
import imghdr
import cStringIO

import os

define("port", default=8955, help="run on the given port", type=int)

class BaseHandler(tornado.web.RequestHandler):
    def set_header(self, name, value):
        super(BaseHandler, self).set_header(name, value)
        self._headers_changed[name] = True

    def set_header_safe(self, name, value):
        '''Override only default values'''
        if name not in self._headers_changed:
            self.set_header(name, value)

    def set_default_headers(self):
        headers = [
            ('ContentType', 'Content-Type')
        ]
        self._headers_changed = {}
        for arg in headers:
            if arg[0] in self.request.arguments:
                self._headers[arg[1]] = self.request.arguments[arg[0]][0]
                self._headers_changed[arg[1]] = True

class ImageHandler(BaseHandler):
    def get(self):
        with open('./files/image') as f:
            data = f.read()
            content_type = 'image/' + imghdr.what(cStringIO.StringIO(data))
            self.set_header_safe('Content-Type', content_type)
            self.write(data)

class BigfileHandler(BaseHandler):
    def get(self):
        with open('./files/big_image') as f:
            self.write(f.read()[:1000])
        size = int(self.get_argument('size', 1))
        for i in xrange(0, size):
            self.write('a'*1024)

class RedirectHandler(BaseHandler):
    def get(self, action=None):
        redirect_to = self.get_argument('RedirectTo', '')
        self.redirect(redirect_to)

class TemplatesHandler(BaseHandler):
    def get(self, template_name):
        with open('./templates/'+template_name) as f:
            self.finish(f.read())

application = tornado.web.Application(
    [
        (r"/image/.*", ImageHandler),
        (r"/bigfile/.*", BigfileHandler),
        (r"/redirect/(ping|pong)?", RedirectHandler),
        (r'/templates/(.*)', TemplatesHandler),
    ],
    static_path = os.path.join(os.path.dirname(__file__), "client/static"),
    debug = True
)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
