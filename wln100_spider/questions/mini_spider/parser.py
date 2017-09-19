# -*- coding: utf-8 -*-

import re
import json

from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.beautify_html import center_image
from afanti_tiku_lib.html.beautify_html import remove_tag


class Wln100QuestionParser(object):

    def __init__(self, archive_image=False, download=False):
        self.html_magic = HtmlMagic(52, archive_image=archive_image,
                                    download=download, beautify=False)

    def parse(self, key, qs_json, as_json, aft_subj_id):

        cols = dict()

        question_html = qs_json['test']
        question_html = self.html_magic.bewitch(question_html,
                                                spider_url=key)
        question_html = fix_any(question_html)
        cols['question_html'] = center_image(question_html)

        ################################################################

        if not qs_json.get('diff'):
            difficulty = 0
        else:
            difficulty = (100 - int(qs_json.get('diff', 0) * 100))
        cols['difficulty'] = difficulty

        ################################################################

        paper_name = (qs_json.get('docname') or '')
        cols['paper_name'] = paper_name

        ################################################################

        mod = re.search(r'([12][09][0189]\d)[^\d]', paper_name)
        if mod:
            exam_year = mod.group(1)
        else:
            exam_year = 0
        cols['exam_year'] = int(exam_year)

        ################################################################

        cols['question_type_str'] = (qs_json.get('typesname') or '')

        ################################################################

        as_js = as_json['data'][1][0][0]
        answer_all_html = self.html_magic.bewitch((as_js.get('answer') or ''),
                                                  spider_url=key)
        answer_all_html = fix_any(answer_all_html)
        cols['answer_all_html'] = center_image(answer_all_html)

        ################################################################

        fenxi = self.html_magic.bewitch((as_js.get('analytic') or ''),
                                        spider_url=key)
        fenxi = fix_any(fenxi)
        cols['fenxi'] = center_image(fenxi)

        ################################################################

        knowledge_point_json = list()
        knowledge_point = list()
        kpstr = (as_js.get('kllist') or '')
        kpstr = remove_tag('<span', kpstr, all=True)
        kpl = kpstr.split('<br>')
        for kps in kpl:
            kps = kps.split(' >> ')
            knowledge_point.append(kps[-1])
            knowledge_point_json.append(kps)
        knowledge_point = ';'.join(knowledge_point)
        knowledge_point_json = json.dumps(knowledge_point_json,
                                          ensure_ascii=False)
        cols['knowledge_point'] = knowledge_point
        cols['knowledge_point_json'] = knowledge_point_json

        ################################################################

        other_info = (as_js.get('remark') or '')
        other_info = self.html_magic.bewitch(other_info, spider_url=key)
        other_info = fix_any(other_info)
        cols['other_info'] = center_image(other_info)

        ################################################################

        cols['spider_url'] = key
        cols['subject'] = aft_subj_id
        cols['exam_city'] = ''
        cols['paper_url'] = ''
        cols['zhuanti'] = ''
        cols['option_html'] = ''
        cols['jieda'] = ''
        cols['dianping'] = ''
        cols['spider_source'] = 52
        cols['question_type'] = 0
        cols['question_quality'] = 0

        return cols


def fix_any(html_string):
    html_string = re.sub(r'_{6,}', '______', html_string)
    html_string = html_string.replace('<p>无</p>', '')
    return html_string
