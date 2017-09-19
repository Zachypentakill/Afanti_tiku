# -*- coding: utf-8 -*-

import os
import asyncio
import time

from afanti_tiku_lib.dbs.redis_proxy import RedisProxy
import adsl_server

DEFAULT_CONFIG_FILE = 'config'
SERVER_PREFIX = 'adsl_proxy'
SERVER_PORT = 9990
INTERNAL = 1
HASH_TALBE = 'proxies'


class NoProxy(Exception): pass


class Proxy(object):

    def __init__(self, server_ids=None, config_file=None):
        if config_file is None:
            config_file = os.path.join(os.path.dirname(adsl_server.__file__),
                                       DEFAULT_CONFIG_FILE)
        redis_proxy = RedisProxy(None, config_file=config_file)
        self.redis_conn = redis_proxy._connect
        self.index = -1

        if server_ids:
            self.server_ids = server_ids
        else:
            server_size = self.redis_conn.hlen(HASH_TALBE)
            self.server_ids = list(range(server_size))


    def get_ip(self, server_id, server_prefix=SERVER_PREFIX):
        key = '{}_{:0>3}'.format(server_prefix, server_id)
        proxy_ip = self.redis_conn.hget(HASH_TALBE, key)
        return proxy_ip


    @asyncio.coroutine
    def async_get(self, server_id=None, server_prefix=SERVER_PREFIX,
                  port=SERVER_PORT, wait=True):
        if server_id is not None:
            while True:
                proxy_ip = self.get_ip(server_id, server_prefix=server_prefix)
                if not proxy_ip:
                    if wait:
                        yield from asyncio.sleep(INTERNAL)
                    else:
                        raise NoProxy()
                else:
                    proxy_ip = proxy_ip.decode()
                    proxy = '{}:{}'.format(proxy_ip, port)
                    return proxy

        while True:
            for server_id in self.server_ids:
                self.index = (self.index + 1) % len(self.server_ids)
                proxy_ip = self.get_ip(self.index, server_prefix=server_prefix)
                if not proxy_ip:
                    continue
                proxy_ip = proxy_ip.decode()
                proxy = '{}:{}'.format(proxy_ip, port)
                return proxy
            if wait:
                yield from asyncio.sleep(INTERNAL)
            else:
                raise NoProxy()



    def get(self, server_id=None, server_prefix=SERVER_PREFIX,
            port=SERVER_PORT, wait=True):
        if server_id is not None:
            while True:
                proxy_ip = self.get_ip(server_id, server_prefix=server_prefix)
                if not proxy_ip:
                    if wait:
                        time.sleep(INTERNAL)
                    else:
                        raise NoProxy()
                else:
                    proxy_ip = proxy_ip.decode()
                    proxy = '{}:{}'.format(proxy_ip, port)
                    return proxy

        while True:
            for server_id in self.server_ids:
                self.index = (self.index + 1) % len(self.server_ids)
                proxy_ip = self.get_ip(self.index, server_prefix=server_prefix)
                if not proxy_ip:
                    continue
                proxy_ip = proxy_ip.decode()
                proxy = '{}:{}'.format(proxy_ip, port)
                return proxy
            if wait:
                time.sleep(INTERNAL)
            else:
                raise NoProxy()
