# -*- coding: utf-8 -*-

import time
import requests

from user_agent_lib.user_agent import UserAgent
from adsl_server.proxy import Proxy

_proxy = Proxy()
user_agent = UserAgent()

HEADERS = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Cache-Control': 'no-cache',
'Connection': 'keep-alive',
}


def request():
    url = 'http://www.jtyhjy.com/sts/'
    while True:
        try:
            proxy = 'http://' + _proxy.get()
            HEADERS['User-Agent'] = user_agent.get()
            resp = requests.get(url, headers=HEADERS, proxies={'http': proxy})
            return resp
        except Exception:
            time.sleep(5)
            continue


def get_cookies():
    resp = request()
    return resp.cookies.get_dict()


