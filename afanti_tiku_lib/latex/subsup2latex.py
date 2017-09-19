# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import logging
import re

from afanti_tiku_lib.html.extract import find_valid_elements, remove_start_tag


def subsup_to_latex(html_string):
    """
    convert sub/sup to latex "_{}" / "^{}"

    html_string must be unicode literals
    """

    html_string = unity_brackets(html_string)

    while True:
        s_tags = find_valid_elements(html_string, '<(sub|sup)',
                                     regex=True, flags=re.I | re.U)

        if not s_tags:
            html_string = _restore_latex(html_string)
            return html_string

        for s_tag in s_tags:
            index = html_string.find(s_tag)
            which_pre = ''
            try:
                which_pre = _find_which_pre(html_string[:index])
            except Exception as err:
                logging.error('[_find_which_pre]: {}'.format(err))
                which_pre = _find_first_not_empty(html_string[:index])

            item = remove_start_tag(s_tag).strip(' \xa0').rstrip('\\').strip(' \xa0')

            if s_tag.lower().startswith('<sub'):
                tex = '<latextag>{{{}}}_{{{}}}</latextag>'.format(
                    which_pre.strip(' \xa0'), item)
            else:
                tex = '<latextag>{{{}}}^{{ {} ##addspace##}}</latextag>'.format(
                    which_pre.strip(' \xa0'), item)

            html_string = (html_string[:index - len(which_pre)]
                           + tex
                           + html_string[index + len(s_tag):])


BRACKETS = set([']', '}', ')'])
BRACKET_DICT = {
    '[': ']',
    '(': ')',
    '{': '}',
}


class NoMatchRelativeBracket(Exception): pass


def _find_which_pre(html_string):
    """
    find the item of "{item}_{sub}" or "{item}^{sup}"
    """

    if not html_string:
        return html_string

    p = len(html_string) - 1
    stack = list()

    while p >= 0:
        if re.search(r'\s', html_string[p]):
            pass
        elif html_string[p] in BRACKET_DICT:
            if not stack:
                raise NoMatchRelativeBracket('stack is empty, char: {}'.format(html_string[p]))
            if html_string[p] in BRACKET_DICT and BRACKET_DICT.get(html_string[p]) != stack[-1]:
                raise NoMatchRelativeBracket('stack top is {}, but char is {}'.format(stack[-1], html_string[p]))
            else:
                stack.pop()
                if not stack:  # end
                    break
        elif html_string[p] in BRACKETS:
                stack.append(html_string[p])
        else:
            if not stack:
                break
        p -= 1

    if stack:  # bad bracket pairs
        raise NoMatchRelativeBracket('bad bracket pairs, "{}"'.format(html_string[p+1:]))

    return html_string[p:]


def _find_first_not_empty(html_string):
    p = len(html_string) - 1

    while p >= 0:
        if re.search(r'\s', html_string[p]):
            pass
        else:
            break
        p -= 1

    return html_string[p:]


def unity_brackets(html_string):
    html_string = html_string.replace('［', '[')\
                             .replace('］', ']')\
                             .replace('（', '(')\
                             .replace('）', ')')\
                             .replace('｛', '{')\
                             .replace('｝', '}')
    return html_string


def _restore_latex(html_string):
    """
    replace <latextag> </latextag> to \( \) at only outsider of latex
    """

    latextags = find_valid_elements(html_string, '<latextag>')
    for latextag in latextags:
        latextag_t = latextag.replace('<latextag>', '').replace('</latextag>', '')
        latextag_t = '<span class="afanti-latex">\(##delspace##{}\)</span>'.format(latextag_t)
#        latextag_t = '##wsq##\({}\)##wsq##'.format(latextag_t)
        html_string = html_string.replace(latextag, latextag_t)

    return html_string

