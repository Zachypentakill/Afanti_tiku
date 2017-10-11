# -*- coding: utf-8 -*-

import asyncio
import logging
import json

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs import html_archive
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.html.extract import get_html_element

from adsl_server.proxy import Proxy

from login import login


LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/achihuo_mini.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()

_proxy = Proxy()

INFOS = (
    {'key': '初中语文', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 189, 'subj': '初中语文', 'aft_subj_id': 1,},
    {'key': '初中数学', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 193, 'subj': '初中数学', 'aft_subj_id': 2,},
    {'key': '初中英语', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 194, 'subj': '初中英语', 'aft_subj_id': 3,},
    {'key': '初中物理', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 195, 'subj': '初中物理', 'aft_subj_id': 5,},
    {'key': '初中化学', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 196, 'subj': '初中化学', 'aft_subj_id': 6,},
    {'key': '初中生物', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 197, 'subj': '初中生物', 'aft_subj_id': 9,},
    {'key': '初中政治', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 198, 'subj': '初中政治', 'aft_subj_id': 10,},
    {'key': '初中历史', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 199, 'subj': '初中历史', 'aft_subj_id': 8,},
    {'key': '初中地理', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 200, 'subj': '初中地理', 'aft_subj_id': 7,},
    {'key': '高中语文', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 109, 'subj': '高中语文', 'aft_subj_id': 21,},
    {'key': '高中数学', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 161, 'subj': '高中数学', 'aft_subj_id': 22,},
    {'key': '高中英语', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 165, 'subj': '高中英语', 'aft_subj_id': 23,},
    {'key': '高中物理', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 166, 'subj': '高中物理', 'aft_subj_id': 25,},
    {'key': '高中化学', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 167, 'subj': '高中化学', 'aft_subj_id': 26,},
    {'key': '高中生物', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 168, 'subj': '高中生物', 'aft_subj_id': 29,},
    {'key': '高中政治', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 169, 'subj': '高中政治', 'aft_subj_id': 30,},
    {'key': '高中历史', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 170, 'subj': '高中历史', 'aft_subj_id': 28,},
    {'key': '高中地理', 'grade': '全部', 'limit': 100, 'skip':0, 'subj_id': 171, 'subj': '高中地理', 'aft_subj_id': 27,},
)

PARAM = ('Key={key}&Subject={subj}&QuestionTypes=&Difficulty=&Year='
         '&Grade={grade}&Type=&Area=&subject_id={subj_id}'
         '&Limit={limit}&Skip={skip}')

INTERNAL = 2 * 24 * 60 * 60


class Dz101QuestionMiniSpider(AsyncLoop):

    NAME = 'dz101_question_mini_spider'

    def __init__(self):
        super(Dz101QuestionMiniSpider, self).__init__(concurrency=2, cache_backend='ssdb')
        self.cookies = login('15542652940', 'www888xxx')


    async def run(self):
        for info in INFOS:
            asyncio.ensure_future(self.get_pages(info))


    async def get_pages(self, info):
        no_new_question = 0
        page_num = 0
        N = 0

        while True:
            if no_new_question > 30:
                no_new_question = 0
                page_num = 0
                await asyncio.sleep(INTERNAL)
                continue

            ninfo = dict(info)
            ninfo['skip'] = page_num * 100

            item = make_page_item(ninfo)

            logging.info('[get_pages]: {}, {}'.format(info['key'], page_num))

            item.proxy = 'http://' + '119.7.227.133:9990' # _proxy.get(server_id=105)
            item.cookies = self.cookies

            with await self.lock:
                await asyncio.sleep(10)
                resp = await self.async_web_request(item, check_html=check_pg)
            if not (resp and resp.content):
                continue

            html_string = resp.text

            if not N:
                s = html_string.rfind('</div>|*|') + len('</div>|*|')
                e = html_string.find('|', s)
                qs_num = html_string[s:e]
                if not qs_num:
                    logging.warn('not qs_num: {}'.format(
                        json.dumps(item.json(), ensure_ascii=False)))
                    continue
                N = int(qs_num) + 100

            if page_num * 100 > N:
                await asyncio.sleep(INTERNAL)
                continue

            questions = get_html_element(
                '<div [^<>]*class="Problems_item"',
                html_string,
                regex=True
            )

            has_qs = False
            for qs in questions:
                s = qs.find('<tt>') + 4
                e = qs.find('</tt>')
                qid = qs[s:e]
                hkey = 'dz101_question_{}'.format(qid)

                if is_archived(hkey):
                    continue

                has_qs = True
                logging.info('[question]: {}, {}'.format(info['key'], hkey))
                save_html(hkey, qs, ninfo['aft_subj_id'], ninfo)

            if not has_qs:
                no_new_question += 1
            else:
                no_new_question = 0

            page_num += 1
            logging.info('[page done]')


def make_page_item(info):
    url = 'http://www.dz101.com/zujuan/zhishidian/Problems'
    item = Item(dict(
        method = 'GET',
        url = url + '?' + PARAM.format(**info),
        max_retry = 2,
        timeout = 120,
    ))
    return item


def check_pg(html_string):
    return 'class="Problems_item"' in html_string


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


def save_html(url, html_string, subj_id, info, flag=0):
    mysql_conn = get_mysql_connection()

    info = json.dumps(info, ensure_ascii=False)
    sql, vals = html_archive.insert_sql(
        'dz101_spider_html_archive_table',
        dict(
            key = url,
            html = html_string,
            md5 = md5_string(html_string),
            subject = subj_id,
            source = 56,
            flag=flag,
            info = info,
        ), ignore=True
    )
    execute(mysql_conn, sql, values=vals)


def is_archived(url):
    mysql_conn = get_mysql_connection()

    cmd = 'select html_id from dz101_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=(url,))
    if result:
        return True
    else:
        return False

    # cmd = 'select question_id from question_pre.question where spider_url = %s and flag = 0'
    # result = execute(mysql_conn, cmd, values=(url,))
    # if result:
        # result = True
    # else:
        # result = False


if __name__ == '__main__':
    loop = Dz101QuestionMiniSpider()
    loop.start()
