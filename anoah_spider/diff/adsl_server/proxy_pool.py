# -*- coding: utf-8 -*-

import logging
import time
import heapq
import random
import asyncio
from collections import deque

from .proxy import Proxy

random = random.SystemRandom()


class BaseProxyPool(object):

    def __init__(self, annealing_cycle, server_ids=None):
        server_ids = server_ids or range(100)
        self._proxy = Proxy()
        self._proxies = [DelayProxy(i) for i in server_ids]
        self.annealing_cycle = annealing_cycle * 1000
        self._heapify()
        self.attr_gens = []


    def _heapify(self):
        heapq.heapify(self._proxies)


    async def _equip_proxy(self, proxy):
        for attr in self.attr_gens:
            if attr.startswith('make_'):
                name = attr[5:]
                val = await getattr(self, attr)(proxy)
                setattr(proxy, name, val)


    async def get(self):
        await self.wait()

        proxy = None
        ip_port = None
        while True:

            proxy = heapq.heappop(self._proxies)

            # wait annealing time
            internal = int(time.time() * 1000) - proxy._last_time - self.annealing_cycle
            if internal < 0:
                tm = (-internal / 1000.0) + random.randint(-2, 5)
                await asyncio.sleep(tm)

            try:
                ip_port = await self._proxy.async_get(server_id=proxy._proxy_id, wait=False)
            except Exception:
                logging.warn('[Proxy.async_get] {} is not existed'.format(proxy.proxy_id))
                proxy.done()
                self.put(proxy)
                continue

            if ip_port != proxy.ip_port:
                proxy.ip_port = ip_port
                await self._equip_proxy(proxy)

            logging.info('[ProxyPool]: proxy: {!r}'.format(proxy))

            break

        return ip_port, proxy


    def put(self, proxy):
        heapq.heappush(self._proxies, proxy)


    async def wait(self):
        while not self._proxies:
            await asyncio.sleep(1)



class DelayProxy(object):

    def __init__(self, proxy_id):
        self._proxy_id = proxy_id
        self._last_time = 0
        self.ip_port = None


    def __lt__(self, proxy):
        return self._last_time < proxy._last_time


    def __eq__(self, proxy):
        return self._last_time == proxy._last_time


    def __gt__(self, proxy):
        return self._last_time > proxy._last_time


    def done(self):
        self._last_time = int(time.time() * 1000)

