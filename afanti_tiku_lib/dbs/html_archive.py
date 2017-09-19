# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import


HTML_ARCHIVE_COLS = (('source', 0),
                     ('subject', 0),
                     ('html', ''),
                     ('md5', ''),
                     ('key', ''),
                     ('request_info', ''),
                     ('info', ''),
                     ('flag', 0),
                     ('flag_str', ''),)


def insert_sql(table, cols, ignore=False):

    sql_template = 'insert{}into %s (%s) values ({})' % (table, ', '.join(
        ['`{}`'.format(col[0]) for col in HTML_ARCHIVE_COLS]))

    col_vals = [(cols.get(col[0]) or col[1]) for col in HTML_ARCHIVE_COLS]
    sql = sql_template.format((' ignore ', ' ')[ignore is False],
                              ', '.join(['%s'] * len(HTML_ARCHIVE_COLS)))
    return sql, col_vals


def replace_sql(table, cols, ignore=False):

    sql_template = 'replace into %s (%s) values ({})' % (table, ', '.join(
        ['`{}`'.format(col[0]) for col in HTML_ARCHIVE_COLS]))

    col_vals = [(cols.get(col[0]) or col[1]) for col in HTML_ARCHIVE_COLS]
    sql = sql_template.format(', '.join(['%s'] * len(HTML_ARCHIVE_COLS)))
    return sql, col_vals


def upsert_sql(table, cols, ignore=False):

    sql_template = (
        'insert{}into %s (%s) values ({}) '
        'on duplicate key update %s' % (table,
            ', '.join(['`{}`'.format(col[0]) for col in HTML_ARCHIVE_COLS]),
            ', '.join(['`{}`'.format(col[0]) + ' = %s' for col in HTML_ARCHIVE_COLS]))
    )

    col_vals = [(cols.get(col[0]) or col[1]) for col in HTML_ARCHIVE_COLS]
    sql = sql_template.format((' ignore ', ' ')[ignore is False],
                              ', '.join(['%s'] * len(HTML_ARCHIVE_COLS)))
    return sql, col_vals * 2


class NotArgumentError(Exception): pass

def select_one_sql(table, cols, key=None, where=None):
    cols = ('`{}`'.format(col) for col in cols)
    sql_template = 'select {} from {} {{where}}'.format(', '.join(cols), table)

    sql = ''
    if key:
        sql = sql_template.format(where='where `key` = %s')

    elif where:
        sql = sql_template.format(where=where)

    else:
        raise NotArgumentError('key and where are None')

    return sql


