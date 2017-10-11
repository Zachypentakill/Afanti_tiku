# -*- coding: utf-8 -*-

import logging
import json
import time

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item
#from achihuo_mini.utils import sync_text

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs import html_archive
from afanti_tiku_lib.dbs.execute import execute

from adsl_server.proxy import Proxy
from user_agent_lib.user_agent import UserAgent

from models import get_cookies

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/achihuo_mini.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()

_proxy = Proxy()

user_agent = UserAgent()

HEADERS = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Accept': 'text/plain, */*; q=0.01',
'X-Requested-With': 'XMLHttpRequest',
'Connection': 'keep-alive',
'Referer': 'http://www.jtyhjy.com/sts/',
}


class JtyhjyMiniSpider(AsyncLoop):

    NAME = 'jtyhjy_mini_spider'

    def __init__(self):
        super(JtyhjyMiniSpider, self).__init__(concurrency=10, cache_backend='ssdb')
        self.cookies = get_cookies()
        self.last_time = time.time()

    async def run(self):
        pass

    async def get_page(self, item):
        logging.info('[get_page]: ' + item.name)

        item.headers = dict(HEADERS)
        item.headers['User-Agent'] = user_agent.get()
        item.cookies = self.cookies
        item.proxy = 'http://' + _proxy.get()
        resp = await self.async_web_request(item, check_html=check_js)

        if not (resp and resp.text):
            self.add_task('get_page', item, task_name=item.name)
            return None

        js = resp.json()

        try:
            if not js.get('success') or not js['data']['questionList']['rows']:
                tm = time.time()
                if tm - self.last_time > 1 * 60:
                    logging.info('[get_cookies]')
                    self.cookies = get_cookies()
                    self.last_time = time.time()
                self.add_task('get_page', item, task_name=item.name)
                return None
        except Exception:
            tm = time.time()
            if tm - self.last_time > 1 * 60:
                logging.info('[get_cookies]')
                self.cookies = get_cookies()
                self.last_time = time.time()
            self.cookies = get_cookies()
            self.add_task('get_page', item, task_name=item.name)
            return None

        for qs in js['data']['questionList']['rows']:
            key = 'jtyhjy_qs_' + str(qs['questionId'])
            save_html(key, qs, item.info)

        if item.name.endswith('_1'):
            for page in range(2, js['data']['questionList']['total'] // 1000 + 1):
                data = item.data.replace('page=1&', 'page={}&'.format(page), 1)
                name = item.name[:-1] + str(page)
                sub_item = make_item(item.url, data, item.info)
                sub_item.name = name
                self.add_task('get_page', sub_item,
                              task_name=sub_item.name, repeat=False)

        logging.info('page done, {}'.format(item.name))


def make_item(url, data, info):
    item = Item(dict(
        method = 'POST',
        url = url,
        data = data,
        info = info,
        max_retry = 2,
        timeout = 80,
    ))
    return item


def check_js(html_string):
    try:
        json.loads(html_string)
        return True
    except Exception:
        return False


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


def save_html(key, js, info, flag=0):
    mysql_conn = get_mysql_connection()

    html_string = json.dumps(js, ensure_ascii=False, sort_keys=True)
    info = json.dumps(info, ensure_ascii=False, sort_keys=True)

    sql, vals = html_archive.insert_sql(
        'jtyhjy_spider_html_archive_table',
        dict(
            key          = key,
            html         = html_string,
            md5          = md5_string(html_string),
            info         = info,
            source       = 78,
            flag         = flag,
        ), ignore=True
    )
    execute(mysql_conn, sql, values=vals)


def is_archived(url):
    mysql_conn = get_mysql_connection()

    cmd = 'select html_id from jtyhjy_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=(url,))
    return result


if __name__ == '__main__':
    loop = JtyhjyMiniSpider()
    loop.start()
