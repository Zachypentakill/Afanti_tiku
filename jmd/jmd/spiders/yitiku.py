# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from urllib import parse
from jmd.ultil.command import get_md5,extract_num
from jmd.items import YitikuItem, YitikuShitiItem, YitikuShijuanItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from multiprocessing import Pool
import time
import random

class YitikuSpider(scrapy.Spider):
    name = 'yitiku'
    allowed_domains = ['yitiku.cn']
    start_urls = ['http://www.yitiku.cn/']
    parsed_all_url = []
    parsed_all_shiti_url = []
    timeout_fail_url = []
    threshold = 10
    first_number = 1229916
    end_number = 1400000
    init_i = 0
    end_number_final = 1397449
    shijuan_first_number = 1
    #31000
    shijuan_end_number = 3361
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

    all_count_number = end_number - first_number
    range_number = int(all_count_number / threshold)

    def parse(self, response):
        # if self.init_i <= self.range_number:
        #     a = self.init_i * self.threshold + self.first_number
        #     b = (self.init_i + 1) * self.threshold + self.first_number
        #     for i in range(a, b):
        #         new_urls = 'http://www.yitiku.cn/shiti/' + str(i) + '.html'
        #         time.sleep(0.1)
        #         yield scrapy.Request(url=new_urls, dont_filter=True, meta={"source_id": str(i)}, cookies=self.cookies,
        #                              headers={"User-Agent": random.choice(self.User_Agents)},
        #                              callback=self.parse_detail_shiti)
        #     self.init_i += 1
        #     yield scrapy.Field(url=response.url, dont_filter=True, callback= self.parse)


        # 注释（三）： 多线程 试题解析1397449
        # for i in range(1, 5000):
        #     new_urls = 'http://www.yitiku.cn/shiti/' + str(i) + '.html'
        #     time.sleep(0.3)
        #     yield scrapy.Request(url=new_urls, dont_filter=True,meta={"source_id": str(i)}, cookies=self.cookies,
        #                         headers={"User-Agent": random.choice(self.User_Agents)},callback=self.parse_detail_shiti)

        #注释（四）： 单线程循环 试题(3)
        if self.first_number <= self.end_number:
            self.first_number += 1
            new_urls = 'http://www.yitiku.cn/shiti/' + str(self.first_number) + '.html'
            time.sleep(0.01)
            yield scrapy.Request(url=new_urls, dont_filter=True, headers={"User-Agent": random.choice(self.User_Agents)},
                            cookies=self.cookies, callback=self.parse_detail_shiti, meta={"source_id": self.first_number})

        # 注释（一）： 试卷解析
        # for i in range(1,31000):
        #     new_url = 'http://www.yitiku.cn/shijuan/' + str(i) + '.html'
        #     time.sleep(1)
        #     yield scrapy.Request(url=new_url, dont_filter=True, meta={"source_id":i},callback=self.parse_detail,
        #                          headers={"User-Agent": random.choice(self.User_Agents)})

        # 注释（二）： 单线程试卷解析
        # if self.shijuan_first_number <= self.shijuan_end_number:
        #     self.shijuan_first_number += 1
        #     new_url = 'http://www.yitiku.cn/shijuan/' + str(self.shijuan_first_number) + '.html'
        #     yield scrapy.Request(url=new_url, dont_filter=True, headers={"User-Agent": random.choice(self.User_Agents)},
        #                          callback=self.parse_detail,meta={"source_id":self.shijuan_first_number})

    def parse_detail(self, response):
        if len(response.text) != 0:
            title = response.xpath('//div[@id="wrapper"]/div[@class="sjbt"]/h1/text()').extract()
            if len(title) != 0:
                yitiku = YitikuShijuanItem()
                title = title[0]
                yitiku['title'] = title
                subject = response.xpath('//div[@class="path"]/label[2]/text()').extract()
                if len(subject) != 0:
                    subject = subject[0][-2:]
                    for key, value in self.subject_item.items():
                        if subject in key:
                            subject = value
                    yitiku['subject'] = subject
                else:
                    yitiku['subject'] = 11
                heads_news = response.xpath('//div[@id="wrapper"]/div[@class="sjbt"]/div').extract()
                if len(heads_news) != 0:
                    heads_news = heads_news[0]
                    grade = re.findall('<span>适用年级：(.+?)</span>', heads_news)
                    yitiku['grade'] = grade[0]
                    pattern = re.findall('<span>试卷类型：(.+?)</span>', heads_news)
                    yitiku['pattern'] = pattern[0]
                    province = re.findall('<span>适用省份：(.+?)</span>', heads_news)
                    yitiku['province'] = province[0]
                    year = re.findall('<span>试卷年份：(.+?)</span>', heads_news)
                    yitiku['year'] = year[0]
                    ti_number = re.findall('<span>题数：(.+?)</span>', heads_news)
                    yitiku['ti_number'] = ti_number[0]
                    watch_number = re.findall('<span>浏览数：(.+?)</span>', heads_news)
                    yitiku['watch_number'] = watch_number[0]
                shijuan = response.xpath('//div[@id="wrapper"]/div[@class="box1000"]').extract()
                #//*[@id="js_qs"]/li[2]/a //*[@id="js_qs"]/li[2]/a
                question_urls = response.xpath('//ul[@id="js_qs"]/li[@class="icon5"]/a/@href').extract()
                question_url = []
                for i in question_urls:
                    new_urls = 'http://www.yitiku.cn/shijuan' + i
                    question_url.append(new_urls)
                yitiku['question_urls'] = question_url
                yitiku['html'] = shijuan[0]
                yitiku['spider_url'] = response.url
                yitiku['md5'] = get_md5(response.url.encode('utf-8'))
                yitiku['spider_source'] = 59
                yitiku['source_id'] = response.meta.get('source_id', "")
                yield yitiku
                # if response.url not in self.parsed_all_url:
            #     self.parsed_all_url.append(response.url)
        yield scrapy.Request(url=response.url, dont_filter=True, headers={"User-Agent": random.choice(self.User_Agents)}, callback=self.parse)

    def parse_detail_shiti(self, response):
        question_id = response.meta.get("source_id", int)
        if len(response.text) != 0:
            subject = response.xpath('//div[@class="full full03"]/div/div[@class="path"]/a[2]/text()').extract()
            if len(subject) != 0:
                yitiku = YitikuItem()
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
                yitiku['source_id'] = question_id
                yield yitiku
        # if question_id <= self.end_number:
        #     self.first_number = question_id + 1
        #     new_url = 'http://www.yitiku.cn/shiti/' + str(self.first_number) + '.html'
        #     time.sleep(0.02)
        #     yield scrapy.Request(url=new_url, dont_filter=True, headers={"User-Agent": random.choice(self.User_Agents)},
        #                     cookies=self.cookies, callback=self.parse_detail_shiti, meta={"source_id": self.first_number})
        yield scrapy.Request(url=response.url, dont_filter=True, callback=self.parse,
                             headers={"User-Agent": random.choice(self.User_Agents)})

