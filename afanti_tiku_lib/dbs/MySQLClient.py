# -*- encoding:utf8 -*-

from afanti_tiku_lib.compat import compat_mysql

class MyDBException(Exception):
    '''自定义异常'''
    pass


class MultiColumnsError(MyDBException):
    pass


class Dict(dict):
    '''
    扩展dict，使其可以通过属性来访问字典的属性
    '''
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('"Dict" object has no attribute "{}"'.format(key))

    def __setattr__(self, key, value):
        self[key] = value


class _Engine(object):
    '''数据库链接对象'''
    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()


class MySQLClient(object):
    '''数据库客户端，实现了查询、更新操作'''
    def __init__(self, user, passwd, db, host, port, **kwargs):
        '''
        初始化数据库客户端
        user:用户名
        passwd:密码
        db:数据库名称
        host:数据库地址
        port:数据库监听地址
        '''
        params = dict(user=user, passwd=passwd, db=db, host=host, port=port)
        defaults = dict(use_unicode=True, charset='utf8')
        for k, v in defaults.items():
            params[k] = kwargs.pop(k, v)
        params.update(kwargs)
        self.params = params
        self.engine = _Engine(lambda: compat_mysql.connect(**params))
        self.conn = None

    def __is_connected(self):
        if not self.conn:
            return False
        else:
            try:
                result = self.conn.ping()
                if self.conn.__module__.startswith('MySQLdb'):
                    if result is None:
                        return True
                    else:
                        return False
                elif self.conn.__module__.startswith('cymysql'):
                    if result is True:
                        return True
                    else:
                        return False
                else:
                    return result
            except Exception as err:
                logging.error('[execute.ping]: {}'.format(err))
                return False

    def __exit__(self):
        if self.conn:
            if self.__is_connected():
                self.conn.close()

    def _get_conn(self):
        '''
        获得数据库连接
        用conn.ping() == None,如果失去鏈接就會拋出異常， 
        如果存在鏈接，複用該鏈接，否則新建鏈接
        '''
        if self.__is_connected():
            pass
        else:
            self.conn = self.engine.connect()

    def select_one(self, sql, *args):
        '''
        查询一条记录
        '''
        return self._select(sql, True, *args)

    def select(self, sql, *args):
        '''
        查询操作
        '''
        return self._select(sql, False, *args)

    def select_int(self, sql, *args):
        d = self._select(sql, True, *args)
        if len(d) != 1:
            raise MultiColumnsError('Except only one column')
        return d.values()[0]

    def insert(self, table, **kw):
        cols, args = zip(*kw.iteritems())
        sql = 'insert into {table} ({fields}) values ({values})'.format(
            table=table,
            fields=' ,'.join(['`%s`'%col for col in cols]),
            values=' ,'.join(['?' for _ in cols])
        )
        return self._update(sql, *args)

    def update(self, sql, *args):
        return self._update(sql, *args)

    def _select(self, sql, only_first, *args):
        self._get_conn()
        cursor = None
        sql = sql.replace('?', '%s')
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, args)
            if cursor.description:
                names = [x[0] for x in cursor.description]
            if only_first:
                values = cursor.fetchone()
                if not values:
                    return None
                return Dict(names, values)
            return [Dict(names, x) for x in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()

    def _update(self, sql, *args):
        self._get_conn()
        cursor = None
        sql = sql.replace('?', '%s')
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, args)
            r = cursor.rowcount
            try:
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise Exception(e)
            return r
        finally:
            if cursor:
                cursor.close()
