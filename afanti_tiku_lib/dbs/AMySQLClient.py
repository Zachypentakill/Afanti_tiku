# -*- coding:utf8 -*-
import logging
import aiomysql


class AMySQLClientExcpetion(Exception):
    pass


logger = logging.getLogger('sql')


async def create_pool(loop, **kw):
    user = kw.get('user', '')
    password = kw.get('passwd', '')
    port = int(kw.get('port', 3306))
    host = kw.get('host', 'localhost')
    db = kw.get('db', '')

    db_info = dict(
        user=user,
        password=password,
        host=host,
        port=port,
        db=db,
    )

    for key, value in db_info.items():
        if not value:
            raise AMySQLClientExcpetion(
                    'You must provide %s' % key)

    more_config = dict(
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 5),
        minsize=kw.get('minsize', 1),
        loop=loop
    )
    db_info.update(more_config)
    logger.info('create database %s connection pool...', host)
    _pool = await aiomysql.create_pool(**db_info)
    return _pool


async def select(conn, sql, *args, size=None):
    async with conn.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await cur.execute(sql, args or ())
                if size:
                    if size == 1:
                        res = await cur.fetchone()
                    else:
                        res = await cur.fetchmany(size)
                else:
                    res = await cur.fetchall()
                return res
            except Exception as err:
                logger.warning(
                    'occured error: `%s` when execute sql: %s, args: %s',
                    err, sql, args
                )


async def execute(conn, sql, *args, autocommit=True):
    async with conn.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor() as cur:
                await cur.execute(sql, args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except Exception as err:
            logger.warning(
               'occured error: `%s` when execute %s, args: %s',
                err, sql, args
            )
            if not autocommit:
                await conn.rollback()
            raise err
        return affected


async def insert(conn, table, sql_ignore=False, autocommit=True, **kwargs):
    keys, values = zip(*kwargs.items())
    sql = 'insert '
    if sql_ignore:
        sql += ' ignore '
    sql += 'into {table}({keys}) values ({values})'.format(
                table=table,
                keys=', '.join(('`%s`' % key for key in keys)),
                values=', '.join(('%s' for _ in values))
            )
    return await execute(conn, sql, *values)
