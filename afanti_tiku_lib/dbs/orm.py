# -*- coding:utf8 -*-
import logging

import aiomysql
from pymysql.err import IntegrityError


logger = logging.getLogger('sql')


class ORMError(Exception):
    pass


class DuplicateError(ORMError):
    pass


class SQLClientError(ORMError):
    pass


# 用于存储数据库连接池的变量
sql_pool = None


# 接受必要参数，创建数据库连接池
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
            raise SQLClientError(
                    'You must provide %s' % key)

    max_size = kw.get('maxsize', 5)
    more_config = dict(
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=max_size if max_size <=10 else 10,
        minsize=kw.get('minsize', 1),
        loop=loop
    )
    db_info.update(more_config)
    logger.info('create database %s connection pool...', host)
    _pool = await aiomysql.create_pool(**db_info)

    global sql_pool
    sql_pool = _pool
    return _pool


# 执行sql查询操作的函数
async def select(sql, *args, size=None):
    global sql_pool
    sql = sql.replace('?', '%s') # 使用?作为占位符
    async with sql_pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await cur.execute(sql, args or ())
                if isinstance(size, int):
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
                raise err


# 执行更新操作的函数
async def execute(sql, *args, autocommit=True):
    global sql_pool
    sql = sql.replace('?', '%s')
    async with sql_pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor() as cur:
                await cur.execute(sql, args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except IntegrityError as err:
            raise DuplicateError(err)
        except Exception as err:
            logger.warning(
               'occured error: `%s` when execute %s, args: %s',
                err, sql, args
            )
            if not autocommit:
                await conn.rollback()
            raise err
        return affected


# 定义插入操作
async def insert(table, sql_ignore=False, autocommit=True, **kwargs):
    keys, values = zip(*kwargs.items())
    sql = 'insert '
    if sql_ignore:  # 使用ignore操作可以避免重复插入时报Duplicate Error
        sql += ' ignore '
    sql += 'into {table}({keys}) values ({values})'.format(
                table=table,
                keys=', '.join(('`%s`' % key for key in keys)),
                values=', '.join(('?' for _ in values))
            )
    return await execute(conn, sql, *values)


# 定义orm的基础字段
class Field(object):
    def __init__(self, **kw):
        self.name = kw.get('name', None)
        self.coloumn_type = kw['coloumn_type']  # 字段类型
        self.primary_key = kw.get('primary_key', False)  # 是否为主键
        self.default_ = kw.get('default', None) # 默认值，可以是函数或者变量
        self.auto_increment = kw.get('auto_increment', False)  # 是否自增
        self.updatetable = kw.get('updateable', False) # 是否可以更新
        self.nullable = kw.get('nullable', False) # 是否可以为空
        self.ddl = kw['ddl']  # 字段的类型定义，如char(32)等
        self.comment = kw.get('commment', '')  # 字段的说明

    @property
    def default(self):
        default_ = self.default_
        default = default_() if callable(default_) else default_
        return default

    def __str__(self):
        return '<%s: %s, %s default (%s)>' %(
                   self.__class__.__name__,
                   self.name,
                   self.ddl,
                   self.default
               )

# 目前并没有对orm中定义的字段类型进行类型验证
# 定义字段类型只用于展示表的定义
# Integer字段的primary_key以及auto_increment属性都为真时，插入操作会忽略对应字段


class IntegerField(Field):
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = 0
        if kw.get('primary_key') and kw.get('auto_increment'):
            auto_increment = True
        else:
            auto_increment = False
        kw['auto_increment'] = auto_increment
        kw['coloumn_type'] = 'integer'
        if 'ddl' not in kw:
            kw['ddl'] = 'int(20)'
        super(IntegerField, self).__init__(**kw)


class StringField(Field):
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = ''
        kw['primary_key'] = False
        kw['coloumn_type'] = 'string'
        if 'ddl' not in kw:
            kw['ddl'] = 'varchar(255)'
        super(StringField, self).__init__(**kw)


class TextField(Field):
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = ''
        kw['primary_key'] = False
        kw['coloumn_type'] = 'text'
        if 'ddl' not in kw:
            kw['ddl'] = 'mediumtext'
        super(TextField, self).__init__(**kw)


# 定义orm需要使用的元类
# 将model的类型定义存储在__fields__变量中
class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        # 提前给table_name加上``，来处理跨数据库操作
        table_name = attrs.get('__table__', None) or name
        if not table_name:
            raise ORMError('no __table__ provied')
        elif table_name.count('`') == 0:
            table_name = '`%s`' % table_name
        elif table_name.count('`') % 2 in [2, 4]:
            pass
        else:
            raise ORMError('bad __table__ argument with %s `' % len(table_name.count('`')))
        mappings = dict()
        fields = []
        primary_key = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    if primary_key:
                        raise RuntimeError('Duplicate primary key')
                    primary_key = k
                else:
                    fields.append(k)
        if not primary_key:
            raise RuntimeError('Cannot find primary_key')

        for k in fields:
            attrs.pop(k)
        attrs.pop(primary_key)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))

        attrs['__mappings__'] = mappings
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        attrs['escaped_fields'] = escaped_fields
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return(self[key])
        except KeyError:
            raise AttributeError('Model object has no attribute: %s' % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value

    @classmethod
    async def get(cls, pk):
        '''通过主键查找一条记录
        '''
        sql = 'select `%s`, %s from %s where `%s` = ? limit 1' % (
                    cls.__primary_key__,
                    ', '.join(cls.escaped_fields),
                    cls.__table__,
                    cls.__primary_key__
              )
        res = await select(sql, pk, size=1)
        if not res:
            return None
        return cls(**res)

    @classmethod
    async def filter_by(cls, sql, *args, **kwargs):
        '''通过sql查询一个或多个对象, limit参数可以控制个数
        '''
        base_sql = 'select `%s`, %s from %s ' % (
                        cls.__primary_key__,
                        ', '.join(cls.escaped_fields),
                        cls.__table__
                    )
        sql = base_sql + sql
        limit = kwargs.get('limit', None)
        res = await select(sql, *args, size=limit)
        if limit == 1:
            if not res:
                return None
            return cls(**res)
        if not res:
            return []
        return [cls(**item) for item in res]

    async def save(self):
        '''保存一条记录，必要时使用默认值, 自增主键交由数据库处理
        '''
        args = list(map(self.getValueOrDefault, self.__fields__))
        primary_key_field = self.__mappings__[self.__primary_key__]
        base_sql = 'insert into %s ' % self.__table__
        if primary_key_field.auto_increment:
            sql = '(%s) values (%s)' % (
                     ', '.join(self.escaped_fields),
                     ', '.join(('?' for _ in range(len(self.__fields__))))
                   )
        else:
            sql = '(`%s`, %s) values (%s)' %(
                     self.__primary_key__,
                     ', '.join(self.escaped_fields),
                     ', '.join(('?' for _ in range(len(self.__fields__))))
                  )
            primary_key_value = self.getValueOrDefault(self.__primary_key__)
            args.append(primary_key_value)
        sql = base_sql + sql
        rows = await execute(sql, *args)
        if rows != 1:
            logging.warning('failed to update by primary_key')

    async def update(self):
        '''更新一条记录
        '''
        base_sql = 'update %s set ' % self.__table__
        base_sql += ', '.join(
            ('%s = ?' % field for field in self.escaped_fields)
        )
        sql = base_sql + ' where %s = ? ' %  self.__primary_key__
        args =  list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(sql, *args)
        if rows != 1:
            logging.warning('failed to update by primary_key')

    @classmethod
    async def count_by(cls, sql, *args, **kwargs):
        '''技术操作，通过sql的条件，返回对应的数目
        '''
        base_sql = 'select count(1) as count from %s ' %(
            cls.__table__
        )
        sql = base_sql + sql
        limit = kwargs.get('limit', 1)
        res = await select(sql, *args, size=limit)
        count = res['count']
        return count


def fake_select(sql, *args, **kwargs):
    '''测试用的假查询操作 
    示例:sql = 'select `id`, `path` from `table`'
    结果：{'id': 'id', 'path': 'path'}
    '''
    import re
    pattern = re.compile('select(.+?)\sfrom\s')
    res = pattern.findall(sql)[0]
    fields = re.split('\s', res)
    fields = [field.replace('`', '').replace(',', '') for field in fields]
    fields = list(
        filter(
            lambda m: m, 
            map(
                lambda m: m.replace('`', ''), 
                fields
            )
        )
    )
    fields = {item: item for item in fields}
    return fields


'''
示例
class Question(Model):
    __table__ = '`question_pre`.`question`'

    id = IntegerField(primary_key=True, auto_increment=True)
    image_id = StringField()
    question_body = TextField()
    answer = TextField()
    analy = TextField()
    update_time = IntegerField()

    async def save(self, *args, **kwargs):
        self.update_time = int(time.time())
        await super(Question, self).save(*args, **kwargs)


from afanti_tiku_lib.dbs.simple_db_key_store import get_db_info
db_info = get_db_info('question')
# 字典格式，格式为{'host': '', 'port': '', 'user': '', 'passwd': ''}

await create_pool(**db_info)

q = Question(image_id='aa', question_body='da', answer='ads', analy='asda')
await q.save()

q = Question.filter_by('where image_id=?', image_id, limit=1)
q = q.question_body = 'dadadsa'
q = await q.update()  # 不能使用save来执行更新

'''
