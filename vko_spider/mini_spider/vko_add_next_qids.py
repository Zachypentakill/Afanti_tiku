# -*- coding: utf-8 -*-

import requests

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item
from vko_spider.mini_spider.vko_mini_spider import VkoMiniSpider

HEADERS = {
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Accept': '*/*',
'X-Requested-With': 'XMLHttpRequest',
'Connection': 'keep-alive',
'Referer': 'http://tiku.vko.cn/',
}

URL = 'http://tiku.vko.cn/resolve/{}'

class VkoMiniSpider(AsyncLoop):

    NAME = 'vko_mini_spider'

    def __init__(self):
        super(VkoMiniSpider, self).__init__(concurrency=30, cache_backend='ssdb')


def make_item(qid):
    url = URL.format(qid)
    item = Item(dict(
        method = 'GET',
        url = url,
        max_retry = 2,
        timeout = 60,
    ))
    return item


def request(qid):
    url = URL.format(qid)
    resp = requests.get(url, headers=HEADERS)
    return resp.text


def find_max_qid():
    min_qid = 1
    max_qid = 1000000

    def binary_search(mnq, mxq):
        if mxq - mnq <= 1:
            return mxq

        mid = (mxq + mnq) // 2
        print(mid)
        html = request(mid)
        if not html.startswith('null('):
            return binary_search(mnq, mid)
        else:
            return binary_search(mid, mxq)

    return binary_search(min_qid, max_qid)


def main():
    loop = VkoMiniSpider()

    max_qid = find_max_qid()
    for qid in range(1, max_qid):
        item = make_item(qid)
        loop.add_task('get_question', item, task_name=item.url, repeat=False)


def test():
    max_qid = find_max_qid()
    print('max_qid', max_qid)


if __name__ == '__main__':
    main()
    # test()
