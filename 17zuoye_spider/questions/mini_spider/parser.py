# -*- coding: utf-8 -*-

from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.beautify_html import center_image

OPTIONS = dict((str(k), v) for k, v in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))


class Zuoye17QuestionParser(object):

    def __init__(self, archive_image=False, download=False):
        self.html_magic = HtmlMagic(53, archive_image=archive_image,
                                    download=download, beautify=False)

    def parse(self, url, js, aft_subj_id):

        cols = dict()

        # 检测是否是多题 (如：完形填空)
        is_mqs = is_multi_qs(js)

        if is_mqs:
            question_html, option_html = get_multi_question(js)
        else:
            question_html, option_html = get_question(js)

        question_html = fix_any(question_html)
        question_html = self.html_magic.bewitch(question_html, spider_url=url)
        question_html = center_image(question_html)
        cols['question_html_origin'] = question_html
        cols['question_html'] = ''
        if 'afanti-latex' not in question_html:
            cols['question_html'] = question_html

        if option_html:
            option_html = fix_any(option_html)
            option_html = self.html_magic.bewitch(option_html, spider_url=url)
            option_html = center_image(option_html)
        cols['option_html_origin'] = option_html
        cols['option_html'] = ''
        if 'afanti-latex' not in option_html:
            cols['option_html'] = option_html

        ################################################################

        answer_all_html, fenxi = get_answers(js)

        answer_all_html = fix_any(answer_all_html)
        answer_all_html = self.html_magic.bewitch(answer_all_html,
                                                  spider_url=url)
        answer_all_html = center_image(answer_all_html)
        cols['answer_all_html_origin'] = answer_all_html
        cols['answer_all_html'] = ''
        if 'afanti-latex' not in answer_all_html:
            cols['answer_all_html'] = answer_all_html

        fenxi = fix_any(fenxi)
        fenxi = self.html_magic.bewitch(fenxi, spider_url=url)
        fenxi = center_image(fenxi)
        cols['fenxi_origin'] = fenxi
        cols['fenxi'] = ''
        if 'afanti-latex' not in fenxi:
            cols['fenxi'] = fenxi

        ################################################################

        cols['difficulty'] = (js['difficulty_int'] or 0)

        ################################################################

        cols['question_type_name'] = get_question_type_name(js)

        ################################################################

        cols['knowledge_point'] = ''
        cols['jieda_origin'] = ''
        cols['jieda'] = ''
        cols['exam_year'] = 0
        cols['exam_city'] = ''
        cols['spider_url'] = url
        cols['subject'] = aft_subj_id
        cols['zhuanti'] = ''
        cols['dianping'] = ''
        cols['spider_source'] = 53
        cols['question_type'] = 0
        cols['question_quality'] = 0

        return cols


def is_multi_qs(js):
    if js['content']['content']:
        return True
    else:
        return False


def make_question(sub_qs):
    cn = sub_qs['content'].replace('<p><br></p>', '')

    opt = make_option(sub_qs['options'])
    return '{} {}'.format(cn, opt)


class NoContent(Exception): pass


def get_question(js):
    sub_qss = list()

    is_mqs = len(js['content']['sub_contents']) > 1

    if not is_mqs:
        cn = js['content']['sub_contents'][0]['content']
        opt = make_option(js['content']['sub_contents'][0]['options'])
        return cn, opt

    for sub_qs in js['content']['sub_contents']:
        qs = make_question(sub_qs)
        sub_qss.append(qs)

    if not sub_qss:
        raise NoContent('[get_question], {}'.format(js['_id']))

    if len(sub_qss) == 1:
        return sub_qss[0]

    qs = ''.join(['<p>{}. {}</p>'.format(i, q) for i, q in enumerate(sub_qss, 1)])
    return qs, ''


def get_multi_question(js):
    cn = js['content']['content']
    if '<mark type="blank"></mark>' in cn:
        cn = make_mark(cn)

    sub_qs, _ = get_question(js)
    cn = '<p>{}</p>{}'.format(cn, sub_qs)
    return cn, ''


def get_answers(js):
    anss = list()

    if not js['content']['sub_contents']:
        raise NoContent('[get_answers], {}'.format(js['_id']))

    is_mqs = len(js['content']['sub_contents']) > 1

    answer = ''
    fenxi = ''

    for sub_qs in js['content']['sub_contents']:
        if sub_qs['options']:
            ans = ', '.join([OPTIONS[o] if o.isdigit() else o for o in sub_qs['answer_list']])
        else:
            ans = ', '.join(sub_qs['answer_list'])
        if len(ans) == 1 and ans.isdigit():
            ans = OPTIONS(int(ans))

        fx = sub_qs['analysis']

        if is_mqs:
            ans += fx
            anss.append(ans)

        else:
            answer = ans
            fenxi = fx

    if is_mqs:
        answer = ''.join(['<p>{}. {}</p>'.format(i, q) for i, q in enumerate(anss, 1)])

    desc = js['content'].get('content_desc')

    if desc:
        answer = '<p>{}<p/>'.format(desc) + answer

    return answer, fenxi


def get_question_type_name(js):
    tp = js['major_content_type']['name']
    return tp


def make_option(options):
    if not options:
        return ''

    tr_t = '<tr><td class="aft_option" data="{0}">{0}. {1}</td></tr>'
    option = '<table class="aft_option_wrapper" style="width: 100%;"><tbody class="measureRoot">{}</tbody></table>'.format(
        ''.join([tr_t.format(OPTIONS[str(o)], v) for o, v in enumerate(options)]))
    return option


def make_mark(html_string):
    i = 1
    index = 0
    while True:
        index = html_string.find('<mark type="blank"></mark>', index)
        if index == -1:
            break
        html_string = html_string.replace('<mark type="blank"></mark>', str(i), 1)
        i += 1

    return html_string


def fix_any(html_string):
    html_string = html_string.replace('__$$__', '<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>')
    if '<span class="latex">' in html_string:
        html_string = html_string.replace('<span class="latex">', '<span class="afanti-latex">')
    return html_string
