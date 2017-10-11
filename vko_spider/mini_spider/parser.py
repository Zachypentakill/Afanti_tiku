# -*- coding: utf-8 -*-

import re

from afanti_tiku_lib.html.beautify_html import remove_tag

from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.beautify_html import center_image
from afanti_tiku_lib.html.extract import get_html_element, remove_start_tag

import string
OPTION_DICT = {i: k for i, k in enumerate(string.ascii_uppercase)}

UNDERLINE = '<sspan class="afanti_put">{}</sspan>'
LINE_THROUGH = '<sspan class="aft_linethrough">{}</sspan>'

re_p_tag = re.compile(r'<p [^<>]*?>')
re_paper = re.compile(r'^<p>【(.+?)】')
re_year = re.compile(r'((199|200|201)\d)[^\d]')
re_underline = re.compile(r'_{3,}')
re_nbsp = re.compile(r'(&nbsp;){6,}')


class VkoParser(object):

    def __init__(self, archive_image=False, download=False):
        # img 格式化
        self.html_magic = HtmlMagic(74, # XXX, spider_source
                                    archive_image=archive_image,
                                    download=download, beautify=False)


    def parse(self, js, url):
        self.url = url
        self._paper = ''
        self._year = 0

        cols = dict()

        question_html = self.get_question_html(js)
        cols['question_html'] = question_html

        answer_all_html = self.get_answer_all_html(js)
        cols['answer_all_html'] = answer_all_html

        jieda = self.get_jieda(js)
        cols['jieda'] = jieda

        cols['option_html'] = ''
        cols['fenxi'] = ''
        cols['dianping'] = ''

        cols['paper_name'] = self._paper
        cols['difficulty'] = 0
        cols['zhuanti'] = ''
        cols['spider_url'] = url
        cols['subject'] = 0
        cols['spider_source'] = 74
        cols['question_type'] = 0
        cols['question_quality'] = 0
        cols['knowledge_point'] = ''
        cols['exam_year'] = self._year
        cols['exam_city'] = ''

        return cols

    def get_question_html(self, js):
        html_string = js['content']
        html_string = self.format_html(html_string)
        mod = re_paper.search(html_string)
        if mod:
            self._paper = mod.group(1)
            html_string = re_paper.sub('<p>', html_string)

            mod = re_year.search(self._paper)
            if mod:
                self._year = int(mod.group(1))
        return html_string


    def get_answer_all_html(self, js):
        html_string = js.get('answer') or ''
        html_string = self.format_html(html_string)
        return html_string


    def get_jieda(self, js):
        if not js.get('examsResolve'):
            return ''

        jiedas = []
        for er in js['examsResolve']:
            jiedas.append(er['content'])

        html_string = '<br>'.join(jiedas)
        html_string = self.format_html(html_string)
        return html_string


    def format_html(self, html_string):
        html_string = self.fix_any(html_string)
        html_string = center_image(html_string)
        html_string = self.html_magic.bewitch(html_string, spider_url=self.url)
        return html_string


    def fix_any(self, html_string):
        html_string = html_string.replace('\n', '')
        html_string = re_p_tag.sub('<p>', html_string)
        html_string = handle_spans(html_string)
        html_string = remove_tag('<span', html_string)
        html_string = html_string.replace('<p></p>', '')\
                                 .replace('<p><br></p>', '')\
                                 .replace('<div><br></div>', '')\
                                 .replace('<o:p></o:p>', '')\
                                 .replace('</p><br>', '</p>')
        html_string = re_nbsp.sub('&nbsp;'*6, html_string)
        html_string = re_underline.sub(UNDERLINE.format('&nbsp;'*6), html_string)
        html_string = html_string.replace('<sspan', '<span')
        return html_string


def handle_spans(html_string):
    spans = get_html_element('<span [^<>]+(text-decoration|vertical-align)',
                             html_string, regex=True, flags=re.I)

    spans = [span for span in set(spans)]
    spans = sorted(spans, key=lambda x: len(x), reverse=True)
    for span in spans:
        txt = remove_start_tag(span)
        i = span.find('>')
        tag = span[:i].lower()

        if 'text-decoration' in tag:
            if 'underline' in tag:
                nspan = UNDERLINE.format(txt)
                html_string = html_string.replace(span, nspan)

            elif 'none' in tag:
                html_string = html_string.replace(span, txt)

            elif 'line-through' in tag:
                nspan = LINE_THROUGH.format(txt)
                html_string = html_string.replace(span, nspan)

        elif 'vertical-align' in tag:
            if ':sub' in tag:
                nspan = '<sub>{}</sub>'.format(txt)
            elif ':sup' in tag:
                nspan = '<sup>{}</sup>'.format(txt)
            else:
                nspan = txt
            html_string = html_string.replace(span, nspan)

    return html_string


def make_option(options):
    tr_t = '<tr><td class="aft_option" data="{}">{}</td></tr>'
    option = '<table class="aft_option_wrapper" style="width: 100%;"><tbody class="measureRoot">{}</tbody></table>'.format(
        ''.join([tr_t.format(OPTION_DICT[index], td) for index, td in enumerate(options)]))
    return option
