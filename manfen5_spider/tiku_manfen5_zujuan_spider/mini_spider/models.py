# -*- coding: utf-8 -*-

import time
import mugen
import random
import asyncio
from collections import deque

from adsl_server.proxy import Proxy
from adsl_server.proxy_pool import BaseProxyPool
from user_agent_lib.user_agent import UserAgent

_proxy = Proxy()
user_agent = UserAgent()

HEADERS = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
# 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Accept': '*/*',
'Referer': 'http://tiku.manfen5.com/',
'Connection': 'keep-alive',
}


class ProxyPool(BaseProxyPool):

    def __init__(self, annealing_cycle, server_ids=None):
        super(ProxyPool, self).__init__(annealing_cycle, server_ids=server_ids)
        self.attr_gens = ('make_headers', 'make_cookies')
        self.users = get_users()
        self.cookies = {}


    async def make_headers(self, proxy):
        print('make_headers')
        ua = user_agent.get()
        headers = dict(HEADERS)
        headers['User-Agent'] = ua
        return headers

    async def make_cookies(self, proxy):
        print('make_cookies')
        username, password = self.users.pop()
        self.users.appendleft([username, password])

        if not self.cookies.get(username):
            cookies = await login(username, password)
            self.cookies[username] = cookies

        print('self.cookies', self.cookies[username])

        return self.cookies[username]



def get_users():
    users = deque()
    for line in open('working/users'):
        line = line.strip()
        if not line:
            continue

        users.append(line.split(' '))

    return users



async def login(username, password):
    data = 'type=login&userid={}&password={}&x='.format(username, password)

    while True:
        try:
            url = 'http://tiku.manfen5.com/default.aspx??randnum={}'.format(random.random())
            proxy = 'http://' + _proxy.get()
            headers = dict(HEADERS)
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            resp = await mugen.post(url, data=data, headers=headers, proxy=proxy)
            if resp.status_code == 200:
                return resp.cookies.get_dict()
            else:
                await asyncio.sleep(2)
        except Exception:
            await asyncio.sleep(2)
            continue


def test():
    print(login('icool42', 'qazwsx'))


if __name__ == '__main__':
    test()
