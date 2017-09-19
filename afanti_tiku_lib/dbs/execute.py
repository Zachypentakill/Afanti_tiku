# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import logging


class MysqlPingError(Exception): pass

def ping(mysql_conn):
    try:
        result = mysql_conn.ping()
        if mysql_conn.__module__.startswith('MySQLdb'):
            if result is None:
                return True
            else:
                return False
        elif mysql_conn.__module__.startswith('cymysql'):
            if result is True:
                return True
            else:
                return False
        else:
            return result
    except Exception as err:
        logging.error('[execute.ping]: {}'.format(err))
        return False


def execute(mysql_conn, sql, values=None, commit=False, throw=True):
    if not ping(mysql_conn):
        if throw is True:
            raise MysqlPingError()
        else:
            return None

    cursor = mysql_conn.cursor()

    try:
        if values is not None:
            cursor.execute(sql, values)
        else:
            cursor.execute(sql)

        result = cursor.fetchall()

        if commit is True:
            mysql_conn.commit()

        return result
    except Exception as err:
        logging.error('[execute.execute]: {}'.format(err))
        if throw is True:
            raise err
        else:
            return None
    finally:
        cursor.close()

