# -*- coding: utf-8 -*-

import time
import requests

from proxy import Proxy

_proxy = Proxy()

def check_proxies():
    for server_id in range(100):
        proxies = {'http': 'http://' + _proxy.get(server_id=server_id)}

        info = timeit(proxies)

        print('server_id:', server_id)
        print(info)
        print('-'*40 + '\n')


def timeit(proxies):
    start = time.time()

    info = None
    for _ in range(2):
        try:
            resp = requests.get('http://baidu.com', proxies=proxies, timeout=30)
            end = time.time()

            info = 'case: {:.2f}, code: {}'.format(end - start, resp.status_code)
            break
        except Exception as err:
            end = time.time()
            info = 'case: {:.2f}, [ERROR]: {}'.format(end - start, err)

    return info


def main():
    check_proxies()


if __name__ == '__main__':
    main()
