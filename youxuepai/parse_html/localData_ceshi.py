# -*-coding:utf8-*-

import json
import pymysql
import pymysql.cursors
from question_template import Question, QuestionFormatter
from multiprocessing import Pool, Process


def writecsv(items):
    strlist = [str(items['source_id']), str(items['key2']), str(items['html']),
               str(items['request_info']), str(items['subject']), str(items['question_type'])]
    strs = ','.join(strlist)
    f.writelines(strs + '\n')


def tableToJson(table):
    conn = pymysql.connect(host='10.44.149.251', user='liyanfeng', passwd='AFtdbliyf7893', db='html_archive',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    # conn = pymysql.connect(host='localhost', user='root', passwd='1234',
    #                        db='youxuepai', port=3306, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    sql = 'select * from %s' % table
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    jsonData = []
    result = {}
    for row in data:
        # row = list(row)
        result = {}  # temp store one jsonObject
        result['question_id'] = row['source_id']
        result['spider_sorce'] = 'www.anoah.com'
        result['spider_url'] = row['key']
        # #知识点是啥
        # result['knowledge_point'] = 0
        result['subject'] = row['subject']
        # #专题是啥
        # result['zhuanti'] = 0
        # # 如果它是某一年的中考题，那么该选项记录了时间，如果没有则用-1表示
        # result['exam_year'] = -1
        # #如果它是某一年的中考题，那么该选项记录了城市，如果没有则用空表示
        # result['exam_city'] = None
        result['question_type'] = row['question_type']
        # #题目质量，主要出现在用菁优网抓取的题目当中
        # result['question_quality'] = None
        html_content = dict(eval(row['html']))
        try:
            result['difficulty'] = html_content['difficulty']
        except:
            result['difficulty'] = None
        try:
            result['question_html'] = html_content['prompt']
        except:
            result['question_html'] = None
        try:
            result['option_html'] = html_content['option']
        except:
            result['option_html'] = None
        try:
            result['answer_all_html'] = html_content['answer']
        except:
            result['answer_all_html'] = None
        try:
            result['fenxi'] = html_content['parse']
        except:
            result['fenxi'] = None
        try:
            result['dianping'] = html_content['comment']
        except:
            result['dianping'] = None
            # result['jieda'] = None
        # 题目标志字段
        result['flag'] = row['flag']
    return jsonData


if __name__ == '__main__':
    jsonData = tableToJson('anoah_sub_page_html_archive_0119')
    # with open('youxuepai_parse_0807.csv', 'wt') as f:
    #     f.writelines("source_id, key2, html, request_info, subject, question_type" + '\n')
    # f.close()
    for table in jsonData:
        youxuepai = Question(table)


