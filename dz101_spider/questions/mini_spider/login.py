# -*- coding: utf-8 -*-

import requests

from afanti_tiku_lib.common import common_headers
from afanti_tiku_lib.utils import md5_string


common_headers.update({'Referer':'http://www.dz101.com/zujuan/zhishidian',
                       'X-Requested-With':'XMLHttpRequest'})

def login(username, password):
    url = 'http://www.dz101.com/common/Login'
    session = requests.Session()

    resp = session.get(url, headers=common_headers)

    url = 'http://www.dz101.com/common/IsUser?Step=IsLogin&IsMobile={}&PasswordA={}&PasswordB=undefined&IsVerify=undefined&appstr=Teacher&province=undefined&city=undefined&county=undefined&unit_id=undefined&my_school=undefined&verify_token=undefined'.format(username, md5_string(password))
    resp = session.get(url, headers=common_headers)

    cookies = {
        'PHPSESSID': session.cookies.get('PHPSESSID'),
        'MyName': username,
        'Automatic_login': '{}%7C{}%7CTeacher'.format(username, md5_string(password))
    }

    url = 'http://www.dz101.com/common/get_session'
    resp = session.get(url, headers=common_headers, cookies=cookies)

    return cookies


def test():
    cookies = login('15542652940', 'www888xxx')
    url = 'http://www.dz101.com/zujuan/zhishidian/Problems?Key=初中语文&Subject=初中语文&QuestionTypes=&Difficulty=&Year=&Grade=全部&Type=&Area=&subject_id=189&Limit=1&Skip=0&Page=1'
    html = requests.get(url, headers=common_headers, cookies=cookies).text
    print(html)


if __name__ == '__main__':
    test()
