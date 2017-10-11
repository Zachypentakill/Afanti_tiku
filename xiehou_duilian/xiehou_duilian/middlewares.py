# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
from scrapy import signals
# Start your middleware class
import random
 # 导入有关IP池有关的模块
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
# 导入有关用户代理有关的模块
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from adsl_server.proxy import Proxy
import time
import re
import scrapy
from adsl_server.proxy import Proxy
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.python import global_object_name
from scrapy.dupefilter import RFPDupeFilter
from w3lib.url import canonicalize_url
from pybloom import ScalableBloomFilter


logger = logging.getLogger(__name__)


class XiehouDuilianSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class URLsha1Filter(RFPDupeFilter):
    # def __init__(self, path=None):
    #     self.urls_seen = set()
    #     RFPDupeFilter.__init__(self, path)

    # def request_seen(self, request):
    #     fp = hashlib.sha1()
    #     fp.update(canonicalize_url(request.url))
    #     url_sha1 = fp.hexdigest()
    #     if url_sha1 in self.urls_seen:
    #         return True
    #     else:
    #         self.urls_seen.add(url_sha1)

    def __init__(self, path=None):
        self.urls_sbf = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        RFPDupeFilter.__init__(self, path)

    def request_seen(self, request):
        fp = hashlib.sha1()
        fp.update(canonicalize_url(request.url))
        url_sha1 = fp.hexdigest()
        if url_sha1 in self.urls_sbf:
            return True
        else:
            self.urls_seen.add(url_sha1)


import redis
pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=pool)
r.set('name','liyanfeng')
r.mset(age=20,country='china')
print(r.mget(['age', 'country', 'name']))
print(r.getrange('name', 3, 6))
print(r.get('name').decode())

r.hmset('student', {'name':'afanti', 'age':'20'})
print(r.hmget('student', ['name','age']))

r.lpush('digit', 11,22,33)
r.linsert('digit', 'before', '22', 'aa')