# -*- coding: utf-8 -*-

import logging
import json
import random

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item
from achihuo_mini.cache import Cache
from achihuo_mini.utils import sync_text

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs import html_archive
from afanti_tiku_lib.dbs.execute import execute

from login import login

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/achihuo_mini.log', filemode='a')

mysql = CommonMysql('html_archive')
mysql_conn = mysql.connection()

headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}


class WlnQuestionMiniSpider(AsyncLoop):

    NAME = 'wln100_question_mini_spider'

    def __init__(self):
        super(WlnQuestionMiniSpider, self).__init__()
        self.concurrency = 8
        self.cache = Cache()
        self.cookies = login('15566679724', 'qazwsx')
        self.no_new_question = 0


    # async def run(self):
        # for item in iter_pre_item():
            # item.cookies = self.cookies
            # self.add_task('get_pages', item)

    async def run(self):
        rows = get_question_ids()
        for row in rows:
            testid = row[0][10:]
            if is_archived(testid):
                continue

            info = dict(aft_subid=row[1])
            as_item = Item(dict(
                method = 'POST',
                url = 'http://www.wln100.com/Home/Index/getOneTestById.html',
                data = 'id={}&width=500&s={}'.format(testid, random.random()),
                headers = headers,
                info = info,
                cookies = self.cookies,
            ))
            self.add_task('get_answer', as_item, testid)


    async def get_pages(self, item):
        data = item.data
        item.data = data.format(1, random.random())
        logging.info('get_pages: ' + item.data)

        resp = await self.async_web_request(item)
        if resp is None:
            self.add_task('get_pages', item)
            return None

        html_string = sync_text(resp)
        if not html_string:
            self.add_task('get_pages', item)
            return None

        js = json.loads(html_string)
        if js['info'] != 'success' or js['status'] != 1:
            logging.error('[get_pages]: {}\n{}'.format(item.data), json.dumps(js, ensure_ascii=False))
            self.add_task('get_pages', item)
            return None

        for page_num in range(1, int(js['data'][1]) // 20 + 1):
            qs_item = Item(dict(
                method = 'POST',
                url = 'http://www.wln100.com/Home/Index/getTestList.html',
                data = data.format(page_num, random.random()),
                info = item.info,
                headers = headers,
            ))
            self.add_task('get_questions', qs_item)


    async def get_questions(self, item):
        if self.no_new_question > 5:
            return None

        logging.info('get_questions: ' + item.data)

        resp = await self.async_web_request(item)
        if resp is None:
            self.add_task('get_questions', item)
            return None

        html_string = sync_text(resp)
        if not html_string:
            self.add_task('get_questions', item)
            return None

        js = json.loads(html_string)
        if js['info'] != 'success' or js['status'] != 1:
            logging.error('[get_pages]: {}'.format(item.data))
            self.add_task('get_questions', item)
            return None


        save_question(js, item.info, json.dumps(item.json(), ensure_ascii=False))

        no_new = True
        for qs in js['data'][0]:
            if is_archived(qs['testid']):
                continue

            no_new = False
            as_item = Item(dict(
                method = 'POST',
                url = 'http://www.wln100.com/Home/Index/getOneTestById.html',
                data = 'id={}&width=500&s={}'.format(qs['testid'], random.random()),
                headers = headers,
                info = item.info,
                cookies = self.cookies,
            ))
            self.add_task('get_answer', as_item, qs['testid'])

        if no_new:
            self.no_new_question += 1

    async def get_answer(self, item, testid):
        logging.info('get_answer: ' + item.data)

        resp = await self.async_web_request(item)
        if resp is None:
            self.add_task('get_answer', item)
            return None

        html_string = sync_text(resp)
        if not html_string:
            self.add_task('get_answer', item)
            return None

        js = json.loads(html_string)
        if js['info'] != 'success' or js['status'] != 1:
            logging.error('[get_pages]: {}'.format(item.data))
            self.add_task('get_answer', item)
            return None

        save_answer(js,
                    item.info,
                    json.dumps(item.json(), ensure_ascii=False),
                    testid)


def iter_pre_item():
    SUBJS = ({"SubjectID":"12","aft_subid":21,},
             {"SubjectID":"13","aft_subid":22,},
             {"SubjectID":"14","aft_subid":23,},
             {"SubjectID":"15","aft_subid":25,},
             {"SubjectID":"16","aft_subid":26,},
             {"SubjectID":"17","aft_subid":29,},
             {"SubjectID":"18","aft_subid":30,},
             {"SubjectID":"19","aft_subid":28,},
             {"SubjectID":"20","aft_subid":27,},)

    for info in SUBJS:
        item = Item(dict(
            method = 'POST',
            url = 'http://www.wln100.com/Home/Index/getTestList.html',
            data = 'sid={}&kid=0&tid=0&dtid=0&dif=0&o=0&page={{}}&sourceid=0&rand={{}}'.format(info['SubjectID']),
            info = info,
            headers = headers,
        ))
        yield item


def get_mysql_connection():
    global mysql
    global mysql_conn

    try:
        if mysql_conn.ping() is False:
            mysql_conn = mysql.connection()
        return mysql_conn
    except Exception:
        mysql_conn = mysql.connection()
        return mysql_conn


def save_question(js, info, request_info, flag=0):
    mysql_conn = get_mysql_connection()

    for qs in js['data'][0]:

        html = json.dumps(qs, ensure_ascii=False)
        sql, vals = html_archive.insert_sql(
            'wln100_spider_html_archive_table',
            dict(
                key = 'wln100_qs_{}'.format(qs['testid']),
                html = html,
                md5 = md5_string(html),
                subject = info['aft_subid'],
                request_info = request_info,
                source = 52,
                flag=flag,
            ), ignore=True
        )
        execute(mysql_conn, sql, values=vals)
        mysql_conn.commit()


def save_answer(js, info, request_info, testid, flag=0):
    mysql_conn = get_mysql_connection()

    html = json.dumps(js, ensure_ascii=False)
    sql, vals = html_archive.insert_sql(
        'wln100_spider_html_archive_table',
        dict(
            key = 'wln100_as_{}'.format(testid),
            html = html,
            md5 = md5_string(html),
            subject = info['aft_subid'],
            request_info = request_info,
            source = 52,
            flag=flag,
        ), ignore=True
    )
    execute(mysql_conn, sql, values=vals)
    mysql_conn.commit()


def get_question_ids():
    sql = 'select `key`, subject from wln100_spider_html_archive_table where `key` like \'wln100_qs_%\''
    rows = execute(mysql_conn, sql)
    return rows

def is_archived(testid):
    mysql_conn = get_mysql_connection()

    cmd = 'select html_id from wln100_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=('wln100_as_{}'.format(testid),))
    return result

    # cmd = 'select question_id from question_pre.question where spider_url = %s and flag = 0'
    # mysql_cursor.execute(cmd, (url,))
    # result = mysql_cursor.fetchall()
    # if result:
        # result = True
    # else:
        # result = False


if __name__ == '__main__':
    loop = WlnQuestionMiniSpider()
    loop.start()
