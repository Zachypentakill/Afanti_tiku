# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
# Importing base64 library because we'll need it ONLY in case if the proxy we are going to use requires authentication
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

logger = logging.getLogger(__name__)

class YouxuepaiSpiderMiddleware(object):
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

class RandomDownloadTimeoutMiddleware(object):
    def __init__(self, timeout=1.5):
        self._timeout = timeout

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings.getfloat('DOWNLOAD_TIMEOUT'))
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self._timeout = getattr(spider, 'download_timeout', self._timeout)

    def process_request(self, request, spider):
        if self._timeout:
            request.meta.setdefault('download_timeout', self._timeout)

class RandomProxyMiddleware(object):
    #动态设置ip代理
    def process_request(self, request, spider):
        _proxy = Proxy()
        proxy = _proxy.get()
        proxy2 = _proxy.get()
        try:
            request.meta["proxy"] = "http://" + proxy2
        except Exception as e:
            print(e)

    def process_response(self, request, response, spider):
        # if response.status != 200:
        #     _proxy = Proxy()
        #     proxy = _proxy.get()
        #     # proxy = "http://121.31.101.107:8123"
        #     # 对当前reque加上代理
        #     request.meta['proxy'] = proxy
        #     return request
        return response

    def process_exception(self, request, exception, spider):
        #if 'proxy' not in request.meta:
        #    request.meta["proxy"] = "http://123.169.34.241:9990"
        # if exception is not None:
        #     request.meta["proxy"] = "http://123.169.34.241:9990"

        return request

class RandomRetryMiddleware(object):

    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def __init__(self, settings):
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        self.json_url_01 = 'http://www.anoah.com/api_cache/?q=json/Qti/get&info={%22param%22:{%22qid%22:%22question:'
        self.json_url_03 = '%22,%22dataType%22:1},%22pulishId%22:%22%22}'
        self.User_Agents = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
                            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
                            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE"]
        self.headers = {
            "GET ": "/1/ HTTP/1.1",
            "Host": "www.anoah.com",
            'User-Agent': random.choice(self.User_Agents),
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status >= 400 or response.status < 200:
        #if response.status in self.retry_http_codes:
            new_number2 = re.findall(".+question:(.+?)%22", response.url)
            try:
                self.init_number = int(new_number2[0]) + 1
                new_url_json = self.json_url_01 + str(self.init_number) + self.json_url_03
                request._set_url(new_url_json)
                return request
            except Exception as e:
                print("there is the middleware of the RandomRetryMiddleware! " * 2)
                print(e)
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)
        # if  'JSONDecodeError'in exception:
        #     new_number2 = re.findall(".+question:(.+?)%22", response.url)
        #     self.init_number = int(new_number2[0]) + 1
        #     new_url_json = self.json_url_01 + str(self.init_number) + self.json_url_03
        #     request._set_url(new_url_json)
        #     return request
        # if request.poiority == -3:
        #     print("进入Retry 的process_exception判断")
        #     return self._set_proxy(request, exception, spider)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            _proxy = Proxy()
            number = random.randint(4, 100)
            proxy_id = _proxy.get_ip(server_id=number)
            proxy_id = proxy_id.decode()
            proxy = "http://" + proxy_id + ":9990"
            request.meta["proxy"]= proxy
            # proxy = _proxy.get()
            # proxy2 = _proxy.get()
            # request.meta["proxy"] = "http://" + proxy2
            request.dont_filter = True
            request.priority = request.priority + self.priority_adjust
            #return self.process_request(request, spider)
            return request
      
