# -*- coding: utf-8 -*-

import re
import json

from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.beautify_html import center_image
from afanti_tiku_lib.html.beautify_html import remove_tag
from lxml.html import fromstring
from lxml.html import etree
from w3lib.html import remove_tags
from afanti_tiku_lib.question_template.question_template import Question


class Wln100QuestionParser(object):

    def __init__(self, archive_image=False, download=False):
        self.html_magic = HtmlMagic(52, archive_image=archive_image,
                                    download=download, beautify=False)
        self.subject_item = {
            '语文': '1',
            '数学': '2',
            '英语': '3',
            '科学': '4',
            '物理': '5',
            '化学': '6',
            '地理': '7',
            '历史': '8',
            '生物': '9',
            '政治': '10'
        }
        self.pattern_item = {
            '单选': '1',
            '填空': '2',
            '多选': '4',
            '选择': '1'
        }

    def parse(self, key, qs_json, as_json, html_id):

        cols = dict()

        html = self.html_magic.bewitch(qs_json,spider_url=key)
        html = fix_any(html)
        html = center_image(html)

        ################################################################

        knowledge_point = re.findall('<div class="answer-context f-roman">(.+?)</div>', html, re.S)
        if len(knowledge_point) != 0:
            knowledge_point_jsons = []
            knowledge_points = ''
            knowledge_point = knowledge_point[0]
            knowledge_point_json = knowledge_point.split('<br/>')
            for i in knowledge_point_json:
                knowledge_points += remove_tags(i).split(' >> ')[-1] + ';'
                node_i = remove_tags(i).split(' >> ')
                #node_i = json.dumps(node_i, ensure_ascii=False)
                knowledge_point_jsons.append(node_i)
            knowledge_point_jsons = json.dumps(knowledge_point_jsons, ensure_ascii=False)
            cols['knowledge_point'] = knowledge_points[ : -2]
            cols['knowledge_point_json'] =  knowledge_point_jsons

        ################################################################

        paper_name = re.findall('id="docname">(.+?)</span>',html)
        if len(paper_name) != 0:
            paper_name = paper_name[0]
            cols['paper_name_abbr'] = paper_name
            subject = 0
            for key1,value1 in self.subject_item.items():
                if key1 in paper_name:
                    subject = value1
            cols['subject'] = subject

        ################################################################

        question_type_str = re.findall('<p class="left">(.+?)</p><p class="right">', html)
        if len(question_type_str) != 0:
            question_type_str = question_type_str[0]
            cols['question_type_str'] = question_type_str
            for keys, values in self.pattern_item.items():
                if keys in question_type_str:
                    question_type_str = values
            if len(question_type_str) >= 2:
                question_type_str = '3'
            cols['question_type'] = question_type_str

        ################################################################

        question_html = re.findall('<div class="test-item-body TD-body f-roman">(.+?)</div>', html, re.S)
        question_html = question_html[0].strip()
        #cols['question_html'] = question_html

        ################################################################

        diff = re.findall('class="staryellow">(.+?)<a', html)
        difficulty = len(diff) * 20
        cols['difficulty'] = difficulty

        ################################################################

        mod = re.search(r'([12][09][0189]\d)[^\d]', paper_name)
        if mod:
            exam_year = mod.group(1)
        else:
            exam_year = 0
        cols['exam_year'] = int(exam_year)

        ################################################################

        as_js = as_json['data'][1][0][0]
        answer_all_html = self.html_magic.bewitch((as_js.get('answer') or ''),
                                                  spider_url=key)
        answer_all_html = fix_any(answer_all_html)
        answer_all_html = center_image(answer_all_html)
        #cols['answer_all_html'] = center_image(answer_all_html)

        ################################################################

        fenxi = self.html_magic.bewitch((as_js.get('analytic') or ''),
                                        spider_url=key)
        fenxi = fix_any(fenxi)
        fenxi = center_image(fenxi)
        #cols['fenxi'] = fenxi

        ################################################################

        _question = Question(question_body=question_html,
                             answer=answer_all_html,
                             analy=fenxi, )
        standard_question = _question.normialize()
        cols['question_html'] = standard_question['question_body']
        cols['answer_all_html'] = standard_question['answer']
        cols['fenxi'] = standard_question['analy']

        ################################################################

        other_info = (as_js.get('remark') or '')
        other_info = self.html_magic.bewitch(other_info, spider_url=key)
        other_info = fix_any(other_info)
        cols['other_info'] = center_image(other_info)

        ################################################################

        cols['spider_url'] = key
        cols['exam_city'] = ''
        cols['paper_url'] = ''
        cols['zhuanti'] = ''
        cols['option_html'] = ''
        cols['jieda'] = ''
        cols['dianping'] = ''
        cols['spider_source'] = 52
        cols['question_quality'] = 0
        cols['html_id'] = html_id

        return cols


def fix_any(html_string):
    html_string = re.sub(r'_{6,}', '______', html_string)
    html_string = html_string.replace('<p>无</p>', '')
    return html_string
