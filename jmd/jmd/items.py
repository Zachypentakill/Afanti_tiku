# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from models.es_types import Article
from elasticsearch_dsl.connections import connections

es = connections.create_connection(Article._doc_type.using)

def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数组
    used_word = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
        #调用es的analysis
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            analyzed_words = set([r['token'] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyzed_words - used_word
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests

class JmdItem(scrapy.Item):
    # define the fields for your item here like:
    public_time = scrapy.Field()
    title = scrapy.Field()
    html = scrapy.Field()
    md5 = scrapy.Field()
    spider_url = scrapy.Field()
    comment = scrapy.Field()
    writer = scrapy.Field()

    def get_insert_sql(self):
        insert_mysql = """
                        insert ignore into jiemodui_0824(title, public_time, 
                        `html`, `md5`, spider_url, writer, `comment`) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s) 
                        ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
                    """
        #ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        params = (str(self["title"]), str(self["public_time"]), self["html"], str(self["md5"]),
                  str(self["spider_url"]),str(self["writer"]), self["comment"])

        return insert_mysql, params

class JingMTItem(scrapy.Item):
    # define the fields for your item here like:
    public_time = scrapy.Field()
    title = scrapy.Field()
    html = scrapy.Field()
    md5 = scrapy.Field()
    spider_url = scrapy.Field()
    wenzhang = scrapy.Field()
    pattern = scrapy.Field()
    writer = scrapy.Field()

    def get_insert_sql(self):
        insert_mysql = """
                        insert ignore into jingmeiti_0825(title, public_time, `html`, 
                        `md5`, spider_url, writer, wenzhang, pattern) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                        ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
                    """
        #ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        params = (str(self["title"]), str(self["public_time"]), self["html"], str(self["md5"]),
                  str(self["spider_url"]),str(self["writer"]), str(self["wenzhang"]), str(self["pattern"]))

        return insert_mysql, params

class YitikuItem(scrapy.Item):
    # define the fields for your item here like:
    subject = scrapy.Field()
    grade = scrapy.Field()
    pattern = scrapy.Field()
    source_shijuan = scrapy.Field()
    difficulty = scrapy.Field()
    kaodian = scrapy.Field()
    spider_source = scrapy.Field()
    html = scrapy.Field()
    md5 = scrapy.Field()
    spider_url = scrapy.Field()
    topic = scrapy.Field()
    analy = scrapy.Field()
    answer = scrapy.Field()
    source_id = scrapy.Field()

    def get_insert_sql(self):
        insert_mysql = """
            insert ignore into yitiku_shiti_no_0901(`subject`, grade, `topic`, `md5`, spider_url, pattern, 
            source_shijuan, `difficulty`, kaodian, `spider_source`, `analy`, `answer`, `html`, source_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
        """
        #ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        params = (str(self["subject"]), str(self["grade"]), str(self["topic"]), str(self["md5"]),
                  str(self["spider_url"]),str(self["pattern"]),str(self["source_shijuan"]),
                  str(self["difficulty"]), str(self["kaodian"]),str(self["spider_source"]),
                  self["analy"], self["answer"], self["html"], self["source_id"])

        return insert_mysql, params

class YitikuShitiItem(scrapy.Item):
    # define the fields for your item here like:
    subject = scrapy.Field()
    grade = scrapy.Field()
    pattern = scrapy.Field()
    source_shijuan = scrapy.Field()
    difficulty = scrapy.Field()
    kaodian = scrapy.Field()
    spider_source = scrapy.Field()
    html = scrapy.Field()
    md5 = scrapy.Field()
    spider_url = scrapy.Field()
    topic = scrapy.Field()
    analy = scrapy.Field()
    answer = scrapy.Field()
    book = scrapy.Field()
    version = scrapy.Field()

    def get_insert_sql(self):
        insert_mysql = """
            insert ignore into yitiku_shiti_html_0906(`subject`, grade, `topic`, `md5`, spider_url, pattern, 
            source_shijuan, `difficulty`, kaodian, `spider_source`, `analy`, `answer`, book, version, `html`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
        """
        #ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        params = (str(self["subject"]), str(self["grade"]), str(self["topic"]), str(self["md5"]),
                  str(self["spider_url"]),str(self["pattern"]),str(self["source_shijuan"]),
                  str(self["difficulty"]), str(self["kaodian"]),str(self["spider_source"]),
                  self["analy"], self["answer"], str(self["book"]), str(self["version"]), self["html"])

        return insert_mysql, params

class YitikuShijuanItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    subject = scrapy.Field()
    grade = scrapy.Field()
    pattern = scrapy.Field()
    province = scrapy.Field()
    year = scrapy.Field()
    ti_number = scrapy.Field()
    watch_number = scrapy.Field()
    spider_source = scrapy.Field()
    html = scrapy.Field()
    md5 = scrapy.Field()
    spider_url = scrapy.Field()
    source_id = scrapy.Field()
    question_urls = scrapy.Field()

    def get_insert_sql(self):
        insert_mysql = """
            insert ignore into yitiku_0829(`subject`, grade, `title`, `md5`, spider_url, pattern, 
            province, year, ti_number, spider_source, watch_number, html, source_id, question_urls) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
        """
        #ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        params = (str(self["subject"]), str(self["grade"]), str(self["title"]), str(self["md5"]),
                  str(self["spider_url"]),str(self["pattern"]), str(self["province"]),
                  str(self["year"]), str(self["ti_number"]), str(self["spider_source"]),
                  self["watch_number"], str(self["html"]), str(self["source_id"]), str(self["question_urls"]))

        return insert_mysql, params

    def save_to_es(self):
        article = Article()
        article.title = self['title']
        article.subject = self['subject']
        article.grade = self['grade']
        article.pattern = self['pattern']
        article.province = self['province']
        # if "answer" in self:
        #     article.answer = self["answer"]
        article.year = self['year']
        article.ti_number = self['ti_number']
        article.watch_number = self['watch_number']
        article.spider_source = self['spider_source']
        article.html = self['html']
        article.spider_url = self['spider_url']
        article.source_id = self['source_id']

        article.suggest = gen_suggests(Article._doc_type.index, ((article.title,10), (article.subject, 7)))

        article.save()

class YitikuPageUrlItem(scrapy.Item):
    # define the fields for your item here like:
    md5 = scrapy.Field()
    spider_url = scrapy.Field()

