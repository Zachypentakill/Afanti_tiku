# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re
from afanti_tiku_lib.html.beautify_html import remove_tag
from afanti_tiku_lib.html.extract import (
    get_html_element,
    find_valid_elements,
    remove_start_tag
)

#
# http://redmine.lejent.cn/projects/tiku/wiki/题库题型规范模板
#

import string
OPTION_DICT = {i: k for i, k in enumerate(string.ascii_uppercase)}

#
# style
#
UNDERLINE = '<span class="aft_underline">{}</span>'
LINE_THROUGH = '<span class="aft_linethrough">{}</span>'
OVERLINE = '<span class="aft_overline">{}</span>'
PUT = '<span class="aft_put">{}</span>'
UNDERPOINT = '<bdo class="aft_underpoint">{}</bdo>'
OVERPOINT = '<bdo class="aft_overpoint">{}</bdo>'


#
# <table class="aft_option_wrapper" style="width: 100%;">
#     <tbody class="measureRoot">
#         <tr>
#             <td class="aft_option" value="A">
#                  <i class="aft_option_value">A.</i>
#                  <div class="aft_option_content"><p>option content A</p></div>
#             </td>
#         </tr>
#         <tr>
#             <td class="aft_option" value="B">
#                  <i class="aft_option_value">B.</i>
#                  <div class="aft_option_content"><p>option content B</p></div>
#             </td>
#         </tr>
#         <tr>
#             <td class="aft_option" value="C">
#                  <i class="aft_option_value">C.</i>
#                  <div class="aft_option_content"><p>option content C</p></div>
#             </td>
#         </tr>
#         <tr>
#             <td class="aft_option" value="D">
#                  <i class="aft_option_value">D.</i>
#                  <div class="aft_option_content"><p>option content D</p></div>
#             </td>
#         </tr>
#     </tbody>
# </table>
#

# In [29]: options = ['<some>A. test A</some>', 'B. 一般的B.', 'C．特殊的C．']
#
# In [30]: options = remove_option_value(options)
#
# In [31]: options
# Out[31]: ['<some> test A</some>', '一般的B.', '特殊的C．']
#
# In [32]: make_option(options)
# Out[32]: '<table class="aft_option_wrapper" style="width: 100%;"><tbody class="measureRoot"><tr><td class="aft_option" value="A"><i class="aft_option_value">A.</i><div class="aft_option_content"><p><some> test A</some></p></div></td></tr><tr><td class="aft_option" value="B"><i class="aft_option_value">B.</i><div class="aft_option_content"><p>一般的B.</p></div></td></tr><tr><td class="aft_option" value="C"><i class="aft_option_value">C.</i><div class="aft_option_content"><p>特殊的C．</p></div></td></tr></tbody></table>'

re_tag = re.compile(r'<(/|)[a-zA-Z].+?>')


def remove_option_value(raw_options):
    #
    # 一定要保证 raw_options 中的选项带有 A B C D
    #
    options = []
    for index, raw_option in enumerate(raw_options):
        raw_option = raw_option.strip()
        value = OPTION_DICT[index]

        opt_text = re_tag.sub('', raw_option).strip()
        if not opt_text.startswith(value):
            option = raw_option
        else:
            temp = opt_text.lstrip('.．、' + value)
            value = opt_text[:len(opt_text) - len(temp)]
            option = raw_option.replace(value, '', 1).strip()

        options.append(option)

    return options


def make_option(options):
    #
    # options 是选项内容的一个 list (顺序排列)，其中的每一个值都不带选项前缀。
    # 也就是options中的值必需被和remove_option_value一样功能的函数处理过
    #
    tr_t = ('<tr><td class="aft_option" data="{0}">'
                '<i class="aft_option_value">{0}.</i>'
                '<div class="aft_option_content">{1}</div>'
            '</td></tr>')
    option = ('<table class="aft_option_wrapper" style="width: 100%;">'
                '<tbody class="measureRoot">{}</tbody>'
              '</table>').format(
                  ''.join([tr_t.format(OPTION_DICT[index], td) for index, td in enumerate(options)]))
    return option


def format_spans(html_string):
    _LINE_THROUGH = LINE_THROUGH.replace('<span', '<sspan')\
                               .replace('</span>', '</sspan>')
    _UNDERLINE = UNDERLINE.replace('<span', '<sspan')\
                         .replace('</span>', '</sspan>')

    spans = get_html_element('<span [^<>]+(text-decoration|vertical-align)',
                             html_string, regex=True, flags=re.I)

    spans = list(set(spans))
    spans = sorted(spans, key=lambda x: len(x), reverse=True)

    for span in spans:
        txt = remove_start_tag(span)
        i = span.find('>')
        tag = span[:i].lower()

        if 'text-decoration' in tag:
            if 'underline' in tag:
                nspan = _UNDERLINE.format(txt)
                html_string = html_string.replace(span, nspan)

            elif 'none' in tag:
                html_string = html_string.replace(span, txt)

            elif 'line-through' in tag:
                nspan = _LINE_THROUGH.format(txt)
                html_string = html_string.replace(span, nspan)

        elif 'vertical-align' in tag:
            if ':sub' in tag:
                nspan = '<sub>{}</sub>'.format(txt)
            elif ':sup' in tag:
                nspan = '<sup>{}</sup>'.format(txt)
            else:
                nspan = txt
            html_string = html_string.replace(span, nspan)

    while True:
        html_string = remove_tag('<span', html_string, all=False, flags=re.I)
        if not get_html_element('<span', html_string):
            break

    html_string = html_string.replace('<sspan', '<span')\
                             .replace('</sspan>', '</span>')

    return html_string


re_opts = re.compile(r'(<(?:p|P|div|DIV|td|TD|LI|li)[^<>]*>(?:\s|&nbsp;)*|(?:\s|&nbsp;|>)+)([ABCDEFGHIJKLMNOPQRSTUVWXYZ](\.|．|、))')
re_br = re.compile(r'((\s|&nbsp;)*<br[\s/]*>(\s|&nbsp;)*)+', flags=re.I)
def format_options(html_string):
    """
    let the options be single-row
    """

    def _filter(mod):
        if mod.group(1).startswith('<'):
            opt = mod.group(1).replace('&nbsp;', '') + mod.group(2)
        else:
            opt = mod.group(1).replace('&nbsp;', '') + '<br> ' + mod.group(2)
        return opt

    html_string = re_opts.sub(_filter, html_string)
    html_string = re_br.sub('<br> ', html_string)
    return html_string


def format_table_options(html_string):
    """
    将table中的选项转为 aft options
    """

    for table, opts in find_table_options(html_string):
        opts = remove_option_value(opts)
        aft_opt = make_option(opts)
        html_string = html_string.replace(table, aft_opt)
    return html_string


def find_table_options(html_string):
    """
    找 <td> 内容已 ABCD... 开头的 <table>
    """

    tables = find_valid_elements(html_string, '<table', flags=re.I)

    rs = []
    for table in tables:
        tds = get_html_element('<td', table, with_tag=False, flags=re.I)
        if len(tds) < 3:
            continue
        _tds = [re_tag.sub('', td).strip() for td in tds]
        if _startswith_abcd(_tds):
            rs.append([table, tds])
    return rs


def _startswith_abcd(items):
    """
    检查 items 中的 str 是否以 ABCD... 开头
    """

    if not items:
        return False

    for i, item in enumerate(items):
        abcd = OPTION_DICT[i]
        if not item.lstrip().startswith(abcd):
            return False

    return True
