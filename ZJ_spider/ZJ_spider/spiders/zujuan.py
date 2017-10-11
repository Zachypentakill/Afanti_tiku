# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from urllib import parse
from ZJ_spider.ultil.command import get_md5,extract_num
from ZJ_spider.items import ZjSpiderItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from multiprocessing import Pool
import time
import random

class ZujuanSpider(scrapy.Spider):
    name = 'zujuan'
    allowed_domains = ['zujuan.com']
    start_urls = ['http://zujuan.com/']

    filter_url = set()
    cookies = {
        '_csrf': 'bcb49842a7322c41aefd7b4b15665d0f209655dc4ac37dade780093db817ebf1a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22nue40PwQNQgzgV0gHAcMfIbN2JESYiNp%22%3B%7D',
        '__guid': '202631831.1772692315455636200.1506497946733.2334',
        'device': '310bdaba05b30bb632f66fde9bf3e2b91ebc4d607c250c2e1a1d9e0dfb900f01a%3A2%3A%7Bi%3A0%3Bs%3A6%3A%22device%22%3Bi%3A1%3BN%3B%7D',
        '_sync_login_identity': '19f88d2474d8f94f8b8597154769f5002bccd70ffdae7ccd481dfc2e9bc8bdf2a%3A2%3A%7Bi%3A0%3Bs%3A20%3A%22_sync_login_identity%22%3Bi%3A1%3Bs%3A50%3A%22%5B1244215%2C%22jKvBjk912SInXNA_261BP9b5fEpSdlk4%22%2C86400%5D%22%3B%7D',
        'PHPSESSID': 'akkmsuthplh97g2nia7pqqe6e7',
        'chid': '753411127a26c0bf4f88c5bb0c64e771512616316bae9de43cb9a9038d6b13ffa%3A2%3A%7Bi%3A0%3Bs%3A4%3A%22chid%22%3Bi%3A1%3Bs%3A1%3A%223%22%3B%7D',
        'xd': 'e409e1df3e15356a9137ce7680720f7dcbdcd6c6ebeb77ff59f645d6ffb02d15a%3A2%3A%7Bi%3A0%3Bs%3A2%3A%22xd%22%3Bi%3A1%3Bs%3A1%3A%223%22%3B%7D',
        '_identity': '041a00f44eeb2c1ec5a2c34daff919a204689a997f07f5fed61cbb0263498e59a%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A50%3A%22%5B1244215%2C%22b8b1cca114a37c4ffc62f30179b4607a%22%2C86400%5D%22%3B%7D',
        'monitor_count': '58',
        'Hm_lvt_6de0a5b2c05e49d1c850edca0c13051f': '1506497947',
        'Hm_lpvt_6de0a5b2c05e49d1c850edca0c13051f': '1506499779'
    }

    User_Agents = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE"]

    grade_subject = {
        '3':['2','3','4','6','7','8','9','10','11'],
        '2':['2','3','4','6','7','8','9','10','11','5','20'],
        '1':['2','3','4','5','9']
    }


    def parse(self, response):
        for keys,values in self.grade_subject.items():
            for subject in values:
                first_zujuan_url = 'http://www.zujuan.com/paper/index?chid={0}&xd={1}&tree_type=knowledge'.format(subject,keys)
                yield scrapy.Request(url=first_zujuan_url, dont_filter=True, callback=self.parse_grade_subject,
                                     headers={"User-Agent": random.choice(self.User_Agents)})

    def  parse_grade_subject(self,response):
        request_info = {}
        self.filter_url = set()
        grade_subject = response.xpath('//div[@class="nav-items"]/a/span/text()').extract()
        all_biaozhu = response.xpath('/html/body/div[@class="search-type g-container"]/div[@class="type-items"]/div[@class="type-conbox"]/div/div')

        banben = all_biaozhu[0].xpath('a/text()').extract()[1:]
        banben_urls = all_biaozhu[0].xpath('a/@href').extract()[1:]
        banben_url = []
        for banben_nodes in banben_urls:
            banben_node = re.search('&versionid=(.+)',banben_nodes)
            banben_url.append(banben_node.group())
        banben_zip = zip(banben,banben_url)

        nianji = all_biaozhu[1].xpath('a/text()').extract()[1:]
        nianji_urls = all_biaozhu[1].xpath('a/@href').extract()[1:]
        nianji_url = []
        for nianji_nodes in nianji_urls:
            nianji_node = re.search('&gradeid=(.+)',nianji_nodes)
            nianji_url.append(nianji_node.group())
        nianji_zip = zip(nianji,nianji_url)

        diqu = all_biaozhu[3].xpath('a/text()').extract()[1:]
        diqu_urls = all_biaozhu[3].xpath('a/@href').extract()[1:]
        diqu_url = []
        for diqu_nodes in diqu_urls:
            diqu_node = re.search('&province_id=(.+)',diqu_nodes)
            diqu_url.append(diqu_node.group())
        diqu_zip = zip(diqu,diqu_url)

        request_info["jibu"] = grade_subject[0][:2]
        request_info["subject"] = grade_subject[0][2:]

        for b in banben_zip:
            for n in nianji_zip:
                for d in diqu_zip:
                    new_urls = response.url + b[1] + n[1] + d[1]
                    request_info["banben"] = b[0]
                    request_info["nianji"] = n[0]
                    request_info["diqu"] = d[0]
                    yield scrapy.Request(url=new_urls, dont_filter=True, callback=self.parse_zujuan_pattern,
                                         headers={"User-Agent": random.choice(self.User_Agents)},
                                         meta={"request_info": request_info})


    def parse_zujuan_pattern(self,response):
        request_info = response.meta.get("request_info", {})
        all_biaozhu = response.xpath(
            '/html/body/div[@class="search-type g-container"]/div[@class="type-items"]/div[@class="type-conbox"]/div/div')

        leixing = all_biaozhu[2].xpath('a/text()').extract()[1:]
        leixing_urls = all_biaozhu[2].xpath('a/@href').extract()[1:]
        leixing_url = []
        for leixing_nodes in leixing_urls:
            leixing_node = re.search('&papertype=(.+)', leixing_nodes)
            leixing_url.append(leixing_node.group())
        leixing_zip = zip(leixing, leixing_url)

        for l in leixing_zip:
            request_info["leixing"] = l[0]
            new_urls = response.url + l[1] + 'page=1&per-page=10'
            yield scrapy.Request(url=new_urls, dont_filter=True, callback=self.parse_zujuan_page,
                                 headers={"User-Agent": random.choice(self.User_Agents)},
                                 meta={"request_info": request_info})


    def parse_zujuan_page(self,response):
        #current_text = response.xpath('//div[@class="search-list g-container"]').extract()
        if '未搜索到相关数据!' not in response.text:
            request_info = response.meta.get("request_info", {})
            zujuan_url = response.xpath('//div[@class="search-list g-container"]/ul/li')
            request_info["SubjectId"] = int(re.findall('chid=(.+?)&',response.url)[0])
            for nodes in zujuan_url:
                new_node_urls = nodes.xpath('div/div[@class="test-txt"]/p/a/@href').extract()[0]
                new_node_url = 'http://www.zujuan.com' + new_node_urls
                if new_node_url not in self.filter_url:
                    self.filter_url.add(new_node_url)
                    yield scrapy.Request(url=new_node_url, dont_filter=True, callback=self.parse_zujuan,
                                        headers={"User-Agent": random.choice(self.User_Agents)},
                                        meta={"request_info": request_info})

                    number_url = int(re.findall('page=(.+?)&', response.url)[0]) + 1
                    head_url = re.search('(.+?)page=', response.url).group()
                    zujuan_page_url = head_url + str(number_url) + '&per-page=10'
                    yield scrapy.Request(url=zujuan_page_url, dont_filter=True, callback=self.parse_zujuan_page,
                                         headers={"User-Agent": random.choice(self.User_Agents)},
                                         meta={"request_info": request_info})



    def parse_zujuan(self,response):
        request_info = response.meta.get("request_info", '')
        request_info["spider_url"] = response.url
        subject = re.findall('',response.url)[0]
        title = response.xpath('//div[@class="preview-title"]/h1/text()').extract()[0]
        request_info["title"] = title
        info = response.xpath('//p[@class="exam-foot-left"]/a[1]/@href').extract()
        zujuan = ZjSpiderItem()
        zujuan["source"] = 18
        zujuan["subject"] = request_info["SubjectId"]
        zujuan["html"] = response.text
        zujuan["md5"] = get_md5(response.url.encode('utf-8'))
        zujuan["key"] = re.findall('paper/(.+?).shtml',response.url)[0]
        zujuan["request_info"] = [request_info]
        zujuan["info"] = info

        yield zujuan
