# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from urllib import parse
from jmd.ultil.command import get_md5,extract_num
from jmd.items import JmdItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from multiprocessing import Pool
import time

class JiemoduiSpider(scrapy.Spider):
    name = 'jiemodui'
    allowed_domains = ['jiemodui.com']
    start_urls = ['http://www.jiemodui.com']
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    }
    all_url = []


    def parse(self, response):
        #print(response.request.headers)
        for i in range(43,85000):
            new_url = 'http://www.jiemodui.com/N/' + str(i) + '.html'
            yield scrapy.Request(url=new_url, dont_filter=True, errback=self.errback_httpbin, headers=self.headers, callback=self.parse_detail)
        # new_url = 'https://www.jiemodui.com/N/83691.html'
        # yield scrapy.Request(url=new_url, dont_filter=True, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response):
        if response.status == 200:
            try:
                title = response.xpath('//div[@id="div_MainCotent"]/section[@class="detailsMain center"]/div[@class="CSDMain"]/div[@class="newContent"]/h1/text()').extract()
            except:
                title = ''

            if len(title) != 0:
                jiemodui = JmdItem()
                jiemodui['title'] = title[0]
                jiemodui['spider_url'] = response.url
                jiemodui['md5'] = get_md5(response.url.encode('utf-8'))
                try:
                    public_time = response.xpath('//div[@id="div_MainCotent"]/section[@class="detailsMain center"]/div[@class="CSDMain"]/div[@class="newContent"]/p/span/time/text()').extract()
                    if len(public_time) != 0:
                        jiemodui['public_time'] = public_time[0]
                    else:
                        jiemodui['public_time'] = ''
                except:
                    pass

                try:
                    writer = response.xpath('//div[@id="div_MainCotent"]/section[@class="detailsMain center"]/div[@class="CSDMain"]/div[@class="newContent"]/p/a/text()').extract()
                    if len(writer) != 0:
                        jiemodui['writer'] = writer[0]
                    else:
                        jiemodui['writer'] = ''
                except:
                    pass

                try:
                    comment = response.xpath('//ul[@class="minuteDiscuss clearfix"]/li/dl/dd/p[@class="xiangxi"]/text()').extract()
                    if len(comment) != 0:
                        comment = comment[0]
                        if isinstance(eval(comment), bytes):
                            comment = eval(comment).decode()
                        jiemodui['comment'] = comment
                    else:
                        jiemodui['comment'] = ''
                except:
                    pass

                try:
                    html = response.xpath('//div[@id="div_MainCotent"]/section[@class="detailsMain center"]/div[@class="CSDMain"]/article').extract()
                    jiemodui['html'] = html[0]
                except:
                    pass
                yield jiemodui


    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on {0},HTTPcode is {1}'.format(response.url, response.status))
            # new_number2 = re.findall(".+question:(.+?)%22", response.url)
            # self.init_number = int(new_number2[0]) + 1
            # new_url_json = self.json_url_01 + str(self.init_number) + self.json_url_03
            # yield scrapy.Request(url=new_url_json, dont_filter=True, headers=self.headers, errback= self.errback_httpbin, callback=self.parse)
            pass

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)


