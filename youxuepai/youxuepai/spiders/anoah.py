# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from urllib import parse
from youxuepai.ultil.command import get_md5,extract_num
from youxuepai.items import YouxuepaiItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import time
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher


class AnoahSpider(scrapy.Spider):
    #是否应该先建立代理池再去尝试去爬取网页，如果是需要代理池的话，第一步就需要配置代理池
    name = 'anoah'
    allowed_domains = ['anoah.com']
    start_urls = ['http://www.anoah.com/api_cache/?q=json/Qti/get&info={%22param%22:{%22qid%22:%22question:0%22,%22dataType%22:1},%22pulishId%22:%22%22}']
    headers = {
        "GET ": "/1/ HTTP/1.1",
        "Host": "www.anoah.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    }
    json_url_01 = 'http://www.anoah.com/api_cache/?q=json/Qti/get&info={%22param%22:{%22qid%22:%22question:'
    json_url_03 = '%22,%22dataType%22:1},%22pulishId%22:%22%22}'
    init_number = 849000
    final_number = 3000000
    count = 0

    # def __init__(self):
    #     super(AnoahSpider, self).__init__()
    #     dispatcher.connect(self.spider_close, signals.spider_closed)
    #
    #
    # def spider_close(self, spider):
    #     print("spider closed!")


    def parse(self, response):
        if self.final_number > self.init_number:
            if self.count < 40000:
                self.init_number += 1
                url_id = self.json_url_01 + str(self.init_number) + self.json_url_03
                try:
                    yield scrapy.Request(url=url_id, dont_filter=True, headers=self.headers, callback=self.parse_detail)
                except Exception as e:
                    print(e)
                    yield scrapy.Request(url=url_id, dont_filter=True, headers=self.headers, callback=self.parse)
            else:
                print("the scrapy is end!")
        else:
            self.final_number += 300000
            try:
                yield scrapy.Request(url=response.url, dont_filter=True, headers= self.headers, callback= self.parse)
            except Exception as e:
                print(e)


    def parse_detail(self,response):
        try:
            anoah_json = json.loads(response.text)
            #new_number2 = re.findall(".+question:(.+?)%22", response.url)
            if len(anoah_json) == 0:
                yield scrapy.Request(url=response.url, callback= self.parse_json_url)
            else:
                youxuepai = YouxuepaiItem()
                youxuepai["source"] = 75
                try:
                    youxuepai["subject"] = anoah_json["subjectId"]
                except:
                    youxuepai["subject"] = 10
                youxuepai["html"] = response.body
                youxuepai["md5"] = get_md5(response.url.encode('utf-8'))
                youxuepai["key2"] = response.url
                youxuepai["request_info"] =  '{"method": "GET", "url": "http://baidu.com"}'
                youxuepai["record_time"] = datetime.datetime.now().date()
                youxuepai["flag"] = 7
                numbers = anoah_json["gid"].replace("-", ":")
                new_number = numbers.split(":")[1]
                youxuepai["source_id"] = new_number
                youxuepai["question_type"] = anoah_json["qtypeId"]

                yield youxuepai
                yield scrapy.Request(url=response.url, dont_filter=True, headers=self.headers, callback=self.parse_json_url)
        except:
           self.count += 1
           yield scrapy.Request(url=response.url, dont_filter=True, headers=self.headers, callback=self.parse) 


    def parse_json_url(self, response):
        try:
            anoah_html = json.loads(response.text)
            if len(anoah_html) == 0:
                self.count += 1
            else:
                self.count = 0
            yield scrapy.Request(url=response.url, dont_filter=True, headers=self.headers, callback=self.parse)
        except:
            pass

    # def errback_httpbin(self, failure):
    #     # log all failures
    #     self.logger.error(repr(failure))
    #
    #     # in case you want to do something special for some errors,
    #     # you may need the failure's type:
    #
    #     if failure.check(HttpError):
    #         # these exceptions come from HttpError spider middleware
    #         # you can get the non-200 response
    #         response = failure.value.response
    #         self.logger.error('HttpError on %s', response.url)
    #         new_number2 = re.findall(".+question:(.+?)%22", response.url)
    #         self.init_number = int(new_number2[0]) + 1
    #         new_url_json = self.json_url_01 + str(self.init_number) + self.json_url_03
    #         yield scrapy.Request(url=new_url_json, dont_filter=True, headers=self.headers, errback= self.errback_httpbin, callback=self.parse)
    #         pass
    #
    #     elif failure.check(DNSLookupError):
    #         # this is the original request
    #         request = failure.request
    #         self.logger.error('DNSLookupError on %s', request.url)
    #
    #     elif failure.check(TimeoutError, TCPTimedOutError):
    #         request = failure.request
    #         self.logger.error('TimeoutError on %s', request.url)

