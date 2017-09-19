# -*-coding:utf8-*-

import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "3lian"])
#execute(["scrapy", "crawl", "diyifanwen"])
# with open('duilian.csv' , 'wt') as f:
#     f.writelines("网址，题目，上联，下联，横批，md5" + '\n')
# f.close()