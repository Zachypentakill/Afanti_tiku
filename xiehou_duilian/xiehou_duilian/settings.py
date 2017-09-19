# -*- coding: utf-8 -*-

# Scrapy settings for xiehou_duilian project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'xiehou_duilian'

SPIDER_MODULES = ['xiehou_duilian.spiders']
NEWSPIDER_MODULE = 'xiehou_duilian.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'xiehou_duilian (+http://www.yourdomain.com)'
#DOWNLOAD_DELAY = 0.25

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 32
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
#SPIDER_MIDDLEWARES = {
#    'xiehou_duilian.middlewares.XiehouDuilianSpiderMiddleware': 543,
#}
# REDIRECT_ENABLED = False

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# RETRY_ENABLED = True
# RETRY_TIMES = 4
#
# RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 400]
# DOWNLOADER_MIDDLEWARES = {
#    #'youxuepai.middlewares.RandomProxyMiddleware': 100,
#    'youxuepai.middlewares.RandomRetryMiddleware': 300,
#    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
#    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware':None,
#    'scrapy.contrib.downloadermiddleware.downloadtimeout.DownloadTimeoutMiddleware':None,
#    'youxuepai.middlewares.RandomDownloadTimeoutMiddleware': 400,
# }

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#
ITEM_PIPELINES = {
   #'xiehou_duilian.pipelines.CsvDataPipeline': 350,
   #'xiehou_duilian.pipelines.MysqlTwistedpipeline': 300,
   'xiehou_duilian.pipelines.Duilian_shengyu_pipeline': 400,
   #'xiehou_duilian.pipelines.Mysqlpipeline': 200,
}
#Duilian_shengyu_pipeline
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

MYSQL_HOST = '10.170.251.183'
MYSQL_USER = 'root'
MYSQL_DBNAME = 'xiehouyu'
MYSQL_PASSWORD = '123'
