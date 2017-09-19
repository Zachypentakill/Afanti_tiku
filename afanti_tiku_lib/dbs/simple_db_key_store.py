# -*- coding:utf8 -*-
from __future__ import unicode_literals, absolute_import
import os

from afanti_tiku_lib.compat import (
    compat_configparser,
)


# 从配置文件中读取db信息
# 默认的配置文件位置在 ~/.dbinfo

# 配置文件信息
'''
[db_name]
username = xxxxxxx
passwd = xxxxxxxxx
port = 330x
host = xxxxxxxx
db = xxxxxxxxxxx
'''


def get_db_info(db, config_file=None):
    # default config_file is ~/.dbinfo
    if not config_file:
        config_file = os.path.join(
                os.path.expanduser('~'),
                '.dbinfo'
            )

    configparser = compat_configparser.ConfigParser()
    with open(config_file) as f:
        configparser.readfp(f)

    user = configparser.get(db, 'username')
    passwd = configparser.get(db, 'passwd')
    host = configparser.get(db, 'host')
    port = configparser.get(db, 'port')
    db = configparser.get(db, 'db')

    if not (user and passwd and host and port):
        return None
    db_info = {
        'user': user,
        'passwd': passwd,
        'host': host,
        'port': int(port),
        'db': db
    }
    return db_info
