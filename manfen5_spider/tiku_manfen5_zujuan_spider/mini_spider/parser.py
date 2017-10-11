# -*- coding: utf-8 -*-

import re

from afanti_tiku_lib.html.beautify_html import remove_tag, center_image, remove_a_tag
from afanti_tiku_lib.html.format_html import format_spans
from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.extract import (get_html_element,
                                          remove_start_tag,
                                          find_valid_elements)

from afanti_tiku_lib.question_template.question_template import Question

import string
OPTION_DICT = {i: k for i, k in enumerate(string.ascii_uppercase)}

SUBJS = {
 'czdl': 7,
 'czhx': 6,
 'czls': 8,
 'czsw': 9,
 'czsx': 2,
 'czwl': 5,
 'czyw': 1,
 'czyy': 3,
 'czzz': 10,
 'gzdl': 27,
 'gzhx': 26,
 'gzls': 28,
 'gzsw': 29,
 'gzsx': 22,
 'gzwl': 25,
 'gzyw': 21,
 'gzyy': 23,
 'gzzz': 30,
 'xxsx': 42}

# more, see http://redmine.lejent.cn/projects/tiku/wiki/题库题型规范模板

re_opts = re.compile(r'(&nbsp;|\s)+([ABCDEFGHIJKLMNOPQRSTUVWXYZ](\.|．))\s')

class Manfen5ZujuanParser(object):

    def __init__(self, archive_image=False, download=False):
        # img 格式化
        self.html_magic = HtmlMagic(80, # XXX, spider_source
                                    archive_image=archive_image,
                                    download=download, beautify=False)


    def parse(self, html_string, url, info):
        self.url = url
        cols = dict()

        tds = find_valid_elements(html_string, '<td')

        question_html      = self.get_question_html(tds[3])
        jieda              = self.get_jieda(tds[4])
        kps                = self.get_kps(tds[2])
        question_type_name = self.get_question_type_name(tds[0])

        # format question object
        _question = Question(question_body = question_html,
                             jieda         = jieda)
        # unity question style
        unity_question = _question.normialize()

        cols['question_html']      = unity_question['question_body']
        cols['jieda']              = unity_question['jieda']

        cols['knowledge_point']    = kps
        cols['question_type_name'] = question_type_name

        cols['subject']            = self.get_subject(info)
        cols['fenxi']              = ''
        cols['dianping']           = ''
        cols['answer_all_html']    = ''
        cols['option_html']        = ''

        cols['difficulty']         = 0
        cols['zhuanti']            = ''
        cols['spider_url']         = url
        cols['spider_source']      = 80
        cols['question_type']      = 0
        cols['question_quality']   = 0
        cols['exam_year']          = 0
        cols['exam_city']          = ''

        return cols

    def get_question_html(self, html_string):
        e = get_html_element('<div', html_string, with_tag=False, limit=1)
        if e:
            e = e[0]
        else:
            e = remove_start_tag(html_string)
        e = self.fix_any(e)
        e = center_image(e)
        e = self.html_magic.bewitch(e, spider_url=self.url)
        e = self.format_options(e)
        return e.strip()

    def get_jieda(self, html_string):
        e = get_html_element('<font color=red>', html_string,
                             with_tag=False, limit=1)[0]
        e = self.fix_any(e)
        e = center_image(e)
        e = self.html_magic.bewitch(e, spider_url=self.url)
        if e.endswith('</div></p>'):
            e = e[:-4]
        return e.strip()

    def get_kps(self, html_string):
        e = get_html_element('<b', html_string, with_tag=False, limit=1)[0].replace(',', ';')
        return e.strip()

    def get_question_type_name(self, html_string):
        e = get_html_element('题型：<b>', html_string, with_tag=False, limit=1)[0]
        return e.strip()

    def get_subject(self, info):
        return SUBJS.get(info['subj'])

    def fix_any(self, html_string):
        html_string = format_spans(html_string)
        html_string = remove_tag('<font', html_string)
        html_string = remove_a_tag(html_string)
        return html_string.strip()

    def format_options(self, html_string):
        html_string = re_opts.sub(r' <br>\2 ', html_string)
        return html_string
