# -*- coding: utf-8 -*-

import requests
from afanti_tiku_lib.common import common_headers

from adsl_server.proxy import Proxy

_proxy = Proxy()

def login(username, password):
    #url = 'http://ucenter.17zuoye.com/j_spring_security_check'
    url = 'http://ucenter.17zuoye.com/index.vpage'
    data = 'returnURL=&j_username={}&j_password={}&_spring_security_remember_me=on&_a_loginForm=%E7%AB%8B%E5%8D%B3%E7%99%BB%E5%BD%95'.format(username, password)

    common_headers.update({
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'http://ucenter.17zuoye.com/index.vpage',
    })

    while True:
        try:
            resp = requests.get(url, headers=common_headers, data=data, timeout=5, allow_redirects=True,
                                proxies = {'http': 'http://' + _proxy.get()})
            if resp.ok is True and resp.status_code == 200:
                #print(resp.cookies.get_dict())
                #return resp.history[0].cookies.get_dict()
                print(resp.cookies.get_dict())
                return resp.cookies.get_dict()
            else:
                print(resp.json())
                return False
        except Exception:
            continue


if __name__ == '__main__':
    print(login('15545082848', 'yiek28x0s'))
