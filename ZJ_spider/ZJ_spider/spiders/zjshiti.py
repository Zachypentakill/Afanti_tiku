# -*- coding: utf-8 -*-
import scrapy
import traceback
import pymysql
import pymysql.cursors
from multiprocessing import Pool, Process
from w3lib.html import remove_tags
from twisted.enterprise import adbapi
import os
from afanti_tiku_lib.html.image_magic import ImageMagic
from afanti_tiku_lib.html.magic import HtmlMagic
import datetime
import logging
import re
import json
import datetime
from urllib import parse
from ZJ_spider.ultil.command import get_md5,extract_num
from ZJ_spider.items import ZjShitiSpiderItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from multiprocessing import Pool
import time
import random
import ZJ_spider


class ZjshitiSpider(scrapy.Spider):
    name = 'zjshiti'
    allowed_domains = ['zujuan.com']
    start_urls = ['http://zujuan.com/']

    _DIR = os.path.dirname(ZJ_spider.__file__)
    CONFIG_FILE = os.path.join(_DIR, 'config')

    cookies = {
        'csrf': 'bcb49842a7322c41aefd7b4b15665d0f209655dc4ac37dade780093db817ebf1a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22nue40PwQNQgzgV0gHAcMfIbN2JESYiNp%22%3B%7D',
        '__guid': '202631831.1772692315455636200.1506497946733.2334',
        'device': '310bdaba05b30bb632f66fde9bf3e2b91ebc4d607c250c2e1a1d9e0dfb900f01a%3A2%3A%7Bi%3A0%3Bs%3A6%3A%22device%22%3Bi%3A1%3BN%3B%7D',
        '_sync_login_identity': 'd01df48e4904bec45a74c331c32777123b5a9082396b5c3b673831679e9c7c8ba%3A2%3A%7Bi%3A0%3Bs%3A20%3A%22_sync_login_identity%22%3Bi%3A1%3Bs%3A50%3A%22%5B1244215%2C%224rVfutbeD0nQv-B2Aq1AHoILfsBExzwb%22%2C86400%5D%22%3B%7D',
        'PHPSESSID': 'e1iqif1dfvk70sbruntng11s93',
        '_identity': '041a00f44eeb2c1ec5a2c34daff919a204689a997f07f5fed61cbb0263498e59a%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A50%3A%22%5B1244215%2C%22b8b1cca114a37c4ffc62f30179b4607a%22%2C86400%5D%22%3B%7D',
        'chid': 'cafaf1cbed4501b7d0e92ec2938f9931b96d5755c316dee169a043deb23cf4fea%3A2%3A%7Bi%3A0%3Bs%3A4%3A%22chid%22%3Bi%3A1%3Bs%3A2%3A%2211%22%3B%7D',
        'xd': '302c76d9e27c6fb0e1f815bdf637ae7f9ec27997dd7c18c9fcf7c68da09ff5c8a%3A2%3A%7Bi%3A0%3Bs%3A2%3A%22xd%22%3Bi%3A1%3Bs%3A1%3A%222%22%3B%7D',
        'monitor_count': '164',
        'Hm_lvt_6de0a5b2c05e49d1c850edca0c13051f': '1506497947',
        'Hm_lpvt_6de0a5b2c05e49d1c850edca0c13051f': '1506597448'
    }

    User_Agents = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE"]

    grade_subject = {
        '3': ['2', '3', '4', '6', '7', '8', '9', '10', '11'],
        '2': ['2', '3', '4', '6', '7', '8', '9', '10', '11', '5', '20'],
        '1': ['2', '3', '4', '5', '9']
    }

    def parse(self, response):
        config = json.load(open(self.CONFIG_FILE))
        first_id = 0
        conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='html_archive2',
                               port=3306, charset="utf8", use_unicode=True, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        first_id = 0
        table = 'zujuan_shijuan_spider_html_archive_table_20170928'

        while True:
            logging.warn('parse the first_id is : {}'.format(first_id))
            sql = 'select * from {0} where html_id > {1} limit 10'.format(table, first_id)
            cur.execute(sql)
            data = cur.fetchall()

            if not data:
                break

            for row in data:
                shiti_urls = eval(row["info"])
                request_info = eval(row["request_info"])[0]
                request_info["source"] = 18
                for url in shiti_urls:
                    new_url = 'http://www.zujuan.com' + url
                    # cookies=self.cookies,
                    yield scrapy.Request(url=new_url, dont_filter=True, callback=self.parse_detail,
                                         headers={"User-Agent": random.choice(self.User_Agents)},
                                         meta={"request_info": request_info})

            first_id = int(data[-1]['html_id'])

    def parse_detail(self, response):
        request_info = response.meta.get("request_info", '')
        html = response.text
        #a = re.findall('("question_text":.+?)"category"', html, re.S)[0]
        info_str = re.findall('MockDataTestPaper = (.+?\]) ;',html)[0]


        request_info["spider_url"] = response.url
        zujuan = ZjShitiSpiderItem()
        zujuan["source"] = 18
        zujuan["subject"] = request_info["SubjectId"]
        zujuan["html"] = response.text
        zujuan["md5"] = get_md5(response.url.encode('utf-8'))
        zujuan["key"] = re.findall('question/(.+?).shtml', response.url)[0]
        zujuan["request_info"] = request_info
        zujuan["info"] = info_str

        yield zujuan