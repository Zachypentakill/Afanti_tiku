# -*- coding: utf-8 -*-

import sys
import logging
import asyncio

import tornado.ioloop
from tornado.web import RequestHandler, Application

from mathjax_render.aphantomjs import APhantom
from mathjax_render.parser import Parser as MathjaxParser

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/mathjax_rendering.log', filemode='a')

mathjax_parser = MathjaxParser()
aphantom = APhantom(concurrency=1,
                    executable_path='/data/home/dingfanghong/local/bin/phantomjs')



class Handler(RequestHandler):

    @asyncio.coroutine
    def post(self):

        try:
            latex = self.request.body.decode('utf-8')
        except Exception as err:
            logging.error('[body.decode(\'utf-8\')]: {}'.format(latex))
            self.write({'code': 101, 'data': None, 'msg': '{}'.format(err)})
            self.flush()
            return None

        chuck = yield from aphantom.render(latex)
        rendered_latex = mathjax_parser.get_render_html(chuck)

        self.write({'code': 0, 'data': rendered_latex})
        self.flush()


if __name__ == '__main__':
    addr = sys.argv[1]
    port = sys.argv[2]
    server = Application([
        ('.*', Handler),
    ])

    server.listen(int(port), addr)

    tornado.ioloop.IOLoop.current().start()

