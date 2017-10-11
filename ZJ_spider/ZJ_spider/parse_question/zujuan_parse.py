# -*- coding: utf-8 -*-
import traceback
import json
import ZJ_spider
import pymysql
import pymysql.cursors
from afanti_tiku_lib.question_template.question_template import Question,QuestionFormatter
from multiprocessing import Pool, Process
import re
import time
from w3lib.html import remove_tags
from twisted.enterprise import adbapi
import os
from afanti_tiku_lib.html.beautify_html import center_image
from afanti_tiku_lib.html.image_magic import ImageMagic
from afanti_tiku_lib.html.magic import HtmlMagic
import datetime
import logging

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/yitiku_parse.log', filemode='a')

_DIR = os.path.dirname(ZJ_spider.__file__)
CONFIG_FILE = os.path.join(_DIR, 'config')


def replace_href(strings):
    if strings:
        strinfo = re.search('id="(.+?)"',strings)
        if strinfo is not None:
            strings = strings.replace(strinfo.group(),'')
        strings = strings.replace('src="/', 'src="http://www.yitiku.cn/').replace('src=""', '').replace('alt="菁优网"','alt="阿凡题"')
    return strings

def Data_to_MySQL(datas):
    #采用同步的机制写入mysql
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_db_offline',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    record_dict = {
        'spider_source':18,
        'spider_url': datas['spider_url'],
        'knowledge_point': datas['knowledge_point'],
        'subject': datas['subject'],
        'difficulty': datas['difficulty'],
        'question_html_origin': datas["question_body"],
        'answer_all_html_origin': datas["answer"],
        'fenxi_origin': datas["analy"],
        'html_id': datas["html_id"],
        'question_type': datas['question_type'],
        'paper_name_abbr': datas['paper_name'],
        'flag': datas['flag'],
        'zhuanti': '',
        'exam_year': datas['exam_year'],
        'exam_city': datas['exam_city'],
        'question_quality': '',
        'option_html': '',
        'jieda_origin': '',
        'dianping': ''
    }

    cols, values = zip(*record_dict.items())

    insert_sql = 'insert ignore into {table} ({cols}) values ({values})'.format(
        table='zujuan_web_question_20170930',
        cols=', '.join(['`%s`' % col for col in cols]),
        values=', '.join(['%s' for col in cols])
    )

    if len(datas['question_body']) != 0:
        try:
            cursor.execute(insert_sql, values)
        except Exception as e:
            print(e)
    conn.commit()

def tableToJson(table):
    config = json.load(open(CONFIG_FILE))
    first_id = 0
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='html_archive2',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()
    #sql = 'select * from {} where topic not like "%yitikuimage.oss-cn-qingdao.aliyuncs.com%" '.format(table)
    while True:
        logging.warn('parse the first_id is : {}'.format(first_id))
        sql = 'select * from {0} where html_id > {1} limit 100'.format(table, first_id)
        cur.execute(sql)
        data = cur.fetchall()
        # cur.close()

        if not data:
            break

        try:
            Parser(data)
        except Exception as e:
            print(e)

        first_id = int(data[-1]['html_id'])

def Parser(data):
    for row in data:
        result = parse_detail(row)
        try:
            Data_to_MySQL(result)
        except Exception as e:
            print(e)


def parse_detail(row):
    result = {}
    spider_source = int(row['source'])
    spider_url = row['key']
    html_id = re.findall('-(.+)', spider_url)[0]
    result['spider_url'] = spider_url
    result['spider_source'] = spider_source
    image_parse = HtmlMagic(spider_source=spider_source, download=True, archive_image=False)

    request_info = row["request_info"]
    question_item = eval(request_info)
    result['subject'] = question_item['SubjectId']
    result['paper_name'] = question_item['title']
    result['exam_city'] = question_item['diqu']
    exam_year = re.search(r'([12][90][0189]\d)', question_item['title'])
    if exam_year is not None:
        result['exam_year'] = exam_year.group()

    info = row["info"]
    info = image_parse.bewitch(html_string=info, spider_url=spider_url,
                                spider_source=spider_source)

    if len(info) != 0:
        question_body = re.findall('question_text":"(.+?)","options', info)
        option_html = re.findall('options":(.+?),"answer', info)
        answer = re.findall('answer":"(.+?)","answer_json', info)
        knowledge_point = re.findall('name":"(.+?)"}}', info)
        question_type = re.findall('exam_type":"(.+?)"', info)
        difficulty = re.findall('difficult_index":"(.+?)"', info)

        if len(answer) != 0:
            result["answer"] = answer[0]
        if len(question_body) != 0:
            result["question_body"] = question_body[0]
        if len(option_html) != 0:
            option = []
            options = eval(option_html[0])
            if isinstance(options, dict):
                for keys, values in options.items():
                    value_items = {}
                    value_items['value'] = keys
                    value_items['content'] = values
                    option.append(value_items)
                result["option_lst"] = option
        if len(knowledge_point) != 0:
            result["knowledge_point"] = knowledge_point[0]
        if len(question_type) != 0:
            result["question_type"] = question_type[0]
        if len(difficulty) != 0:
            result["difficulty"] = difficulty[0]


    zujuan = Question(**result)
    zujuans = zujuan.normialize()
    zujuans['flag'] = request_info
    zujuans['html_id'] = int(html_id)


    return zujuans

if __name__ == '__main__':
    jsonData = tableToJson('zujuan_shiti_spider_html_archive_table_20170929')

