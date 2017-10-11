# -*- coding: utf-8 -*-

import time
import os
import sys
import json

import requests

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item

from models import get_cookies

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

SUBJS = [
 {'code': '01', 'disciplineId': 20, 'name': '初中语文', 'schoolType': '1'},
 {'code': '02', 'disciplineId': 21, 'name': '初中数学', 'schoolType': '1'},
 {'code': '03', 'disciplineId': 22, 'name': '初中英语', 'schoolType': '1'},
 {'code': '04', 'disciplineId': 23, 'name': '初中物理', 'schoolType': '1'},
 {'code': '05', 'disciplineId': 24, 'name': '初中化学', 'schoolType': '1'},
 {'code': '06', 'disciplineId': 25, 'name': '初中生物', 'schoolType': '1'},
 {'code': '07', 'disciplineId': 26, 'name': '初中政治', 'schoolType': '1'},
 {'code': '08', 'disciplineId': 27, 'name': '初中历史', 'schoolType': '1'},
 {'code': '09', 'disciplineId': 28, 'name': '初中地理', 'schoolType': '1'},
 {'code': '01', 'disciplineId': 20, 'name': '高中语文', 'schoolType': '2'},
 {'code': '02', 'disciplineId': 21, 'name': '高中数学', 'schoolType': '2'},
 {'code': '03', 'disciplineId': 22, 'name': '高中英语', 'schoolType': '2'},
 {'code': '04', 'disciplineId': 23, 'name': '高中物理', 'schoolType': '2'},
 {'code': '05', 'disciplineId': 24, 'name': '高中化学', 'schoolType': '2'},
 {'code': '06', 'disciplineId': 25, 'name': '高中生物', 'schoolType': '2'},
 {'code': '07', 'disciplineId': 26, 'name': '高中政治', 'schoolType': '2'},
 {'code': '08', 'disciplineId': 27, 'name': '高中历史', 'schoolType': '2'},
 {'code': '09', 'disciplineId': 28, 'name': '高中地理', 'schoolType': '2'},
 {'code': '10', 'disciplineId': 29, 'name': '高中文综', 'schoolType': '2'},
 {'code': '11', 'disciplineId': 50, 'name': '高中理综', 'schoolType': '2'}]


class JtyhjyMiniSpider(AsyncLoop):

    NAME = 'jtyhjy_mini_spider'


def request(method, url, **kwargs):
    while True:
        try:
            resp = requests.request(method, url, **kwargs)
            js = resp.json()
            return js
        except Exception:
            time.sleep(5)
            continue


def make_item(url, data, info):
    item = Item(dict(
        method = 'POST',
        url = url,
        data = data,
        info = info,
        max_retry = 2,
        timeout = 120,
    ))
    return item


def main():
    loop = JtyhjyMiniSpider()
    cookies = get_cookies()

    for subj in SUBJS:
        info_path = 'working/knowledges/{}_{}_{}'.format(
            subj['code'], subj['schoolType'], subj['disciplineId'])
        if os.path.exists(info_path):
            js = json.load(open(info_path))
        else:
            url = 'http://www.jtyhjy.com/sts/initPage_initQuestionPageForKnowledge.action'
            data = 'disciplineCode={}&disciplineType={}&disciplineId={}'.format(
                subj['code'], subj['schoolType'], subj['disciplineId'])
            js = request('POST', url, data=data, headers=HEADERS, cookies=cookies)
            if not js['success']:
                print('cookies is invalid')
                sys.exit()
            with open(info_path, 'w') as fd:
                json.dump(js, fd, indent=4, ensure_ascii=False)

        que_type_ids = '%2C'.join([str(j['queTypeId']) for j in js['data']['questionTypeList']])

        for kp in js['data']['knowledgeList']:
            data = ('disciplineCode={}&disciplineType={}&disciplineId={}'
                    '&page=1&rows=1000&flag=3&queTypeIds={}&difficults='
                    '&knowledgeIds={}&knowledgeLevel=1').format(
                        subj['code'], subj['schoolType'],
                        subj['disciplineId'], que_type_ids,
                        kp['knowledgeId'])

            name = '{}_{}_{}_{}_{}'.format(
                subj['code'], subj['schoolType'],
                subj['disciplineId'], kp['knowledgeId'], '1')

            url = 'http://www.jtyhjy.com/sts/question_findQuestionPage.action'
            item = make_item(url, data, subj)
            item.name = name
            loop.add_task('get_page', item, task_name=item.name)


if __name__ == '__main__':
    main()
