# -*- coding: utf-8 -*-
import traceback
import json
import pymysql
import pymysql.cursors
from question_template import Question,QuestionFormatter
from multiprocessing import Pool, Process
import re
import time
from twisted.enterprise import adbapi
import os
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.html.image_magic import ImageMagic
from afanti_tiku_lib.html.magic import HtmlMagic
from w3lib.html import remove_tags

_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_DIR, 'config')

def writecsv(items):
    strlist = [str(items['source_id']), str(items['key2']), str(items['html']),
               str(items['request_info']), str(items['subject']), str(items['question_type'])]
    strs = ','.join(strlist)
    f.writelines(strs + '\n')

def remove_biaoqian(str_bioaqian):
    if isinstance(str_bioaqian, str):
        str_bioaqian = str_bioaqian.replace('&nbsp;',' ').replace('; ; ; ;','').replace("\\/",'/')
        str_bioaqian = str_bioaqian.replace('; ; ;','').replace('&nbsp', ' ')
        str_bioaqian = str_bioaqian.replace('; ;', ' ').replace('\/','/')
        return str_bioaqian
    else:
        print("插入的不是str格式！")


def Data_to_MySQL(datas):
    #采用同步的机制写入mysql
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_db_offline',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    # record_dict = {
    #     'spider_source':75,
    #     'spider_url': '',
    #     'knowledge_point': '',
    #     'subject': '',
    #     'difficulty': '',
    #     'question_type': '',
    #     'question_html': '',
    #     'question_html_origin': '',
    #     'option_html': '',
    #     'option_html_origin': '',
    #     'answer_all_html': '',
    #     'answer_all_html_origin': '',
    #     'jieda': '',
    #     'jieda_origin': '',
    #     'fenxi': '',
    #     'fenxi_origin': '',
    #     'dianping': '',
    #     'dianping_origin': '',
    #     'html_id': '',
    # }
    #
    # cols, values = zip(*record_dict.items())
    #
    # sql = 'insert ignore into {table} ({cols}) values ({values})'.format(
    #     table='youxuepai_parse_0823',
    #     cols=', '.join(['`%s`' % col for col in cols]),
    #     values=', '.join(['`%s`' for col in cols])
    # )
    #datas["sorce"] = 75
    insert_sql = """
                    insert ignore into youxuepai_parse_0914(spider_source, spider_url, knowledge_point,
                     `subject`, difficulty, question_type, question_html,question_html_origin,
                    answer_all_html, answer_all_html_origin, jieda, jieda_origin, fenxi, fenxi_origin, 
                    dianping, dianping_origin, html_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
    if len(datas['question_body']) != 0:
        cursor.execute(insert_sql, (
            75, datas["spider_url"], datas["knowledge_point"], datas["subject"], datas["difficulty"],
            datas["question_type"], '', datas["question_body"], '', datas["answer"], '', datas["jieda"],
            '', datas["analy"], datas["comment"], datas["comment"], datas["question_id"]))
    else:
        cursor.execute(insert_sql, (
            75, datas["spider_url"], datas["knowledge_point"], datas["subject"], datas["difficulty"],
            datas["question_type"], '', '', '', datas["answer"], '', datas["jieda"],
            '', datas["analy"], datas["comment"], datas["comment"], datas["question_id"]))
    conn.commit()


    # 异步插入数据库
#     dbparms = dict(
#         host='10.44.149.251',
#         user='liyanfeng',
#         passwd='AFtdbliyf7893',
#         db='question_db_offline',
#         port=3306,
#         charset= "utf8",
#         use_unicode=True,
#         cursorclass = pymysql.cursors.DictCursor,
#         )
#     dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
#     try:
#         dbpool.runInteraction(do_insert , datas)
#     except Exception as e:
#         print(e)
#
# def do_insert(cursor, datas):
#     try:
#         insert_sql = """
#             insert ignore into youxuepai_parse_0807(spider_source, spider_url, knowledge_point, `subject`,
#             difficulty, question_type,question_html_origin,
#             answer_all_html_origin, jieda_origin, fenxi_origin, dianping_origin, html_id)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#         if len(datas['question_body']) != 0:
#             cursor.execute(insert_sql, (
#             datas["source"], datas["spider_url"], datas["knowledge_point"], datas["subject"], datas["difficulty"],
#             datas["question_type"], datas["question_body"], datas["answer"], datas["jieda"], datas["analy"],
#             datas["comment"], datas["question_id"]))
#         else:
#             datas['question_body'] = None
#             cursor.execute(insert_sql, (
#             datas["source"], datas["spider_url"], datas["knowledge_point"], datas["subject"], datas["difficulty"],
#             datas["question_type"], datas["question_body"], datas["answer"], datas["jieda"], datas["analy"],
#             datas["comment"], datas["question_id"]))
#
#     except Exception as e:
#         print(e)

