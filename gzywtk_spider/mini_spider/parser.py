# -*- coding: utf-8 -*-

import re
import json

from afanti_tiku_lib.html.extract import get_html_element
from afanti_tiku_lib.html.beautify_html import remove_tag

from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.beautify_html import center_image

import string
OPTION_DICT = {i: k for i, k in enumerate(string.ascii_uppercase)}

re_kps = re.compile(r'"_blank">(.+?)</a>')
re_paper = re.compile(r'<a href="(/sjshow/\d+.html)" target="_blank">(.+?)</a>')


class GzywtkParser(object):

    def __init__(self, archive_image=False, download=False):
        # img 格式化
        self.html_magic = HtmlMagic(68, # XXX, spider_source
                                    archive_image=archive_image,
                                    download=download, beautify=False)


    def parse(self, html_string, url):
        self.url = url

        cols = dict()

        question_html, jieda = self.get_question_html(html_string)
        cols['question_html'] = question_html
        cols['jieda'] = jieda

        kps = self.get_kps(html_string)
        cols['knowledge_point'] = kps

        paper_url, paper_name = self.get_paper(html_string)

        cols['paper_url'] = paper_url
        cols['paper_name'] = paper_name

        cols['answer_all_html'] = ''
        cols['fenxi'] = ''
        cols['dianping'] = ''

        cols['difficulty'] = 0
        cols['zhuanti'] = ''
        cols['spider_url'] = url
        cols['subject'] = 21
        cols['spider_source'] = 68
        cols['question_type'] = 0
        cols['question_quality'] = 0
        cols['exam_year'] = 0
        cols['exam_city'] = ''
        cols['option_html'] = ''

        return cols


    def get_question_html(self, html_string):
        rs = []
        cns = get_html_element('<div class="content">', html_string, with_tag=False)
        for cn in cns:
            cn = abs_url(cn)
            cn = center_image(cn)
            cn = self.html_magic.bewitch(cn, spider_url=self.url)
            rs.append(cn.strip())
        rs[1] = self.fix_any(rs[1]).replace('\r', '').strip()
        return rs


    def get_kps(self, html_string):
        for line in html_string.split('\n'):
            if '<b>考点详细：</b>' in line:
                kps = re.findall('</b>(.+?)</li>', line)
                kps2 = kps[0].replace('－', ';')
                return ';'.join(re_kps.findall(line)) or kps2


    def get_paper(self, html_string):
        e = re.search('所属试卷：(.+?)</a>', html_string).group()
        #e = get_html_element('<li>所属试卷：', html_string, limit=1)[0]
        mod = re_paper.search(e)
        if mod:
            paper = 'http://www.gzywtk.com' + mod.group(1)
            paper_name = mod.group(2)
            return paper, paper_name
        else:
            return '', ''


    def fix_any(self, html_string):
        i = html_string.find('<a href=')
        return html_string[:i]


def abs_url(html_string):
    html_string = html_string.replace('src="/', 'src="http://www.gzywtk.com/')
    return html_string


def make_option(options):
    tr_t = '<tr><td class="aft_option" data="{}">{}</td></tr>'
    option = '<table class="aft_option_wrapper" style="width: 100%;"><tbody class="measureRoot">{}</tbody></table>'.format(
        ''.join([tr_t.format(OPTION_DICT[index], td) for index, td in enumerate(options)]))
    return option
