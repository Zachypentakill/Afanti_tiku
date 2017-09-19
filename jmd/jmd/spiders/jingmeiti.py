# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from urllib import parse
from jmd.ultil.command import get_md5,extract_num
from jmd.items import JingMTItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from multiprocessing import Pool
import time


class JingmeitiSpider(scrapy.Spider):
    name = 'jingmeiti'
    allowed_domains = ['jingmeiti.com']
    start_urls = ['http://jingmeiti.com/page/2']
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    }
    all_url = []

    def parse(self, response):
        for i in range(1, 308):
            new_url = 'http://www.jingmeiti.com/page/' + str(i)
            yield scrapy.Request(url=new_url,headers=self.headers, dont_filter=True, callback=self.parse_second_url)
        # new_url = 'http://www.jingmeiti.com/page/2'
        # yield scrapy.Request(url=new_url, headers=self.headers, dont_filter=True, callback=self.parse_second_url)

    def parse_second_url(self, response):
        #/div[@class="posts-default-box"]/div[@class="posts-default-title"]/h2/a/@href.extract()
        url_list = response.xpath('//div[@class="ajax-load-box posts-con"]/div')
        for each_nodes in url_list:
            url_second_list = each_nodes.xpath('div/div[@class="posts-default-box"]/div[@class="posts-default-title"]/h2/a/@href').extract()
            title_second_list = each_nodes.xpath('div/div[@class="posts-default-box"]/div[@class="posts-default-title"]/h2/a/text()').extract()
            yield scrapy.Request(meta={"title": title_second_list[0]}, url=url_second_list[0], headers=self.headers, dont_filter= True, callback= self.parse_detail)


    def parse_detail(self,response):
        jingmeiti = JingMTItem()
        jingmeiti['spider_url'] = response.url
        jingmeiti['md5'] = get_md5(response.url.encode('utf-8'))
        jingmeiti['title'] = response.meta.get("title","")
        wenzhang = response.xpath('//div[@class="post-title"]/div[@class="post_icon"]/span[@class="postoriginal"]/text()').extract()
        if len(wenzhang) == 0:
            wenzhang = ['非原创文章']
        jingmeiti['wenzhang'] = wenzhang[0]
        pattern = response.xpath('//div[@class="post-title"]/div[@class="post_icon"]/span[@class="postcat"]/a/text()').extract()
        jingmeiti['pattern'] = pattern[0]
        writer = response.xpath('//div[@class="post-title"]/div[@class="post_icon"]/span[@class="postauthor"]/a/text()').extract()
        if len(writer) == 0:
            writer = response.xpath('//div[@class="post-title"]/div[@class="post_icon"]/span[@class="postauthor"]/text()').extract()
        jingmeiti['writer'] = writer[0]
        public_time = response.xpath('//div[@class="post-title"]/div[@class="post_icon"]/span[@class="postclock"]/text()').extract()
        jingmeiti['public_time'] = public_time[0]
        #//*[@id="page-content"]/div/div/div[1]/div[2]/div[2]
        htmls = response.xpath('//div[@class="post-content"]').extract()
        html = htmls[0]
        if isinstance(html, bytes):
            html = html.decode()
        jingmeiti['html'] = html
        yield jingmeiti
