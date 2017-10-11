# -*- coding: utf-8 -*-

import logging
import json

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item
#from achihuo_mini.utils import sync_text

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs import html_archive
from afanti_tiku_lib.dbs.execute import execute

from adsl_server.proxy import Proxy
from user_agent_lib.user_agent import UserAgent

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/achihuo_mini_vko.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()

_proxy = Proxy()

user_agent = UserAgent()

HEADERS = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
'Referer': 'http://tiku.vko.cn/',
'X-Requested-With': 'XMLHttpRequest',
'Connection': 'keep-alive',
}


class VkoMiniSpider(AsyncLoop):

    NAME = 'vko_mini_spider'

    def __init__(self):
        super(VkoMiniSpider, self).__init__(concurrency=30, cache_backend='ssdb')


    async def run(self):
        return


    async def get_question(self, item):
        logging.info('[get_question]: ' + item.url)

        item.proxy = 'http://' + _proxy.get()
        item.headers = dict(HEADERS)
        item.headers['User-Agent'] = user_agent.get()
        resp = await self.async_web_request(item, check_html=check_js)

        if not (resp and resp.text):
            self.add_task('get_question', item, task_name=item.url)
            return None

        html_string = resp.text
        if not html_string.startswith('null({'):
            self.task_done(item.url)
            return None

        js = json.loads(html_string[5:-1])

        if not js.get('examsResolve') and not js.get('answer'):
            self.add_task('get_question', item, task_name=item.url)
            return None

        key = 'vko_qs_{}'.format(js['id'])

        save_html(key, js)

        logging.info('question done')
        self.task_done(item.url)


def check_js(html_string):
    if html_string.startswith('null('):
        return True
    elif '微课网在线教育' in html_string:
        return True
    else:
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


def save_html(key, js, flag=0):
    mysql_conn = get_mysql_connection()

    html_string = json.dumps(js, ensure_ascii=False, sort_keys=True)

    sql, vals = html_archive.insert_sql(
        'vko_spider_html_archive_table',
        dict(
            key          = key,
            html         = html_string,
            md5          = md5_string(html_string),
            source       = 74,
            flag         = flag,
        ), ignore=True
    )
    execute(mysql_conn, sql, values=vals)


def is_archived(url):
    mysql_conn = get_mysql_connection()

    cmd = 'select html_id from vko_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=(url,))
    return result


if __name__ == '__main__':
    loop = VkoMiniSpider()
    loop.start()
