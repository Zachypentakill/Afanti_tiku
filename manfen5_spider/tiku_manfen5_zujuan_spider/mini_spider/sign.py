# -*- coding: utf-8 -*-

import logging
import string
import random

import requests

from adsl_server.proxy import Proxy
from user_agent_lib.user_agent import UserAgent

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/sign.log', filemode='a')

_proxy = Proxy()
user_agent = UserAgent()

LETTERS = string.ascii_letters * 10 + string.digits * 20

HEADERS = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Accept': '*/*',
'Referer': 'http://tiku.manfen5.com/reg.aspx',
'Connection': 'keep-alive',
}


def generate_password():
    size = random.randint(6, 12)
    pwd = ''.join(random.sample(LETTERS, size))
    return pwd


def request(method, url, **kwargs):
    for _ in range(10):
        try:
            proxies = {'http': 'http://' + _proxy.get()}
            resp = requests.request(method, url, proxies=proxies, **kwargs)
            return resp
        except Exception:
            continue
    return None


def sign(username, password):
    url = 'http://tiku.manfen5.com/reg.aspx??randnum={}'.format(random.random())
    data  = 'type=reg&username={}&password={}&x='.format(username, password)
    headers = dict(HEADERS)
    headers['User-Agent'] = user_agent.get()
    resp = request('POST', url, data=data, headers=headers)

    if not resp:
        return False

    if resp.text.startswith('1|'):
        return True
    else:
        return False


def main():
    users = []
    i = 0
    for line in open('working/usernames'):
        i += 1
        if i < 5040:
            continue

        line = line.strip()
        if not line:
            continue

        pwd = generate_password()
        if sign(line, pwd):
            logging.info('[user]: {} {}'.format(line, pwd))
            users.append((line, pwd))

    with open('working/users', 'w') as fd:
        for username, password in users:
            fd.write('{} {}\n'.format(username, password))


if __name__ == '__main__':
    main()
