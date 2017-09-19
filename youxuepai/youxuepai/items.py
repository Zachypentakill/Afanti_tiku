# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YouxuepaiItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field()
    subject = scrapy.Field()
    html = scrapy.Field()
    md5 = scrapy.Field()
    key2 = scrapy.Field()
    request_info = scrapy.Field()
    record_time = scrapy.Field()
    flag = scrapy.Field()
    source_id = scrapy.Field()
    question_type = scrapy.Field()

    # name = scrapy.Field()
    # name = scrapy.Field()
    def get_insert_sql(self):
        insert_mysql = """
                        insert ignore into youxuepai_0802(source, subject, html, md5, key2, request_info, record_time, flag, source_id, question_type) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        ON DUPLICATE KEY UPDATE md5=VALUES(md5)
                    """
        #ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        params = (str(self["source"]), str(self["subject"]), self["html"].decode('utf-8'), str(self["md5"]),str(self["key2"]),
                  str(self["request_info"]), str(self["record_time"]), str(self["flag"]), str(self["source_id"]), str(self["question_type"]))

        return insert_mysql, params
