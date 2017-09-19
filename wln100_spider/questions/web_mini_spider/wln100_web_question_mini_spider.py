# -*- coding: utf-8 -*-

import logging
import json
import random
import asyncio

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs import html_archive
from afanti_tiku_lib.dbs.execute import execute

from adsl_server.proxy import Proxy

from util import get_max_qid

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/achihuo_mini.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()

_proxy = Proxy()

HEADERS = {
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2486.0 Safari/537.36 Edge/12.10586',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}


# COOKIES = {
    # 'wln_aat_VERSIONID': '0',
    # 'PHPSESSID': '4lj27ntg1ap7c5bs4io26h49m5',
    # 'wln_aat_UID': '130218',
    # 'wln_aat_CODE': '7ca880b9c325a72a42483cdb11b413c3',
    # 'wln_aat_USER': 'jameda%40lillemap.net'
# }

# COOKIES = {'PHPSESSID': '2i3eq567v2idq5f8jjpppv9ml6', 'wln_aat_CODE': '7ca880b9c325a72a42483cdb11b413c3', 'wln_aat_USER': 'jameda%40lillemap.net', 'wln_aat_VERSIONID': '0', 'wln_aat_UID': '130218'}
# COOKIES = {'PHPSESSID': '93hvb52lvfr4hou21l91nn4ov1', 'a1027_pages': '1', 'a1027_times': '1', 'wln_aat_VERSIONID': '2', 'wln_aat_USER': 'natorigu%40leeching.net', 'wln_aat_UID': '98273', 'wln_aat_CODE': '75d5d4e63cab0738b7710a2601a0c6e2'}
COOKIES = {'PHPSESSID': '93hvb52lvfr4hou21l91nn4ov1', 'a1027_times': '2', 'wln_aat_VERSIONID': '2', 'a1038_times': '1', 'a1027_pages': '3', 'wln_aat_USER': 'natorigu%40leeching.net', 'wln_aat_UID': '98273', 'wln_aat_CODE': 'f668a8981cf76bc0b5669c5a7b0c22af'}

INTERNAL = 2 * 24 * 60 * 60


class Wln100WebQuestionMiniSpider(AsyncLoop):

    NAME = 'wln100_web_question_mini_spider'

    def __init__(self):
        super(Wln100WebQuestionMiniSpider, self).__init__(concurrency=100, cache_backend='ssdb')
        # self.stop()
        self.max_qid = 993138


    async def run(self):
        # await self.test()
        # return

        while True:
            max_qid = get_max_qid()
            for qid in range(self.max_qid, max_qid):
                if not is_qs_archived(qid):
                    self.add_task('get_question',
                                  qid,
                                  task_name=str(qid),
                                  repeat=False)

            self.max_qid = max_qid
            await asyncio.sleep(INTERNAL)


    async def test(self):
        await self.get_question(924825)


    async def get_question(self, qid):
        logging.info('[question]: {}'.format(qid))

        item = make_qs_item(qid)

        while True:
            # number = random.randint(2, 10)
            # proxy = _proxy.get_ip(server_id= number)
            # item.proxy = 'http://' + proxy.decode() + ':9990'
            item.proxy = 'http://' + _proxy.get()
            resp = await self.async_web_request(item, check_html=check_qs)
            if not (resp and resp.content):
                continue

            html_string = get_question_html(resp.text)
            if is_valid_html(html_string):
                key = 'wln100_qs_{}'.format(qid)

                save_html(key, html_string)

                if not is_as_archived(qid):
                    self.add_task('get_answer',
                                  qid,
                                  task_name='a_' + str(qid),
                                  repeat=False)

            break

        self.task_done(str(qid))
        logging.info('[question done]: {}'.format(qid))


    async def request(self, item, check_html):
        #180.110.19.190:9990
        proxy = 'http://' + '119.7.227.81:9990' # a105
        item.proxy = proxy
        item.cookies = COOKIES

        while True:
            with await self.lock:
                await asyncio.sleep(1)
                resp = await self.async_web_request(item, check_html=check_html)
                if not (resp and resp.content):
                    continue
                return resp


    async def get_answer(self, qid):
        logging.info('[ans]: {}'.format(qid))

        item = make_as_item(qid)
        item.headers['Referer'] = 'Referer:http://www.wln100.com/Test/{}.html'.format(qid)
        item.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        item.headers['X-Requested-With'] = 'XMLHttpRequest'

        while True:
            resp = await self.request(item, check_js)

            if not (resp and resp.content):
                continue

            js = resp.json()
            if js.get('info') == 'success' and js.get('status') == 1:
                key = 'wln100_as_{}'.format(qid)
                save_html(key, js)
                break
            else:
                logging.warn('[get_answer]: {}, {}'.format(qid, js))

        self.task_done('a_' + str(qid))
        logging.info('[ans done]: {}'.format(qid))


def make_qs_item(qid):
    item = Item(dict(
        method = 'GET',
        url = 'http://www.wln100.com/Test/{}.html'.format(qid),
        max_retry = 3,
        timeout = 30,
        headers = dict(HEADERS),
    ))
    return item


def make_as_item(qid):
    item = Item(dict(
        method = 'POST',
        url = 'http://www.wln100.com/Test/TestPreview/getOneTestById.html',
        data = 'id={}&width=500&s={}'.format(qid, random.random()),
        max_retry = 3,
        timeout = 30,
        headers = dict(HEADERS),
    ))
    return item


def check_qs(html_string):
    return '未来脑智能教学云平台' in html_string


def check_js(html_string):
    try:
        json.loads(html_string)
        return True
    except Exception:
        return False


def get_question_html(html_string):
    i = html_string.find('<!-- 百度分享 -->')
    if i == -1:
        return html_string
    else:
        return html_string[:i]


def is_valid_html(html_string):
    return '该试题信息不存在！' not in html_string


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


def save_html(key, cn, flag=0):
    mysql_conn = get_mysql_connection()

    if not isinstance(cn, str):
        cn = json.dumps(cn, ensure_ascii=False, sort_keys=True)

    sql, vals = html_archive.insert_sql(
        'wln100_spider_html_archive_table',
        dict(
            key          = key,
            html         = cn,
            md5          = md5_string(cn),
            source       = 52,
            flag         = flag,
        ), ignore=True
    )
    execute(mysql_conn, sql, values=vals)


def is_qs_archived(qid):
    mysql_conn = get_mysql_connection()

    key = 'wln100_qs_{}'.format(qid)

    cmd = 'select html_id from wln100_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=(key,))
    if result:
        return True
    else:
        return False


def is_as_archived(qid):
    mysql_conn = get_mysql_connection()

    key = 'wln100_as_{}'.format(qid)

    cmd = 'select html_id from wln100_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=(key,))
    if result:
        return True
    else:
        return False


if __name__ == '__main__':
    loop = Wln100WebQuestionMiniSpider()
    loop.start()
