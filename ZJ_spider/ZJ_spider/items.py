# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZjSpiderItem(scrapy.Item):
    source = scrapy.Field()
    subject = scrapy.Field()
    html = scrapy.Field()
    md5 = scrapy.Field()
    key = scrapy.Field()
    request_info= scrapy.Field()
    info = scrapy.Field()

    def get_insert_sql(self):
        insert_mysql = """
                            insert ignore into zujuan_shijuan_spider_html_archive_table_20170928(source, 
                            subject, `html`, `md5`, `key`, request_info, `info`)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
                        """
        # ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        params = (self["source"], self["subject"], self["html"], self["md5"],
                  self["key"], str(self["request_info"]), str(self["info"]))

        return insert_mysql, params

class ZjShitiSpiderItem(scrapy.Item):
    source = scrapy.Field()
    subject = scrapy.Field()
    html = scrapy.Field()
    md5 = scrapy.Field()
    key = scrapy.Field()
    request_info= scrapy.Field()
    info = scrapy.Field()

    def get_insert_sql(self):
        insert_mysql = """
                            insert ignore into zujuan_shiti_spider_html_archive_table_20170929(source, 
                            subject, `html`, `md5`, `key`, request_info, `info`)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
                        """
        # ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        params = (self["source"], self["subject"], self["html"], self["md5"],
                  self["key"], str(self["request_info"]), str(self["info"]))

        return insert_mysql, params