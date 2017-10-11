# -*- coding: utf-8 -*-

import re
import logging
import json

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item
#from achihuo_mini.utils import sync_text

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs import html_archive
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.html.extract import find_valid_elements

from models import ProxyPool

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/achihuo_mini.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()


SUBJS = [
'czdl', # 初中地理
'czhx', # 初中化学
'czls', # 初中历史
'czsw', # 初中生物
'czsx', # 初中数学
'czwl', # 初中物理
'czyw', # 初中语文
'czyy', # 初中英语
'czzz', # 初中政治
'gzdl', # 高中地理
'gzhx', # 高中化学
'gzls', # 高中历史
'gzsw', # 高中生物
'gzsx', # 高中数学
'gzwl', # 高中物理
'gzyw', # 高中语文
'gzyy', # 高中英语
'gzzz', # 高中政治
# 'lkzh', # 理科综合
# 'wkzh', # 文科综合
'xxsx', # 小学数学
]


re_page = re.compile(r'当前\(1/(\d+)\) 首页')
re_qid = re.compile(r'id="addBtn_(.+?)"')


class Manfen5ZujuanMiniSpider(AsyncLoop):

    NAME = 'manfen5_zujuan_mini_spider'

    def __init__(self):
        super(Manfen5ZujuanMiniSpider, self).__init__(concurrency=20, cache_backend='ssdb')
        self._proxy = ProxyPool(3 * 60)


    async def run(self):
        for subj in SUBJS:
            # 系统题目
            item = make_item(subj, 1, _type='xt')
            self.add_task('get_page', item, task_name=item.name, repeat=False)

            # 全品题目
            item = make_item(subj, 1, _type='qp')
            self.add_task('get_page', item, task_name=item.name, repeat=False)


    async def request(self, item):
        ip_port, proxy_obj = await self._proxy.get()
        item.headers = proxy_obj.headers
        item.cookies = proxy_obj.cookies
        item.proxy = 'http://' + ip_port

        resp = await self.async_web_request(item, check_html=check_qs)

        self._proxy.put(proxy_obj)

        return resp


    async def get_page(self, item):
        logging.info('[get_page]: ' + item.url)

        resp = await self.request(item)

        if not (resp and resp.text):
            self.add_task('get_page', item, task_name=item.name)
            return None

        html_string = resp.text

        qs_n = self.record_questions(html_string, item.subj)
        # logging.info('qs_n: {}, {}'.format(qs_n, item.url))

        if item.name.endswith('_1'):
            pages = int(re_page.search(html_string).group(1))
            for page in range(2, pages + 1):
                sub_item = make_item(item.subj, page, _type=item._type)
                self.add_task('get_page', sub_item,
                              task_name=sub_item.name, repeat=False)

        logging.info('page done')


    def record_questions(self, html_string, subj):
        qss = find_valid_elements(html_string, '<table ')
        n = 0
        for qs in qss:
            mod = re_qid.search(qs)
            if mod:
                qid = mod.group(1)
                key = 'manfen5_zujuan_qs_' + qid
                save_html(key, qs, {'subj': subj})
                n += 1
        return n


def make_item(subj, page, _type='xt'):
    # _type = None  系统题目
    # _type = 'qp'  全品题目
    if _type == 'qp':
        url = ('http://tiku.manfen5.com/zujuan/UserSTListAjax.aspx?'
               'type=getUserST&UnionID=10050&CourseID={}&ZSDZJType='
               '&ZSDZJID=&EndID=0&STTX=&STLeavel=&page={}').format(subj, page)
    elif _type == 'xt':
        url = ('http://tiku.manfen5.com/zujuan/STListAjax.aspx?'
               'type=getST&CourseID={}&ZSDZJType=&ZSDZJID='
               '&EndID=0&STTX=&STLeavel=&IsOnlineTest=&page={}').format(subj, page)

    item = Item(dict(
        method = 'POST',
        url = url,
        max_retry = 2,
        timeout = 80,
    ))
    item.subj = subj
    item._type = _type
    item.name = '{}_{}_{}'.format(subj, _type, page)
    return item


def check_qs(html_string):
    return '条记录 当前(' in html_string and '转到<input ' in html_string


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


def save_html(key, html_string, info, flag=0):
    mysql_conn = get_mysql_connection()

    info = json.dumps(info, ensure_ascii=False, sort_keys=True)

    sql, vals = html_archive.insert_sql(

        'manfen5_zujuan_spider_html_archive_table',
        dict(
            key          = key,
            html         = html_string,
            md5          = md5_string(html_string),
            info         = info,
            source       = 80,
            flag         = flag,
        ), ignore=True
    )
    execute(mysql_conn, sql, values=vals)


def is_archived(url):
    mysql_conn = get_mysql_connection()

    cmd = 'select html_id from manfen5_zujuan_spider_html_archive_table where `key` = %s and flag = 0'
    result = execute(mysql_conn, cmd, values=(url,))
    return result


if __name__ == '__main__':
    loop = Manfen5ZujuanMiniSpider()
    loop.start()
