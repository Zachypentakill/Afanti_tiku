# -*- coding: utf-8 -*-

import logging
import json

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs import html_archive
from afanti_tiku_lib.dbs.execute import execute

from adsl_server.proxy import Proxy

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/achihuo_mini.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()

_proxy = Proxy()


class GzywtkMiniSpider(AsyncLoop):

    NAME = 'gzywtk_mini_spider'

    def __init__(self):
        super(GzywtkMiniSpider, self).__init__(concurrency=10, cache_backend='ssdb')

    async def run(self):
        pass

    async def get_question(self, item):
        logging.info('[get_question]: ' + item.url)

        item.timeout = 120
        item.proxy = 'http://' + _proxy.get()
        resp = await self.async_web_request(item, check_html=check_qs)

        if not (resp and resp.text):
            self.add_task('get_question', item, task_name=item.url)
            return None

        html_string = resp.text

        # check answer
        if '答案尚未转成文字' not in html_string:
            save_html(item.url, html_string)

        self.task_done(item.url)


def check_qs(html_string):
    return '试题内容' in html_string


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


def save_html(key, html_string, flag=0):
    mysql_conn = get_mysql_connection()

    sql, vals = html_archive.insert_sql(
        'gzywtk_spider_html_archive_table',
        dict(
            key          = key,
            html         = html_string,
            md5          = md5_string(html_string),
            source       = 68,
            flag         = flag,
        ), ignore=True
    )
    execute(mysql_conn, sql, values=vals)


def is_archived(url):
    mysql_conn = get_mysql_connection()

    cmd = 'select html_id from gzywtk_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=(url,))
    return result


if __name__ == '__main__':
    loop = GzywtkMiniSpider()
    loop.start()
