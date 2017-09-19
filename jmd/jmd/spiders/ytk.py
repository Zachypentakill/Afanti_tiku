# -*- coding: utf-8 -*-

import jmd
import scrapy
import re
import os
import json
import datetime
from urllib import parse
from jmd.ultil.command import get_md5,extract_num
from jmd.items import YitikuPageUrlItem, YitikuShitiItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from multiprocessing import Pool
import time
import random
import pymysql
import pymysql.cursors

class YitikuSpider(scrapy.Spider):
    name = 'ytk'
    allowed_domains = ['yitiku.cn']
    start_urls = ['http://www.yitiku.cn/']
    parsed_all_url = []
    parsed_all_shiti_url = []
    timeout_fail_url = []
    threshold = 2
    cookies = {
        'pgv_pvi': '2848735232',
        'Hm_lvt_ba430f404e1018c19017fd7d6857af83': '1504005406,1504078014,1504093651,1504229613',
        '_qddaz': 'QD.jwmj5t.o5uttt.j6wz682k',
        'tencentSig': '4939668480',
        'PHPSESSID': 'd94t409l8msqjqcvv3gos8rib3',
        'pgv_si': 's1328115712',
        'Hm_lpvt_ba430f404e1018c19017fd7d6857af83': '1504229930',
        'IESESSION': 'alive',
        '_qddab': '3-htwi5y.j717h2ml',
        'ytkuser': '%7B%22id%22%3A%22644459%22%2C%22deadline%22%3A%220%22%2C%22feature%22%3A%229acfdb11a8cb9113945fd4330d294bdf%22%7D',
        'jiami_userid': 'NjQ0NDU5fGU3ZWE0YWFmZDEwMmMxZGI1YTM0NDEyNmMyZTMyN2E5',
        'account': 'yofenice%40nutpa.net',
        'password': 'cWF6d3N4'
    }
    cookies2 = {
        '__guid': '121430670.1910768087959285000.1503973721719.0112',
        'pgv_pvi': '1866981376',
        'tencentSig': '631201792',
        'PHPSESSID': 'mouet3fjaf89rcu7qcdcvpbct2',
        'pgv_si': 's652461056',
        'IESESSION': 'alive',
        '_qddamta_800024201': '3-0',
        'jiami_userid': 'NjQ0NDU5fGU3ZWE0YWFmZDEwMmMxZGI1YTM0NDEyNmMyZTMyN2E5',
        'account': 'yofenice%40nutpa.net',
        'password': 'cWF6d3N4',
        'monitor_count': '226',
        'Hm_lvt_ba430f404e1018c19017fd7d6857af83': '1503973727,1504059461,1504061747',
        'Hm_lpvt_ba430f404e1018c19017fd7d6857af83': '1504085056',
        '_qddaz': 'QD.v0t7iz.5q8t6j.j6wz4jaj',
        '_qdda': '3-1.41ihuk',
        '_qddab': '3-csmv5g.j6yoxvxz',
        'ytkuser': '%7B%22id%22%3A%22644459%22%2C%22deadline%22%3A%220%22%2C%22feature%22%3A%229acfdb11a8cb9113945fd4330d294bdf%22%7D'
    }
    User_Agents = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE"]
    subject_item = {
        '语文': '1',
        '数学': '2',
        '英语': '3',
        '科学': '4',
        '物理': '5',
        '化学': '6',
        '地理': '7',
        '历史': '8',
        '生物': '9',
        '政治': '10'
    }
    parsed_subject_list = ["gzyuwen", "gzshuxue", "gzyingyu", "gzhuaxue", "gzwuli",
                            "gzshengwu", "gzlishi", "gzdili", "gzzhengzhi"]
    parsing_subject_list = ["gzhuaxue", "gzwuli", "gzshengwu", "gzlishi", "gzdili", "gzzhengzhi"]
    unparsed_subjuct_list = [ "tbyw", "tbsx", "tbyy", "tbhx", "tbwl", "tbsw", "tbls", "tbdl", "tbzz" ]
    _DIR = os.path.dirname(jmd.__file__)
    CONFIG_FILE = os.path.join(_DIR, 'config')

    def parse(self, response):
        #注释（一）： 对在yitiku_shiti_page_url_0905库中的page——url进行解析
        config = json.load(open(self.CONFIG_FILE))
        conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='html_archive',
                               port=3306, charset="utf8", use_unicode=True, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        sql = 'select * from yitiku_shiti_page_url_0905 limit 6000,1000'
        #sql = 'select * from yitiku_shiti_page_url_0905 limit 3000,7000'
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        jsonData = []
        #解析带book和version页面的
        for row in data:
            new_url = row['spider_url']
            time.sleep(0.1)
            yield scrapy.Request(url=new_url, dont_filter=True, callback=self.parse_url,
                                 headers={"User-Agent": random.choice(self.User_Agents)})

        #注释（二）： 添加book和version判定(2)
        # for node_subject in self.unparsed_subjuct_list:
        #     new_urls = 'http://www.yitiku.cn/tiku/' + node_subject
        #     yield scrapy.Request(url=new_urls, dont_filter=True, callback=self.parse_second_url,
        #                          headers={"User-Agent": random.choice(self.User_Agents)})

    def parse_second_url(self,response):
        book_url = response.xpath('//div[@class="tongbu"]/dl[@class="bbxz"]/dd/a/@href').extract()
        book = response.xpath('//div[@class="tongbu"]/dl[@class="bbxz"]/dd/a/text()').extract()
        a = len(book_url)
        for i in range(a):
            first_url = 'http://www.yitiku.cn' + book_url[i]
            time.sleep(0.02)
            yield scrapy.Request(url=first_url, dont_filter=True, callback=self.parse_third_url,
                                 headers={"User-Agent": random.choice(self.User_Agents)} )

    def parse_third_url(self, response):
        version_url = response.xpath('//div[@class="tongbu"]/dl[@class="bbxz mb5"]/dd/a/@href').extract()
        version = response.xpath('//div[@class="tongbu"]/dl[@class="bbxz mb5"]/dd/a/text()').extract()
        b = len(version_url)
        for j in range(b):
            version_url_node = re.findall('/jid(.+)', version_url[j])
            version_url_node = version_url_node[0]
            second_url = response.url + '/jid' + version_url_node
            time.sleep(0.5)
            #测试网页http://www.yitiku.cn/tiku/gzyuwen/banben/1560/jid/1578
            #second_url = 'http://www.yitiku.cn/tiku/gzdili/tb_tixing/1/jid/12537?page=1'
            yield scrapy.Request(url=second_url, callback=self.parse_fourth_url,dont_filter=True,
                                    headers={"User-Agent": random.choice(self.User_Agents)})

    def parse_fourth_url(self, response):
        next_url_number = response.xpath('//div[@class="page"]/a[@style="display:none"]/text()').extract()
        yitiku = YitikuPageUrlItem()
        url_list = []
        md5_list = []
        if len(next_url_number) == 0:
            for i in range(1,5):
                new_urls = response.url + '?page=' + str(i)
                md5 = get_md5(new_urls.encode('utf-8'))
                md5_list.append(md5)
                url_list.append(new_urls)
        else:
            for i in range(1, int(next_url_number[0]) + 1):
                new_urls = response.url + '?page=' + str(i)
                md5 = get_md5(new_urls.encode('utf-8'))
                md5_list.append(md5)
                url_list.append(new_urls)
        yitiku['spider_url'] = url_list
        yitiku['md5'] = md5_list
        yield yitiku

    def parse_url(self, response):
        book = response.xpath('//dl[@class="bbxz"]/dd/a[@class="on"]/text()').extract()
        version = response.xpath('//dl[@class="bbxz mb5"]/dd/a[@class="on"]/text()').extract()
        parse_urls = response.xpath('//ul[@id="js_qs"]/li[@class="icon5"]/a/@href').extract()
        if len(parse_urls) != 0 and len(book) != 0 and len(version) != 0:
            for parse_url in parse_urls:
                new_urls = 'http://www.yitiku.cn' + parse_url
                time.sleep(0.3)
                yield scrapy.Request(url=new_urls, callback=self.parse_detail, headers={"User-Agent": random.choice(self.User_Agents)},
                             dont_filter=True, cookies= self.cookies, meta={"book": book[0], "version": version[0]})

    def parse_detail(self, response):
        if len(response.text) != 0:
            subject = response.xpath('//div[@class="full full03"]/div/div[@class="path"]/a[2]/text()').extract()
            if len(subject) != 0:
                yitiku = YitikuShitiItem()
                answer1 = response.xpath('//li[@class="noborder"]/div').extract()
                answer2 = response.xpath('//li[@class="noborder"]/b/text()').extract()
                answer = answer1 or answer2
                if len(answer) == 0:
                    yitiku['answer'] = ''
                else:
                    yitiku['answer'] = answer[0]
                analy = response.xpath('//div[@class="quesTxt quesTxt2"]/ul[2]/li[1]/div').extract()
                if len(analy) != 0:
                    yitiku['analy'] = analy[0]
                else:
                    yitiku['analy'] = ''
                yitiku['grade'] = subject[0][:2]
                subject = subject[0][-2:]
                yitiku['subject'] = subject
                for key, value in self.subject_item.items():
                    if subject in key:
                        subject = value
                yitiku['subject'] = subject
                yitiku['book'] = response.meta.get("book", "")
                yitiku['version'] = response.meta.get("version", "")
                pattern = response.xpath('//div[@class="detailsTitle"]/h3/text()').extract()
                if len(pattern) != 0:
                    yitiku['pattern'] = pattern[0]
                else:
                    yitiku['pattern'] = ''
                source_shijuan = response.xpath('//div[@class="quesdiv"]/h1').extract()
                if len(source_shijuan) != 0:
                    yitiku['source_shijuan'] = source_shijuan[0]
                else:
                    yitiku['source_shijuan'] = ''
                difficulty = response.xpath('//div[@class="handle"]/div/u[1]/i/text()').extract()
                if len(difficulty) != 0:
                    yitiku['difficulty'] = difficulty[0]
                else:
                    yitiku['difficulty'] = ''
                kaodian = response.xpath('//div[@class="quesTxt quesTxt2"]/ul/li/div/a/text()').extract()
                if len(kaodian) != 0:
                    yitiku['kaodian'] = kaodian[0]
                else:
                    yitiku['kaodian'] = ''
                shijuan = response.xpath('//div[@class="quesdiv"]').extract()
                if len(shijuan) != 0:
                    yitiku['topic'] = shijuan[0]
                yitiku['spider_url'] = response.url
                yitiku['md5'] = get_md5(response.url.encode('utf-8'))
                yitiku['spider_source'] = 59
                yitiku['html'] = response.text
                yield yitiku