def tableToJson(table):
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='html_archive',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()
    #sql = 'select * from {}  where html like "%img%" limit 300'.format(table)
    sql = 'select * from %s limit 100000,100000' % table
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    jsonData = []
    for row in data:
        image_parse = HtmlMagic(75,download=True, archive_image=False)
        # row = list(row)
        result = {}  # temp store one jsonObject
        result['question_id'] = row['source_id']
        result['spider_sorce'] = 75
        result['spider_url'] = row['key2']
        result['subject'] = row['subject']
        result['question_type'] = row['question_type']

        #由于html解析后出现"aorder":false等情况，如果不加下列两行，则出现name 'false' is not defined报错
        false = False
        true = True
        null = None
        try:
            if isinstance(row['html'], str):
                html_contents = row['html']
                # try:
                #     html_contents = image_parse.bewitch(html_string=html_contents, spider_url=row['key2'],
                #                                         spider_source='75')
                # except Exception as e:
                #     print(traceback.print_exc())
                html_contents = remove_biaoqian(html_contents)
                html_contents = eval(html_contents)
                if isinstance(html_contents,bytes):
                    html_contents = html_contents.decode()
                    html_contents = image_parse.bewitch(html_string=html_contents, spider_url=row['key2'],
                                                        spider_source='75')
                    html_content = eval(html_contents)
                elif isinstance(html_contents,dict):
                    html_contents = image_parse.bewitch(html_string=str(html_contents), spider_url=row['key2'],
                                                        spider_source='75')
                    html_content = eval(html_contents)

        except Exception as e:
            # print(row)
            # print(row['html'])
            # print('++' * 20)
            # print(traceback.print_exc())
            # print(e)
            pass

        mapping_dict = {
            'difficulty': 'difficulty',
            'question_body': 'prompt',
            'comment': 'comment',
            'analy': 'parse'
        }

        result2 = {
            key: html_content.get(value, '')
            for key, value in mapping_dict.items()
            }

        try:
            options = html_content['options']
            option = []
            if options:
                for keys, values in options.items():
                    value_items = {}
                    value_items['value'] = keys
                    value_items['content'] = values
                    option.append(value_items)
            result['option_lst'] = option
        except:
            pass

        try:
            answer = html_content['answer']
            if len(answer) == 0:
                answer = ''
                result['answer'] = answer
            else:
                if isinstance(answer, str):
                    result['answer'] = answer
                elif isinstance(answer, list):
                    answers = ''
                    for i in answer:
                        if isinstance(i, str):
                            answers += i + ' '
                        elif isinstance(i, list):
                            answers += i[0] + ' '
                    if len(answers) == 0:
                        answers = ''
                    result['answer'] = answers
        except:
            pass

        try:
            sub_question_lst = html_content['items']
            sub_question_lsts = []
            if sub_question_lst:
                for i in range(len(sub_question_lst)):
                    sub_question = parse_sub_question_lst(sub_question_lst[i])
                    sub_question_lsts.append(sub_question)
                result['sub_question_lst'] = sub_question_lsts
        except:
            pass

        try:
            result['flag'] = row['flag']
        except:
            pass
        result1 = dict(result , **result2)
        # question_body = result1['question_body']
        # result1['question_body'] = image_parse.bewitch(html_string=question_body, spider_url=row['key2'],
        #                                     spider_source='75')
        # if len(result1['answer']) != 0:
        #     answer = result1['answer']
        #     result1['answer'] = image_parse.bewitch(html_string=answer, spider_url=row['key2'],
        #                                                    spider_source='75')
        jsonData.append(result1)
        #jsonData.append(result)
    return jsonData

def parse_sub_question_lst(row):
    result ={}
    try:
        gid = row['gid']
        number = re.findall('.+tion:(.+?)-sub', gid)
        newnumnber = re.findall(number[0])
        result['question_id'] = newnumnber
    except:
        pass

    try:
        answer = row['answer']
        if answer is None:
            result['answer'] = ''
        else:
            result['answer'] = answer
    except:
        pass

    try:
        result['sub_question_lst'] = row['items']
    except:
        pass

    try:
        options = row['options']
        option = []
        if options:
            for keys, values in options.items():
                value_items = {}
                value_items['value'] = keys
                value_items['content'] = values
                option.append(value_items)
        result['option_lst'] = option
    except:
        pass

    mapping_dict = {
        'difficulty': 'difficulty',
        'comment': 'comment',
        'subject': 'subjectId',
        'question_type': 'qtypeId',
        'score': 'score',
        'question_body': 'prompt',
        'analy': 'parse'
    }

    result2 = {
        key: row.get(value, '')
        for key, value in mapping_dict.items()
    }
    result1 = dict(result, **result2)
    return result1


if __name__ == '__main__':
    jsonData = tableToJson('youxuepai_0802')
    s = []
    pool = Pool()
    print(time.time())
    # all_content = []
    for table in jsonData:
        youxuepai = Question(**table)
        a = len(youxuepai['answer']) + len(youxuepai['analy']) + len(youxuepai['question_body']) \
            + len(youxuepai['option_lst']) + len(youxuepai['sub_question_lst'])
        if a != 0:
            try:
                youxuepais = youxuepai.normialize()
            except Exception as e:
                traceback.print_exc()
                print(youxuepai)
                print(table)
                print(e)
            pool.apply_async(func=Data_to_MySQL,args=(youxuepais,))
    pool.close()
    pool.join()
    # for table in jsonData:
    #     youxuepai = Question(**table)
    #     a = len(youxuepai['answer']) + len(youxuepai['analy']) + len(youxuepai['question_body']) \
    #         + len(youxuepai['option_lst']) + len(youxuepai['sub_question_lst'])
    #     if a != 0:
    #         youxuepais = youxuepai.normialize()
    #         none_list.append(youxuepais)
    # a = none_list
    # pass

