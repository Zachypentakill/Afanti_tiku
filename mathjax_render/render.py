
import json
import os
import asyncio
import mugen
import urllib

_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_DIR, 'config')


class RenderProxy(object):

    def __init__(self, config_file=CONFIG_FILE):
        config = json.load(open(config_file))
        self.config = config
        self.server_ports = config['server_ports']
        self.url = 'http://' + urllib.parse.urlparse(config['url']).netloc

        port_queue = asyncio.queues.Queue()
        for port in self.server_ports:
            port_queue._queue.append(port)

        self.port_queue = port_queue

        self.session = mugen.session()


    @asyncio.coroutine
    def render(self, latex):
        port = yield from self.port_queue.get()
        try:
            resp = yield from self.session.post(
                self.url + ':' + port,
                data=latex,
                timeout=30
            )
            return resp.json()
        finally:
            yield from self.port_queue.put(port)

