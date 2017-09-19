# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import afanti_tiku_lib
from afanti_tiku_lib.compat import (
    compat_mysql,
    compat_configparser,
)

import os

import peewee

# 默认配置文件是 'afanti_tiku_lib/config'
DEFAULT_CONFIG_FILE = 'config'
DEFAULT_CHARSET = 'utf8'


class BaseMysql(object):

    def __init__(self, config_file=None):
        if not config_file:
            top_dir = os.path.dirname(afanti_tiku_lib.__file__)
            config_file = os.path.join(top_dir, DEFAULT_CONFIG_FILE)
        else:
            config_file = config_file

        configparser = compat_configparser.ConfigParser()
        configparser.readfp(open(config_file))

        self.user = configparser.get('mysql', 'user')
        if not self.user:
            self.user = None

        self.password = configparser.get('mysql', 'password')
        if not self.password:
            self.password = ''

        self.host = configparser.get('mysql', 'host')
        if not self.host:
            self.host = 'localhost'

        self.port = configparser.getint('mysql', 'port')
        if not self.port:
            self.port= 3306


class CommonMysql(BaseMysql):

    def __init__(self, db, config_file=None):
        super(CommonMysql, self).__init__(config_file=config_file)
        self.db = db

    def connection(self, db=None, charset=DEFAULT_CHARSET, **kwargs):

        # compat_mysql sures "Threads may share the module, but not connections."
        # http://stackoverflow.com/a/9173737
        # so, each thread will has one unqiue connect,
        # making sure MySQL client library not to die.

        db = (db or self.db)
        connect = compat_mysql.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            passwd = self.password,
            db = db,
            charset=charset,
            **kwargs
        )
        return connect

    def insert(self, table, item, db=None, ignore=True, **kwargs):
        db = (db or self.db)
        connect = self.connection(db=db, **kwargs)
        cursor = connect.cursor()

        cols = list(item.keys())
        values = [item[col] for col in cols]

        cmd = 'insert{}into {} ({}) values ({})'.format(
            (' ', ' ignore ')[ignore is True],
            table,
            ', '.join(cols),
            ', '.join(['%s']*len(cols)),
        )
        result = cursor.execute(cmd, values)
        connect.commit()
        return result


class OrmMysql(BaseMysql):

    def __init__(self, db, config_file=None):
        super(OrmMysql, self).__init__(config_file=config_file)
        self.db = db

    def connection(self, db=None):
        db = (db or self.db)
        connect = peewee.MySQLDatabase(
            db,
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password
        )
        return connect
