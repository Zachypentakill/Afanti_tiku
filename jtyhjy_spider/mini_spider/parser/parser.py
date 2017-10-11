# -*- coding:utf8-*-
from __future__ import unicode_literals
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import os
import logging
import json
import configparser
import re


from afanti_tiku_lib.dbs.MySQLClient import MySQLClient
from afanti_tiku_lib.html.magic import HtmlMagic

from afanti_tiku_lib.question_template.question_template import Question, Option

db_config_file = os.path.join(
        os.path.expanduser('~'), '.dbinfo')
config = configparser.RawConfigParser(allow_no_value=True)
config.readfp(open(db_config_file))
QUESTION_DICT = dict(
    user=config.get('question', 'username'),
    passwd=config.get('question', 'passwd'),
    host=config.get('question', 'host'),
    port=int(config.get('question', 'port')),
    db=config.get('question', 'db')
)


HEADERS = {
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Referer': 'http://www.jtyhjy.com/sts/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
    }


def convert_str_subject_to_int(string):
     grade_dict = {
         '初中': 0,
         '高中': 20,
         '小学': 40
     }
     subject_dict = {
         '语文': 1,
         '数学': 2,
         '英语': 3,
         '物理': 5,
         '化学': 6,
         '地理': 7,
         '历史': 8,
         '生物': 9,
         '政治': 10,
     }
     subject = 0
     for key in grade_dict.keys():
         if key in string:
             subject = grade_dict[key]
             break
     for key in subject_dict.keys():
         if key in string:
             subject += subject_dict[key]
             break
     if subject // 2 not in [0, 2, 4]:
         subject = 0
     return subject



# sub word tag style
def sub_word_tag(text):
    #chinese font
    pattern_chinese = re.compile(r'<[^<>/]+(style\s*=\s*[\'"][^<>\'"/]+体[^<>\'"/]+[\'"])[^<>/]*?>', flags=re.I | re.U)
    text = pattern_chinese.sub('', text)
    #english font
    pattern_english = re.compile('''(<span)(\s[^<>/]*?)(lang\s*=\s*['"]EN-(?:US|GB)['"])[^<>/]*?(style\s*=\s*['"][^<>\'"]+['"])?''', flags=re.I | re.U)
    text = pattern_english.sub(lambda m: m.group(1) + m.group(2) if m.group(2).strip() else m.group(1), text)
    # MsoNormal class
    pattern = re.compile('''<p\s*?[^<>/]*?class\s*=\s*['"]MsoNormal['"][^<>/]*?>''', flags=re.I | re.U)
    del_attribute = lambda m: re.sub('''(class|align|style)\s*=\s*['"][^<>\'"]+['"]\s*''', '',  m.group(0), flags=re.U | re.I)
    text = pattern.sub(del_attribute, text)

    pattern = re.compile('''(<span\s+[^<>/]*?)(style\s*=\s*['"][^'"<>/]+(?:black|white)[^'"<>/]*?['"])([^<>/]*>)''', flags=re.I | re.U)
    text = pattern.sub(lambda m: m.group(1) + m.group(3), text)
    # convert '<span>A</span>' to 'A'
    pattern = re.compile('<span[^<>/]*?>([^<>]{,2})</span>', flags=re.I | re.U)
    text = pattern.sub(lambda m: m.group(1), text)
    return text
 

class Parser(object):
    def __init__(self):
        self.logger = logging.getLogger('iter')
        self.sql_client = MySQLClient(**QUESTION_DICT)
        self.html_magic = HtmlMagic(spider_source=78, download=True, proxy=True)

    def deal_one_item(self, item):
        html = item['html']
        html_id = item['html_id']
        spider_url = item['key']

        subject_dict = True and item['info'] or {}
        subject_dict = json.loads(subject_dict)
        subject_string = subject_dict.get('name', '')
        subject = convert_str_subject_to_int(subject_string)
        question_item = dict(
            spider_source = 78,
            spider_url = spider_url,
            subject=subject
        )
        question_dict = self.parse(html)
        question_item['knowledge_point'] = question_dict['knowledge_point']
        question_item['paper_name_abbr'] = question_dict['paper_name_abbr']
        question_dict = Question(**question_dict).normialize()
        question_item['question_html'] = question_dict['question_body']
        question_item['option_html'] = ''
        question_item['jieda'] = ''
        question_item['zhuanti'] = ''
        question_item['question_type'] = 0
        question_item['answer_all_html'] = question_dict['answer']
        question_item['fenxi'] = question_dict['analy']
        question_item['dianping'] = question_dict['comment']

        for key in ['question_html', 'option_html', 'answer_all_html',
                    'fenxi', 'dianping']:
            question_item[key] = sub_word_tag(question_item[key])
            question_item[key] = self.html_magic.bewitch(
                  question_item[key], question_item['spider_url'], spider_source=78, headers=HEADERS
            )

        # print(question_item)
        try:
            if self.sql_client.select('select spider_url from question_db_offline.jtyhjy_question_20171010 where spider_url =%s', spider_url):
                self.sql_client.update('delete from question_db_offline.jtyhjy_question_20171010 where spider_url = %s limit 1', spider_url)
            self.sql_client.insert('question_db_offline.jtyhjy_question_20171010', **question_item)
        except Exception as err:
            self.logger.warning(
                'html_id: %s. error happend when insert question: %s',
                html_id, err
            )
            raise err


    def parse(self, html):
        if isinstance(html, dict):
            question_json = html
        else:
            question_json = json.loads(html)

        question_dict = {}
        if not question_json:
            return question_dict
        question_dict['question_body'] = question_json.get('bodyHtmlText', '')
        question_dict['answer'] = question_json.get('answerHtmlText', '')
        question_dict['analy'] = question_json.get('analysisHtmlText', '')
        question_dict['knowledge_point'] = question_json.get('knowledgeName', '')
        question_dict['paper_name_abbr'] = question_json.get('queSource', '')
        question_dict['difficulty'] = question_json.get('difficult', '')

        return question_dict
