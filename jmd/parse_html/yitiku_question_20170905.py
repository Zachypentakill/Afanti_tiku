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
from w3lib.html import remove_tags
from afanti_tiku_lib.html.image_magic import ImageMagic
from afanti_tiku_lib.html.magic import HtmlMagic
from jmd import jmd

_DIR = os.path.dirname(jmd.__file__)
CONFIG_FILE = os.path.join(_DIR, 'config')

def writecsv(items):
    strlist = [str(items['source_id']), str(items['key2']), str(items['html']),
               str(items['request_info']), str(items['subject']), str(items['question_type'])]
    strs = ','.join(strlist)
    f.writelines(strs + '\n')

def remove_biaoqian(str_bioaqian):
    if isinstance(str_bioaqian, str):
        # str_bioaqian = str_bioaqian.replace('<\/v>','').replace('<label>','').replace('&nbsp;',' ')
        # str_bioaqian = str_bioaqian.replace('<\/tr>', '</tr>').replace('<\/td>', '</td>').replace('<\/pos>','</pos>')
        # str_bioaqian = str_bioaqian.replace('<\/label>','').replace('<\/div>','</div>').replace('<\/li>','')
        # str_bioaqian = str_bioaqian.replace('<\/ul>','/ul').replace('<v>','').replace('<\/span>','</span>')
        # str_bioaqian = str_bioaqian.replace('<p>', '').replace('<\\/p>', '').replace('; ; ; ;','')
        # str_bioaqian = str_bioaqian.replace('&nbsp', ' ').replace('<u>','').replace('; ; ;','')
        # str_bioaqian = str_bioaqian.replace('; ;', ' ').replace('\/data','/data').replace('<\\/u>','')
        # str_bioaqian = str_bioaqian.replace('<\/sub>','</sub>').replace('<\/sup>','</sup>')
        # str_bioaqian = str_bioaqian.replace('<pos>', '').replace('<\\/pos>', '').replace('<\/ b>','</ b>')
        # str_bioaqian = str_bioaqian.replace('<br \\/>','<br />').replace('\/','/').replace('<\/p>','')
        str_bioaqian = str_bioaqian.replace('&nbsp;',' ').replace('; ; ; ;','').replace("\\/",'/')
        str_bioaqian = str_bioaqian.replace('; ; ;','').replace('&nbsp', ' ')
        str_bioaqian = str_bioaqian.replace('; ;', ' ').replace('\/','/')
        return str_bioaqian
    else:
        print("插入的不是str格式！")

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
        'spider_source':59,
        'spider_url': datas['spider_url'],
        'knowledge_point': datas['knowledge_point'],
        'subject': datas['subject'],
        'difficulty': datas['difficulty'],
        'question_type_name': datas['question_type'],
        'question_html': datas["question_body"],
        'answer_all_html': datas["answer"],
        'fenxi': datas["analy"],
        'html_id': datas["question_id"],
        'book_name': datas["book_name"],
        'version_name': datas["version_name"],
        'question_type_name': datas['question_type_name'],
        'question_type': datas['question_type'],
        'paper_name_abbr': datas['paper_name'],
        'zhuanti': '',
        'exam_year': '',
        'exam_city': '',
        'question_quality': '',
        'option_html': '',
        'jieda': '',
        'dianping': ''
    }

    cols, values = zip(*record_dict.items())

    insert_sql = 'insert ignore into {table} ({cols}) values ({values})'.format(
        table='yitiku_question_20170914',
        cols=', '.join(['`%s`' % col for col in cols]),
        values=', '.join(['%s' for col in cols])
    )

    if len(datas['question_body']) != 0:
        #此处应会有问题
        try:
            cursor.execute(insert_sql, values)
        except Exception as e:
            print(e)
    conn.commit()

def tableToJson(table):
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='html_archive',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()
    #sql = 'select * from %s ' % table
    sql = 'select * from %s limit 320000' % table
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    jsonData = []
    pattern_item = {
        '单选': '1',
        '填空': '2',
        '多选': '4'
    }
    for row in data:
        spider_source = int(row['spider_source'])
        image_parse = HtmlMagic(spider_source=spider_source,download=True, archive_image=False)
        result1 = {}
        spider_url = row['spider_url']
        result1['spider_url'] = spider_url
        question_id = re.findall('shiti/(.+).html', spider_url)
        result1['question_id'] = question_id[0]

        pattern = row['pattern']
        result1['question_type_name'] = pattern
        for key, value in pattern_item.items():
            if key in pattern:
                pattern = value
        if len(pattern) >= 2:
            pattern = '3'
        result1['question_type'] = pattern


        topic = row['topic']
        topic = replace_href(topic)
        topic = remove_tags(text=topic, which_ones=('h1', 'div'))
        topic = image_parse.bewitch(html_string=topic, spider_url=spider_url,
                            spider_source=spider_source)
        result1['question_body'] = topic
        answer = row['answer']
        answer = replace_href(answer)
        answer = image_parse.bewitch(html_string=answer, spider_url=spider_url,
                            spider_source=spider_source)
        result1['answer'] = answer
        analy = row['analy']
        analy = replace_href(analy)
        analy = image_parse.bewitch(html_string=analy, spider_url=spider_url,
                            spider_source=spider_source)
        result1['analy'] = analy

        source_shijuan = row['source_shijuan']
        source_shijuan = re.findall('<span class="colf43">来源：(.+?)</span>', source_shijuan)
        if len(source_shijuan) != 0:
            result1['paper_name'] = source_shijuan[0]

        mapping_dict = {
            'spider_sorce': 'spider_source',
            'subject': 'subject',
            'knowledge_point': 'kaodian',
            'difficulty': 'difficulty',
            'book': 'book',
            'version': 'version',
            'source': 'spider_source'
        }
        result2 = {
            key: row.get(value, '')
            for key, value in mapping_dict.items()
        }

        #result['exam_year'] = row['year']
        #result['exam_city'] = row['province']
        result = dict(result1, **result2)
        jsonData.append(result)
    return jsonData


if __name__ == '__main__':
    jsonData = tableToJson('yitiku_shiti_html_0906')
    pool = Pool()
    # all_content = []
    none_list = []
    for table in jsonData:
        youxuepai = Question(**table)
        a = len(youxuepai['answer']) + len(youxuepai['analy'])
        if a != 0:
            try:
                youxuepais = youxuepai.normialize()
            except Exception as e:
                traceback.print_exc()
                print(e)
            youxuepais['book_name'] = table['book']
            youxuepais['version_name'] = table['version']
            youxuepais['question_type_name'] = table['question_type_name']
            pool.apply_async(func=Data_to_MySQL,args=(youxuepais,))
    pool.close()
    pool.join()


