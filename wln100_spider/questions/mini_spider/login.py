# -*- coding: utf-8 -*-

import requests
from afanti_tiku_lib.common import common_headers


def login(username, password):
    url = 'http://www.wln100.com/User/Index/login.html'
    data = 'userName={}&passWord={}&ifSave=1'.format(username, password)

    common_headers.update({
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
    })

    try:
        resp = requests.post(url, headers=common_headers, data=data)
        if resp.ok is True and resp.status_code == 200:
            return resp.cookies.get_dict()
        else:
            return False
    except Exception:
        return False


if __name__ == '__main__':
    print(login('15566679724', 'qazwsx'))
