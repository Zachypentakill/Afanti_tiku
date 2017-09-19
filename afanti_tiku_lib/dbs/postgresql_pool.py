# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import afanti_tiku_lib
from afanti_tiku_lib.compat import (
    compat_configparser,
)

import os

import psycopg2
import peewee

# 默认配置文件是 'afanti_tiku_lib/config'
DEFAULT_CONFIG_FILE = 'config'


class BasePostgresql(object):

    def __init__(self, config_file=None):
        if not config_file:
            top_dir = os.path.dirname(afanti_tiku_lib.__file__)
            config_file = os.path.join(top_dir, DEFAULT_CONFIG_FILE)
        else:
            config_file = config_file

        configparser = compat_configparser.ConfigParser()
        configparser.readfp(open(config_file))

        self.user = configparser.get('postgresql', 'user')
        if not self.user:
            self.user = None

        self.password = configparser.get('postgresql', 'password')
        if not self.password:
            self.password = ''

        self.host = configparser.get('postgresql', 'host')
        if not self.host:
            self.host = 'localhost'

        self.port = configparser.getint('postgresql', 'port')
        if not self.port:
            self.port = 5432


class CommonPostgresql(BasePostgresql):

    def __init__(self, database, config_file=None):
        super(CommonPostgresql, self).__init__(config_file=config_file)
        self.database = database

    def connection(self, database=None):
        database = (database or self.database)
        connect = psycopg2.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            database = database
        )
        return connect

    def insert(self, table, item, database=None, ignore=True):
        database = (database or self.database)
        connect = self.connection(database=database)
        cursor = connect.cursor()

        cols = item.keys()
        values = [item[key] for key in cols]

        cmd = 'insert{}into {} ({}) values ({})'.format(
            table,
            (' ignore ', ' ')[ignore is True],
            ', '.join(cols),
            ', '.join(['%s']*len(cols)),
        )
        result = cursor.execute(cmd, values)
        connect.commit()
        return result


class OrmPostgresql(BasePostgresql):

    def __init__(self, database, config_file=None):
        super(OrmPostgresql, self).__init__(config_file=config_file)
        self.database = database

    def connection(self, database=None):
        database = (database or self.database)
        connect = peewee.PostgresqlDatabase(
            database,
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password
        )
        return connect

