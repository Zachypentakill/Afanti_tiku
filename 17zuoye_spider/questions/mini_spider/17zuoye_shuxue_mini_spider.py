# -*- coding: utf-8 -*-

import json
import random
import time
import logging

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item
#from achihuo_mini.cache import Cache
#from achihuo_mini.utils import sync_text

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs import html_archive
from afanti_tiku_lib.dbs.execute import execute

from adsl_server.proxy import Proxy

from login import login

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/achihuo_mini_shuxue.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()

headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer': 'http://zx.17zuoye.com/teacher/assign/index?finalReview=1',
    'X-Requested-With': 'XMLHttpRequest',
}

INTERNALS = (10,11,12,13)

_proxy = Proxy()

class Zuoye17QuestionMiniSpider(AsyncLoop):

    NAME = 'zuoye17_shuxue_mini_spider'

    def __init__(self):
        super(Zuoye17QuestionMiniSpider, self).__init__(cache_backend='ssdb')
        self.concurrency = 10
        #self.cache_backend = 'ssdb'
        #self.cache = Cache()
        self.cookies = login('13287280744', 'iamam00')
        self.no_new_question = 0

    @property
    def task_internal(self):
        return random.choice(INTERNALS)

    async def run(self):
        return None   # has done, no do it again
        item = Item(dict(
            method = 'GET',
            url = 'http://zx.17zuoye.com/teacher/assign/books?grade_id=0&_={}'.format(int(time.time() * 1000)),
            headers = headers,
            cookies = self.cookies,
        ))

        while True:
            resp = await self.async_web_request(item)
            js = json.loads(resp)
            #js = json.loads(sync_text(resp))
            if js['error_code'] != 0 or js['success'] != True:
                logging.error('[get_pages]: {}\n{}'.format(item.data), json.dumps(js, ensure_ascii=False))
                item.proxy = 'http://' + _proxy.get()
                self.stop()
            else:
                break

        for book in js['data']['books']:
            book['subject'] = 2
            item = Item(dict(
                method = 'POST',
                url = 'http://zx.17zuoye.com/teacher/assign/searchQuestions',
                data = 'book_id={}&lesson_id={}&page=1'.format(book['_id'],
                                                               book['series_id']),
                headers = headers,
                info = book,
                cookies = self.cookies,
                max_retry = 2,
                timeout = 10,
            ))
            self.add_task('get_pages', item)

    async def get_pages(self, item):
        item.proxy = 'http://' + _proxy.get()
        item.max_retry = 2
        item.timeout = 10
        item.cookies = self.cookies
        logging.info('get_pages: ' + item.data)

        resp = await self.async_web_request(item)
        if resp is None:
            item.proxy = 'http://' + _proxy.get()
            self.add_task('get_pages', item)
            return None

        html_string = resp
        #html_string = sync_text(resp)
        if not html_string:
            item.proxy = 'http://' + _proxy.get()
            self.add_task('get_pages', item)
            return None

        js = json.loads(html_string)
        if js['error_code'] != 0 or js['success'] != True:
            logging.error('[get_pages]: {}\n{}'.format(item.data), json.dumps(js, ensure_ascii=False))
            item.proxy = 'http://' + _proxy.get()
            self.add_task('get_pages', item)
            self.stop()
            return None

        for page_num in range(1, int(js['data']['page_count'])):
            qs_item = Item(dict(
                method = 'POST',
                url = 'http://zx.17zuoye.com/teacher/assign/searchQuestions',
                data = 'book_id={}&lesson_id={}&page={}'.format(item.info['_id'],
                                                                item.info['series_id'],
                                                                page_num),
                headers = headers,
                cookies = self.cookies,
                info = item.info,
                max_retry = 2,
                timeout = 10,
            ))
            self.add_task('get_questions', qs_item)


    async def get_questions(self, item):
        if self.no_new_question > 5:
            return None

        item.proxy = 'http://' + _proxy.get()
        item.max_retry = 2
        item.timeout = 10
        item.cookies = self.cookies
        logging.info('get_questions: ' + item.data)

        resp = await self.async_web_request(item)
        if resp is None:
            item.proxy = 'http://' + _proxy.get()
            self.add_task('get_questions', item)
            return None

        html_string = resp
        #html_string = sync_text(resp)
        if not html_string:
            item.proxy = 'http://' + _proxy.get()
            self.add_task('get_questions', item)
            return None

        js = json.loads(html_string)
        if js['error_code'] != 0 or js['success'] != True:
            logging.error('[get_pages]: {}\n{}'.format(item.data, js))
            item.proxy = 'http://' + _proxy.get()
            self.add_task('get_questions', item)
            self.stop()
            return None

        no_new = True
        for qs in js['data']['questions']:
            for s_qs in qs['qs']:
                _id = s_qs['_id']
                if is_archived('17zuoye_qs_' + _id):
                    continue

                no_new = False
                save_html(s_qs,
                          item.info,
                          json.dumps(item.json(), ensure_ascii=False))

        if no_new:
            self.no_new_question += 1


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


def save_html(js, info, request_info, flag=0):
    mysql_conn = get_mysql_connection()

    html = json.dumps(js, ensure_ascii=False)
    sql, vals = html_archive.insert_sql(
        '17zuoye_spider_html_archive_table',
        dict(
            key = '17zuoye_qs_{}'.format(js['_id']),
            html = html,
            md5 = md5_string(html),
            subject = info['subject'],
            request_info = request_info,
            source = 53,
            flag=flag,
        ), ignore=True
    )
    execute(mysql_conn, sql, values=vals)


def is_archived(testid):
    mysql_conn = get_mysql_connection()

    cmd = 'select html_id from 17zuoye_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=('17zuoye_qs_{}'.format(testid),))
    return result

    # cmd = 'select question_id from question_pre.question where spider_url = %s and flag = 0'
    # mysql_cursor.execute(cmd, (url,))
    # result = mysql_cursor.fetchall()
    # if result:
        # result = True
    # else:
        # result = False


if __name__ == '__main__':
    loop = Zuoye17QuestionMiniSpider()
    loop.start()
