# -*- coding: utf-8 -*-
import codecs
from scrapy.pipelines.images import ImagesPipeline
import json
from scrapy.exporters import JsonItemExporter
import pymysql
import pymysql.cursors
from twisted.enterprise import adbapi
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class Youxuepai_CSV_Pipeline(object):
    def __init__(self):
        self.file_csv = open('youxuepai_id.csv', 'wt')

    def process_item(self, item, spider):
        if len(item["json_id"]) != 0:
            for i in range(len(item["json_id"])):
                self.file_csv.writelines(item["question_id"][i] + '\t')

    def spider_closed(self, spider):
        self.file_csv.close()

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
