# -*- coding: utf-8 -*-

# Scrapy settings for youxuepai project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'youxuepai'

SPIDER_MODULES = ['youxuepai.spiders']
NEWSPIDER_MODULE = 'youxuepai.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'youxuepai (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.001
#DOWNLOAD_TIMEOUT = 6
#DONT_RETRY = True
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 32
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'youxuepai.middlewares.YouxuepaiSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html

REDIRECT_ENABLED = True

RETRY_ENABLED = True
RETRY_TIMES = 2

RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 400, 404, 403, 415, 405]
DOWNLOADER_MIDDLEWARES = {
   'youxuepai.middlewares.RandomProxyMiddleware': 100,
   'youxuepai.middlewares.RandomRetryMiddleware': 300,
   'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
   'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware':None,
   'scrapy.contrib.downloadermiddleware.downloadtimeout.DownloadTimeoutMiddleware':None,
   'youxuepai.middlewares.RandomDownloadTimeoutMiddleware': 10,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'youxuepai.pipelines.MysqlTwistedpipeline': 3,
   #'youxuepai.pipelines.Youxuepai_CSV_Pipeline': 4,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
#本地库函数
#MYSQL_HOST = 'localhost'
#MYSQL_USER = 'root'
#MYSQL_DBNAME = 'youxuepai'
#MYSQL_PASSWORD = '1234'
#云端数据库
MYSQL_HOST = '10.44.149.251'
MYSQL_USER = 'liyanfeng'
MYSQL_DBNAME = 'html_archive'
MYSQL_PASSWORD = 'AFtdbliyf7893'
