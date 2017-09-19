# -*- coding: utf-8 -*-
import codecs
from scrapy.pipelines.images import ImagesPipeline
import json
from scrapy.exporters import JsonItemExporter
import pymysql
import pymysql.cursors
from twisted.enterprise import adbapi
import os
from models.es_types import Article
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# _DIR = os.path.dirname(os.path.abspath(__file__))
# CONFIG_FILE = os.path.join(_DIR, 'config')

_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_DIR, 'config')

class JmdPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlTwistedpipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            port = 3306,
            charset = 'utf8',
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,
             )

        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将MySQL插入变成异步
        try:
            query = self.dbpool.runInteraction(self.do_insert, item)
        except Exception as e:
            print(e)

    def do_insert(self, cursor, item):
        try:
            insert_mysql, params = item.get_insert_sql()
            cursor.execute(insert_mysql, params)
        except Exception as e :
            print(e)

class MysqlTwistedForUrlpipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            port = 3306,
            charset = 'utf8',
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,
             )

        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将MySQL插入变成异步
        try:
            query = self.dbpool.runInteraction(self.do_insert, item)
        except Exception as e:
            print(e)

    def do_insert(self, cursor, item):
        insert_mysql = """
            insert ignore into yitiku_shiti_page_url_0905(`md5`, spider_url) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
        """
        #ON DUPLICATE KEY UPDATE question_id=VALUES(question_id)
        for i in range(len(item["md5"])):
            cursor.execute(insert_mysql,(item['md5'][i], item['spider_url'][i]))

class Mysqlpipeline(object):
    def __init__(self):
        config = json.load(open(CONFIG_FILE))
        self.conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], port=3306,
                            cursorclass=pymysql.cursors.DictCursor, db='html_archive', charset= "utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        if item.__class__.__name__ == "YitikuItem":
            insert_mysql = """
                        insert ignore into yitiku_shiti_no_0901(`subject`, grade, `topic`, `md5`, spider_url, pattern, 
                        source_shijuan, `difficulty`, kaodian, `spider_source`, `analy`, `answer`, `html`, source_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
                    """

            self.cursor.execute(insert_mysql, (str(item["subject"]), str(item["grade"]), str(item["topic"]), str(item["md5"]),
                                               str(item["spider_url"]),str(item["pattern"]),str(item["source_shijuan"]),
                                               str(item["difficulty"]), str(item["kaodian"]),str(item["spider_source"]),
                                               item["analy"], item["answer"], item["html"], item["source_id"]))
            self.conn.commit()

class ElasticsearchPipiline(object):
    #将数据写入到es中
    def process_item(self, item, spider):
        #将item转换成es的数据
        item.save_to_es()
        return item