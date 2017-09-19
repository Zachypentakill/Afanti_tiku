# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XiehouDuilianItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class DuilianItem(scrapy.Item):
    html_url = scrapy.Field()
    title = scrapy.Field()
    shanglian = scrapy.Field()
    xialian = scrapy.Field()
    hengpi = scrapy.Field()
    md5 = scrapy.Field()
    html = scrapy.Field()
    # def get_insert_sql(self):
    #     insert_mysql = """
    #           insert into duilian(html_url, title, shanglian, xialian, hengpi, md5)
    #           VALUES (%s, %s, %s, %s, %s, %s)
    #         """
    #     # ON DUPLICATE KEY UPDATE title=VALUES(title),html_url=VALUES(html_url),html=VALUES(html)
    #     params = (str(self["html_url"]), str(self["title"]), str(self["shanglian"]), str(self["xialian"]), str(self["hengpi"]), str(self["md5"]))
    #
    #     return insert_mysql, params

class XiehouItem(scrapy.Item):
    html_id = scrapy.Field()
    html_url = scrapy.Field()
    first_title = scrapy.Field()
    second_title = scrapy.Field()
    option = scrapy.Field()
    answer = scrapy.Field()
    md5 = scrapy.Field()


    # def get_insert_sql(self):
    #     insert_mysql = """
    #         insert into xiehouyu(html_url, first_title, second_title, `option`, answer, md5)
    #         VALUES (%s, %s, %s, %s, %s, %s)
    #     """
    #     #ON DUPLICATE KEY UPDATE md5=VALUES(md5)
    #     for i in range(len(self["option"])):
    #         params = (str(self["html_url"]), str(self["first_title"]), str(self["second_title"]), str(self["option"][i]),
    #                   str(self["answer"][i]), str(self["md5"][i]))
    #         return insert_mysql, params
        #params = (str(self["html_url"]), str(self["first_title"]), str(self["second_title"]), str(self["option"][0]),str(self["answer"][0]), str(self["md5"][0]))
        # for i in range(len(self["option"])):
        #     print(self["option"][i])



