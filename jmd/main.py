# -*-coding:utf8-*-
import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#execute(["scrapy", "crawl", "jiemodui"])
#execute(["scrapy", "crawl", "jingmeiti"])
execute(["scrapy", "crawl", "yitiku"])
#execute(["scrapy", "crawl", "ytk"])