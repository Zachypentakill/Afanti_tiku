# -*- coding: utf-8 -*-
import codecs
from scrapy.pipelines.images import ImagesPipeline
import json
from scrapy.exporters import JsonItemExporter
import pymysql
import pymysql.cursors
import random
from twisted.enterprise import adbapi
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class XiehouDuilianPipeline(object):
    def process_item(self, item, spider):
        return item

class CsvDataPipeline(object):
    def __init__(self):
        self.file_txt = open('duilian.csv', 'wt', encoding='utf-8')
        self.file_txt.writelines("网址,题目,上联,下联,横批,md5" + '\n')

    def process_item(self, item, spider):
        for i in range(len(item['md5'])):
            if len(item['md5']) == len(item['hengpi']) and len(item['md5']) == len(item['xialian']):
                strlist = [str(item['html_url']), str(item['title']), str(item['shanglian'][i]), str(item['xialian'][i]), str(item['hengpi'][i]), str(item['md5'][i])]
            elif len(item['md5']) != len(item['hengpi']) and len(item['md5']) == len(item['xialian']):
                strlist = [str(item['html_url']), str(item['title']), str(item['shanglian'][i]),str(item['xialian'][i]), str(item['hengpi']), str(item['md5'][i])]
            strss = ','.join(strlist)
            self.file_txt.writelines(strss + '\n')

    def spider_closed(self, spider):
        self.file_txt.close()


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
            charset='gbk',
            port= 13309,
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,
             )
        #
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
            if item.get('html_url'):
                insert_mysql = """
                            INSERT INTO shengyu_url_1(html_url, title, shanglian, xialian, hengpi, `md5`)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
                        """
                # #only_hengpi的数据库
                # if '横批' in item['hengpi']:
                #     cursor.execute(insert_mysql,
                #                (str(item['html_url']), str(item['title']), str(item['shanglian']),
                #                 str(item['xialian']), str(item['hengpi']), str(item['md5'])))

                # #lianji的数据库
                # for i in range(len(item['md5'])):
                #     cursor.execute(insert_mysql,
                #                    (str(item['html_url']), str(item['title']), str(item['shanglian'][i]),
                #                     str(item['xialian'][i]), str(item['hengpi']), str(item['md5'][i])))

                # #shengyu_url 的数据库 当len等于2的时候
                # cursor.execute(insert_mysql,
                #                (str(item['html_url']), str(item['title']), str(item['shanglian']),
                #                 str(item['xialian']), str(item['hengpi']), str(item['md5'])))

                # shengyu_url 的数据库 当len等于1的时候
                for i in range(len(item['md5'])):
                    if len(item['shanglian'][i]) == len(item['xialian'][i]):
                        cursor.execute(insert_mysql,
                               (str(item['html_url']), str(item['title']), str(item['shanglian'][i]),
                                str(item['xialian'][i]), str(item['hengpi']), str(item['md5'][i])))

                # #shangxialian的数据库
                # for i in range(len(item['md5'])) :
                #     if len(item['md5']) == len(item['hengpi']) and len(item['md5']) == len(item['xialian']):
                #         cursor.execute(insert_mysql,(str(item['html_url']), str(item['title']), str(item['shanglian'][i]),
                #                         str(item['xialian'][i]), str(item['hengpi'][i]), str(item['md5'][i])))
                #     elif len(item['md5']) != len(item['hengpi']) and len(item['md5']) == len(item['xialian']):
                #         if len(item['hengpi']) == 0:
                #             cursor.execute(insert_mysql,
                #                            (str(item['html_url']), str(item['title']), str(item['shanglian'][i]),
                #                             str(item['xialian'][i]), str(item['hengpi']), str(item['md5'][i])))
                #         else:
                #             if '横批' in str(item['xialian'])  or '【横批】' in str(item['xialian']) or '】' in str(item['xialian']) or ' —' in str(item['xialian']):
                #                 cursor.execute(insert_mysql,
                #                            (str(item['html_url']), str(item['title']), str(item['shanglian'][i]),
                #                             str(item['xialian'][i]), str(item['xialian'][i]), str(item['md5'][i])))
                #             else:
                #                 cursor.execute(insert_mysql,
                #                                (str(item['html_url']), str(item['title']), str(item['shanglian'][i]),
                #                                 str(item['xialian'][i]), None, str(item['md5'][i])))
                #     else:
                #         cursor.execute(insert_mysql,
                #                        (str(item['html_url']), str(item['title']), str(item['shanglian'][i]),
                #                         str(item['xialian'][i]), None, str(item['md5'][i])))



        except Exception as e:
            print(str(e))

class Duilian_shengyu_pipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset='gbk',
            port= 13309,
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,
             )
        #
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
            if item.get('html_url'):
                insert_mysql = """
                            INSERT INTO duilian(html_url, title, html, `md5`)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE `md5`=VALUES(`md5`)
                        """

                # duilian 的数据库
                cursor.execute(insert_mysql,(str(item['html_url']), str(item['title']),
                                             str(item['html']), str(item['md5'])))




        except Exception as e:
            print(str(e))

class Mysqlpipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = 'gbk',
            port = 13309,
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,
             )

        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将MySQL插入变成异步
        query = self.dbpool.runInteraction(self.do_insert, item)
    #     query.addErrorback(self.handle_error)

    # def handle_error(self, failure):
    #     #处理异步插入的异常
    #     print failure
#,  school_image_url, school_province, school_city, school_town, school_page, school_type, school_num, school_tel

    def do_insert(self, cursor, item):
        try:
            if item.get('html_url'):
                insert_mysql = """
                            INSERT INTO xiehouyu(html_url, first_title, second_title, `option`, answer, md5)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE md5=VALUES(md5)
                        """
                for i in range(len(item['answer'])):
                    cursor.execute(insert_mysql, (str(item['html_url']), str(item['first_title']), str(item['second_title']), str(item['option'][i]), str(item['answer'][i]), str(item['md5'][i])))
        except Exception as e:
            print(str(e))
