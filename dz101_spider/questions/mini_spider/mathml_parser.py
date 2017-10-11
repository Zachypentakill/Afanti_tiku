# -*- coding: utf-8 -*-

import re
import os
import json
import logging

from afanti_tiku_lib.html.extract import get_html_element
from afanti_tiku_lib.html.beautify_html import remove_tag

from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.beautify_html import center_image
from afanti_tiku_lib.latex.latex2png import to_png, to_pngs
from afanti_tiku_lib.latex.mathml2latex import to_latexes
from afanti_tiku_lib.compat import compat_base64
from afanti_tiku_lib.utils import md5_string, get_image_size

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
        self.uri2oss = self.html_magic.image_magic.uri2oss


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
        cols['question_all_html'] = question_all_html

        question_html = self.html_magic.bewitch(question_all_html, spider_url=url)
        question_html = center_image(question_html)
        question_html = handle_mathml(question_html, self.uri2oss, url)
        if question_html is False:
            return False
        cols['question_html'] = question_html

        answer_all_html = '<br>\n'.join(answer_all_html_t)
        answer_all_html = self.html_magic.bewitch(answer_all_html, spider_url=url)
        answer_all_html = center_image(answer_all_html)
        answer_all_html = handle_mathml(answer_all_html, self.uri2oss, url)
        if answer_all_html is False:
            return False
        cols['answer_all_html'] = answer_all_html

        fenxi = '<br>\n'.join(fenxi_t)
        fenxi = self.html_magic.bewitch(fenxi, spider_url=url)
        fenxi = center_image(fenxi)
        fenxi = handle_mathml(fenxi, self.uri2oss, url)
        if fenxi is False:
            return False
        cols['fenxi'] = fenxi

        cols['difficulty'] = get_difficulty(html_string)
        cols['question_type_str'] = get_question_type_str(html_string)

        cols['dianping'] = ''
        cols['zhuanti'] = ''
        cols['paper_name'] = paper_name
        cols['paper_url'] = ''
        cols['spider_url'] = url
        cols['subject'] = aft_subj_id
        cols['spider_source'] = 56
        cols['question_type'] = 0
        cols['question_quality'] = 0
        cols['knowledge_point'] = ''
        cols['knowledge_point_json'] = json.dumps([])
        cols['exam_year'] = exam_year
        cols['exam_city'] = ''
        cols['option_html'] = ''

        return cols


def handle_mathml(html_string, uri2oss, url):
    img_dir = 'working/latex_imgs/'
    mathmls = get_html_element('<math', html_string)
    latexes = [fix_latex(lt) for lt in to_latexes(mathmls)]
    png_paths = [img_dir + md5_string(latex) + '.png' for latex in latexes]
    png_results = to_pngs(latexes, png_paths, check=False)
    for latex, mathml, png_path, png_result in zip(latexes,
                                                   mathmls,
                                                   png_paths,
                                                   png_results):
        if png_result is False:
            logging.warn('latex2png:{} {}'.format(url, latex))
            return False

        # if not os.path.exists(png_path):
            # if png_result is False:
                # logging.warn('latex2png:{}'.format(latex))
                # return False

        w, h = get_image_size(png_path)

        latex_base64 = compat_base64.b64encode(latex.encode('utf-8')).decode()

        span = '<span data-latex="base64,{}">'.format(latex_base64)
        md5_name = os.path.basename(png_path)
        oss_img_url = uri2oss.convert(md5_name, 56)
        # oss_img_url = png_path
        # img = span + ('<img src="{}" width="{}" heigh="{}" '
                # 'style="vertical-align: middle; margin: 5px 3px 5px 3px"></span>'.format(
                    # oss_img_url, w // 2 + 2, h // 2 + 2))
        img = span + ('<img src="{}" width="{}" heigh="{}" '
                'class="afanti_latex"></span>'.format(
                    oss_img_url, w // 2 + 2, h // 2 + 2))
        html_string = html_string.replace(mathml, img)

    return html_string

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


def fix_latex(latex):
    latex = latex.replace(r"\text{'}", "'")
    latex = latex.replace(r'\stackrel{⃗}', r'\overrightarrow')
    latex = latex.replace(r'\stackrel{⏜}', r'\wideparen')
    latex = latex.replace('<mi mathvariant="normal"/>', '')
    return latex
