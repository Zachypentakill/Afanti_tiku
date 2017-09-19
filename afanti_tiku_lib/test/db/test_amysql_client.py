# -*- coding:utf8 -*-
import asyncio
import json
import uuid

import afanti_tiku_lib.dbs.AMySQLClient as amysql
from afanti_tiku_lib.dbs.simple_db_key_store import get_db_info

question_db_info = get_db_info('question')
question_db_info['db'] = 'question_pre'


_pool = None
table =  '`test`.`21_century_question_20151013_test`'


async def test_select(loop):
    global _pool
    sql = 'select * from `question_pre`.`question` order '\
          'by question_id limit 1'
    res = await amysql.select(_pool, sql, size=10)
    with open('res.dat', 'w') as f:
        f.write(json.dumps(res))


async def test_insert(loop):
    global _pool
    global table
    spider_url = uuid.uuid4().hex
    question_dict = {
        'answer_all_html': 'test_aiomysql',
        'dianping': 'test',
        'exam_city': '',
        'exam_year': -1,
        'fenxi': '',
        'jieda': '',
        'knowledge_point': '',
        'option_html': '',
        'question_html': '',
        'question_quality': 0,
        'question_type': 0,
        'spider_source': 3,
        'spider_url': spider_url,
        'subject': 9,
        'zhuanti': ''
    }
    await amysql.insert(_pool, table, **question_dict)
    sql = 'select * from {table} where spider_url = %s'.format(table=table)
    res = await amysql.select(_pool, sql, spider_url, size=1)
    assert res['spider_url'] == spider_url
    print('insert test passed')


async def test_delete(loop):
    global _pool
    global table
    sql = 'select question_id from {table} order by question_id desc limit 1'.format(
                 table=table)
    question_id = await amysql.select(_pool, sql, size=1)
    question_id = question_id.get('question_id')
    print(question_id)
    sql = 'delete from {table} where question_id = %s limit 1'.format(table=table)
    await amysql.execute(_pool, sql, question_id)
    sql = 'select * from {table} where question_id =%s'.format(table=table)
    res = await amysql.select(_pool, sql, question_id, size=1)
    assert res == None
    print('delete test passed')


async def main(loop):
    global _pool
    try:
        _pool = await amysql.create_pool(loop, **question_db_info)
        await test_insert(loop)
        await test_insert(loop)
        await test_delete(loop)
        await test_select(loop)
    finally:
        if _pool:
            _pool.close()
            await _pool.wait_closed()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
