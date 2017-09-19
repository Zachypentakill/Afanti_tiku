# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import


def select_sql(table, cols, condition=None):

    query = ', '.join(['`{}`'.format(col) for col in cols])
    sql_template = 'select {} from {}{}'
    if condition is None:
        sql = sql_template.format(query, table, '')
    else:
        sql = sql_template.format(query, table, ' ' + condition)

    return sql


def insert_sql(table, items, ignore=False):

    cols = list(items.keys())
    values = [items[col] for col in cols]

    query = ', '.join(['`{}`'.format(col) for col in cols])
    sql_template = 'insert{}into {} ({}) values ({})'
    sql = sql_template.format((' ignore ', ' ')[ignore is False],
                              table,
                              query,
                              ', '.join(['%s'] * len(values)))
    return sql, values


def replace_sql(table, items):

    cols = list(items.keys())
    values = [items[col] for col in cols]

    query = ', '.join(['`{}`'.format(col) for col in cols])
    sql_template = 'replace into {} ({}) values ({})'
    sql = sql_template.format(table, query,
                              ', '.join(['%s'] * len(values)))
    return sql, values


def update_sql(table, items, where):
    '''
    `where` is necessarily for safe
    '''

    cols = list(items.keys())
    values = [items[col] for col in cols]

    query = ', '.join(['`{}` = %s'.format(col) for col in cols])
    sql_template = 'update {} set {} {}'
    sql = sql_template.format(table, query, where)
    return sql, values

