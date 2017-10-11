# -*- coding: utf-8 -*-

import sys
import os
import re
import time
import logging

import requests

from achihuo_mini.item import Item
from achihuo_mini.async_loop import AsyncLoop

from adsl_server.proxy import Proxy

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/gzywtk_add_next_qids.log', filemode='a')

HEADERS = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Referer': 'http://www.gzywtk.com/',
}

URL = 'http://www.gzywtk.com/tmshow/{}.html'

_proxy = Proxy()


class GzywtkMiniSpider(AsyncLoop):

    NAME = 'gzywtk_mini_spider'

    def __init__(self):
        super(GzywtkMiniSpider, self).__init__(concurrency=10, cache_backend='ssdb')


def request(url):
    while True:
        proxy = 'http://' + _proxy.get()
        try:
            resp = requests.get(url, headers=HEADERS, proxies={'http': proxy})
            if resp.status_code == 200:
                return resp.text
            else:
                continue
        except Exception:
            continue


def make_item(qid):
    url = URL.format(qid)
    item = Item(dict(
        method = 'GET',
        url = url,
        headers = HEADERS,
        max_retry = 2,
        timeout = 20,
    ))
    return item

re_qid = re.compile(r'/tmshow/(\d+).html')
re_page = re.compile(r'\(共(\d+)页\)')
def find_qids(page):
    time.sleep(1)
    url = 'http://www.gzywtk.com/tmlist/{}.html'.format(page)
    html = request(url)
    return set(re_qid.findall(html))


def main():
    loop = GzywtkMiniSpider()

    html = request('http://www.gzywtk.com/kaodian/tmlist.aspx')
    pages = int(re_page.search(html).group(1))

    for page in range(1, pages + 1):
        qids = find_qids(page)
        logging.info(page)
        for qid in qids:
            item = make_item(qid)
            loop.add_task('get_question', item, task_name=item.url, repeat=False)


def add_task_from_file():
    loop = GzywtkMiniSpider()
    if os.path.exists('working/qids'):
        for qid in open('working/qids'):
            qid = qid.strip()
            if not qid:
                continue

            item = make_item(qid)
            loop.uncache_task(item.url)
            loop.add_task('get_question', item, task_name=item.url, repeat=False)


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        main()
    else:
        if argv[0] == '-i':
            add_task_from_file()
