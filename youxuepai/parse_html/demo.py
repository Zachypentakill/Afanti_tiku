# -*-coding:utf8-*-
import os
import sys

import re
import json

from afanti_tiku_lib.html.extract import get_html_element, remove_start_tag
from afanti_tiku_lib.html.beautify_html import remove_tag

from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.beautify_html import center_image

from afanti_tiku_lib.latex.util import displaystyle

import string

OPTION_DICT = {i: k for i, k in enumerate(string.ascii_uppercase)}

DIFFS = {
    '低': 25,
    '中': 25 + 33,
    '高': 25 + 33 + 33,
}


class Dz101QuestionParser(object):

    def __init__(self, archive_image=False, download=False):
        self.html_magic = HtmlMagic(56, archive_image=archive_image,
                                    download=download, beautify=False)


    def parse(self, html_string, url, aft_subj_id):
        cols = dict()

        exam_year = 0
        paper_name = ''

        question_html_t = list()
        answer_all_html_t = list()
        fenxi_t = list()

        cols_dict = {
            '"IsTopic"': question_html_t,
            '"optionoption"': question_html_t,
            '"Answer"': answer_all_html_t,
            '"Analytical"': fenxi_t,
        }

        entities = {
            '"IsTopic"': get_question_html,
            '"optionoption"': get_question_html,
            '"Answer"': get_answer_all_html,
            '"Analytical"': get_fenxi,
        }

        elems = get_html_element('<(li|span) class="(IsTopic|Answer|Analytical|optionoption)',
                                 html_string, regex=True)

        q = -1
        for elem in elems:
            for key in entities.keys():
                if key in elem[:30]:
                    entity = entities[key](elem)
                    if q > 0 and key in ('"Answer"', '"Analytical"'):
                        entity = '({}). {}'.format(q, entity)

                    if q == -1 and key == '"IsTopic"':
                        exam_year, paper_name = get_exam_info(entity)
                        entity = remove_exam_info(entity)

                    cols_dict[key].append(entity)

                    if key == '"IsTopic"':
                        q += 1
                    break

        question_all_html = '<br>\n'.join(question_html_t)

        question_html = self.html_magic.bewitch(question_all_html, spider_url=url)
        question_html = center_image(question_html)
        question_html = fix_any(question_html)
        question_html = displaystyle(question_html, latex=False, mml=True)
        cols['question_html_origin'] = question_html

        answer_all_html = '<br>\n'.join(answer_all_html_t)
        answer_all_html = self.html_magic.bewitch(answer_all_html, spider_url=url)
        answer_all_html = center_image(answer_all_html)
        answer_all_html = fix_any(answer_all_html)
        answer_all_html = displaystyle(answer_all_html, latex=False, mml=True)
        cols['answer_all_html_origin'] = answer_all_html

        fenxi = '<br>\n'.join(fenxi_t)
        fenxi = self.html_magic.bewitch(fenxi, spider_url=url)
        fenxi = center_image(fenxi)
        fenxi = fix_any(fenxi)
        fenxi = displaystyle(fenxi, latex=False, mml=True)
        cols['fenxi_origin'] = fenxi

        cols['difficulty'] = get_difficulty(html_string)
        cols['question_type_str'] = get_question_type_str(html_string)

        cols['question_html'] = ''
        cols['option_html'] = ''
        cols['answer_all_html'] = ''
        cols['jieda'] = ''
        cols['fenxi'] = ''
        cols['dianping'] = ''

        cols['option_html_origin'] = ''
        cols['jieda_origin'] = ''
        cols['dianping_origin'] = ''

        cols['zhuanti'] = ''
        cols['paper_name'] = paper_name
        cols['paper_url'] = ''
        cols['spider_url'] = url
        cols['subject'] = aft_subj_id
        cols['spider_source'] = 56
        cols['question_type'] = 0
        cols['question_quality'] = 0
        cols['knowledge_point'] = ''
        cols['exam_year'] = exam_year
        cols['exam_city'] = ''

        return cols

def get_question_html(entity):
    if entity.startswith('<li'):
        qs = get_html_element('<li class="IsTopic">', entity,
                              with_tag=False, limit=1)[0]
        if not qs:
            return ''
    else:
        qs = get_html_element('<span class="optionoption">', entity,
                              with_tag=False, limit=1)[0]
        if not qs:
            return ''

    qs = remove_tag('<XHTML', qs, all=False).strip()

    if entity.startswith('<span'):
        qs = make_option(qs)

    return qs.strip()


def remove_exam_info(qs):
    qs = re.sub(r'^\[([12][90][0189]\d)(?:·|．|●|•)([^\s]+?)\]', '', qs, 1)
    return qs


def make_option(entity):
    options = get_html_element('<span class="option">', entity, with_tag=False)
    tr_t = '<tr><td class="aft_option" data="{}">{}</td></tr>'
    option = '<table class="aft_option_wrapper" style="width: 100%;"><tbody class="measureRoot">{}</tbody></table>'.format(
        ''.join([tr_t.format(OPTION_DICT[index], td) for index, td in enumerate(options)]))
    return option


def get_answer_all_html(entity):
    ans = get_html_element('<li class="Answer">', entity, with_tag=False)[0]
    if not ans:
        return ''

    ans = remove_tag('<XHTML', ans, all=False).strip()
    ans = ans.replace('【答案】', '', 1)
    return ans.strip()

def get_fenxi(entity):
    fx = get_html_element('<li class="Analytical">', entity, with_tag=False)[0]
    if not fx:
        return ''

    fx = remove_tag('<XHTML', fx, all=False).strip()
    fx = fx.replace('【解析】', '', 1)
    return fx.strip()


def get_difficulty(html_string):
    e = get_html_element('<div class="T">', html_string, with_tag=False, limit=1)[0]
    mod = re.search('difficulty">(.+?)<', e)
    if not mod:
        return ''
    dfs = mod.group(1)
    df = DIFFS.get(dfs, 0)
    return df


def get_exam_info(entity):
    mod = re.search(r'^\[([12][90][0189]\d)(?:·|．|●|•)([^\s]+?)\]', entity)
    if not mod:
        return 0, ''
    return int(mod.group(1)), mod.group(2)

def get_question_type_str(html_string):
    e = get_html_element('<div class="T">', html_string, with_tag=False, limit=1)[0]
    mod = re.search('type">(.+?)</tt>', e)
    if not mod:
        return ''
    tp = mod.group(1)
    return tp


def fix_any(html_string):
    maths = get_html_element('<math', html_string, flags=re.I)
    for math in set(maths):
        math_t = '<span class="afanti-latex">{}</span>'.format(math)
        html_string = html_string.replace(math, math_t)

    # 加点字
    spans = get_html_element('<span class="founderdotem">', html_string)
    for span in spans:
        text = remove_start_tag(span)
        aft_tag = '<bdo class="aft_underpoint">{}</bdo>'.format(text)
        html_string = html_string.replace(span, aft_tag)

    return html_string