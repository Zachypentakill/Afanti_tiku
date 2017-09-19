# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re

from afanti_tiku_lib.html.extract import get_html_element, find_valid_elements
from afanti_tiku_lib.html.beautify_html import remove_tag
from afanti_tiku_lib.compat import compat_urllib_parse


_re_displaystyle_target = re.compile(r'(\\[cdt]{,1}frac|\\sum|\\int|\\prod|\\binom|∫|∑|∏)')
_re_frac = re.compile(r'\\[cdt]{,1}frac')


def latex_clear(tex):
    if not tex:
        return ''

    tex = tex.replace('\\underline{}', '\t'*5)
    return tex


def fix_latex_underline(tex):
    tex = re.sub(r'\t{5,}', '\\underline{\\qquad}', tex)
    return tex


def fix_underline(tex):
    tex = re.sub(r'\t{5,}', '<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>', tex)
    return tex


def is_latex(tex):
    if not tex:
        False

    if re.search(r'[{_\\^]', tex):
        return True
    else:
        return False


def fix_latex_table(tex):
    if not tex:
        return tex

    mod = re.search(r'\\begin\{array\}\{.+?\}', tex)
    if not mod:
        return tex

    front = mod.group(0)
    ltt = tex.replace(r'\hline', '')
    first_row = ltt.split(r'\\', 1)[0]
    column_size = len([True for c in first_row if c == '&']) + 1
    tex = tex.replace(front, r'\begin{array}{|%s|}' % '|'.join(['c']*column_size))
    return tex


def latex_excape(tex):
    tex = compat_urllib_parse.unquote(tex)
    tex = tex.replace('{', '\{')\
             .replace('}', '\}')
    return tex


class FindLatexError(Exception): pass


def find_latexes(html_string, with_delimiter=True):
    html_string = html_string.replace('\\$', '<latex_TT_latex/>')

    texes = list()
    N = len(html_string)
    b = 0
    p = 0
    tag = ''

    while p < N - 1:
        if '$' in html_string[p:p+2]:
            if not tag:
                tag = '$'
                if html_string[p] == '$':
                    b = p + 1
                else:
                    b = p + 2
                    p += 1
            else:
                if tag != '$':
                    raise FindLatexError('conflict "$", {}'.format(html_string))
                else:
                    if html_string[p] != '$':
                        p += 1

                    tex = html_string[b:p]
                    if with_delimiter is False:
                        texes.append(tex)
                    else:
                        texes.append('${}$'.format(tex))
                    tag = ''

        elif r'\(' == html_string[p:p+2]:
            if tag:
                raise FindLatexError('conflict "\(", {}'.format(html_string))
            else:
                tag = r'\('
                b = p + 2
                p += 1

        elif r'\)' == html_string[p:p+2]:
            if tag != r'\(':
                raise FindLatexError('conflict "\)", {}'.format(html_string))
            else:
                tex = html_string[b:p]
                if with_delimiter is False:
                    texes.append(tex)
                else:
                    texes.append('\({}\)'.format(tex))
                tag = ''
                p += 1

        elif r'\[' == html_string[p:p+2]:
            if tag:
                raise FindLatexError('conflict "\[", {}'.format(html_string))
            else:
                tag = r'\['
                b = p + 2
                p += 1

        elif r'\]' == html_string[p:p+2]:
            if tag != r'\[':
                raise FindLatexError('conflict "\]", {}'.format(html_string))
            else:
                tex = html_string[b:p]
                if with_delimiter is False:
                    texes.append(tex)
                else:
                    texes.append('\[{}\]'.format(tex))
                tag = ''
                p += 1

        p += 1

    texes = [t.replace('<latex_TT_latex/>', '\$') for t in texes]
    return texes


def unify_tag(html_string):
    try:
        for latex in find_latexes(html_string):
            unify_latex = '\\(' + latex[1:-1] + '\\)'
            html_string = html_string.replace(latex, unify_latex)
    except FindLatexError:
           pass
    else:
           pass
    return html_string

def unify_tag_for_show(html_string):
    try:
        for latex in find_latexes(html_string):
            unify_latex = '<span class="afanti-latex">' + '\\( ' + latex[1:-1] + ' \\)' + '</span>'
            html_string = html_string.replace(latex, unify_latex)
    except FindLatexError:
           pass
    else:
           pass
    return html_string


def find_mathml_elems(html_string, with_tag=True):
    maths = get_html_element('<(mfrac|msubsup|munder)', html_string,
                             with_tag=with_tag, regex=True, flags=re.I)
    return maths


def find_latex_subsups(tex):
    """
    find "_{}" or "^{}"
    """

    if not tex:
        return tex

    subsups = list()
    b = 0
    p = 0
    stack = list()
    while p < len(tex):
        if not stack:
            if tex[p:p+2] in ('_{', '^{'):
                b = p
                stack.append('{')
                p += 3
            else:
                p += 1
            continue
        else:
            if tex[p] == '{':
                if tex[p-1] != '\\':
                    stack.append('{')
                p += 1
                continue
            elif tex[p] == '}':
                if tex[p-1] != '\\':
                    stack.pop()
                    p += 1
                    if not stack:
                        ss = tex[b:p]
                        subsups.append(ss)
                else:
                    p += 1
                continue
            else:
                p += 1
                continue
    return subsups


DISPLAYSTYLE = r'\displaystyle '


def _displaystyle(tex):
    """
    add \displaystyle at global
    """

    tex = _re_frac.sub(DISPLAYSTYLE + r'\\frac', tex)
    tex = tex.replace('\\binom', DISPLAYSTYLE + '\\binom')\
             .replace('\\sum', DISPLAYSTYLE + '\\sum')\
             .replace('\\int', DISPLAYSTYLE + '\\int')\
             .replace('\\prod', DISPLAYSTYLE + '\\prod')\
             .replace('∫', DISPLAYSTYLE + '\\int ')\
             .replace('∑', DISPLAYSTYLE + '\\sum ')\
             .replace('∏', DISPLAYSTYLE + '\\prod ')

    return tex


def _discard_latex_displaystyle_for_subsup(tex):
    """
    # fractions that are in sub/sup are not needed to display

    remove displaystyle in which "_{}" or "^{}"
    """

    subsups = find_latex_subsups(tex)
    for subsup in subsups:
        subsup_t = subsup.replace(DISPLAYSTYLE, '')
        if subsup != subsup_t:
            tex = tex.replace(subsup, subsup_t, 1)
    return tex


def _discard_mathml_displaystyle_for_subsup(mathml):
    """
    # fractions that are in sub/sup are not needed to display

    remove displaystyle in which of sub/sup
    """

    subsups = find_valid_elements(mathml, '<msu(b|p)',
                                  regex=True, with_tag=False)
    subsups = list(set(subsups))
    subsups = sort_by_len(subsups, reverse=True)
    for subsup in subsups:
        subsup_t = remove_tag('<mstyle displaystyle', subsup, all=False)
        mathml = mathml.replace(subsup, subsup_t, 1)
    return mathml


def displaystyle(html_string, latex_tag=None, regex=False,
                 flags=re.U, latex=True, mml=True):
    """
    give displaystyle at right places
    """

    if latex is True:
        texes = list()
        if latex_tag:
            texes = get_html_element(latex_tag, html_string,
                                    regex=regex, flags=flags)
        else:
            if _re_displaystyle_target.search(html_string):
                texes = find_latexes(html_string)

        for tex in set(texes):
            tex_t = _displaystyle(tex)
            tex_t = _discard_latex_displaystyle_for_subsup(tex_t)
            html_string = html_string.replace(tex, tex_t)

    if mml is True and '<math' in html_string.lower():
        mathmls = find_mathml_elems(html_string, with_tag=True)
        mathmls = list(set(mathmls))
        mathmls = sort_by_len(mathmls, reverse=True)

        for mathml in mathmls:
            html_string = html_string.replace(
                mathml, ('<mstyle displaystyle="true">{}</mstyle>').format(mathml))
        html_string = _discard_mathml_displaystyle_for_subsup(html_string)

    return html_string


def sort_by_len(ls, reverse=False):
    """
    sort [str1, str2, str3, ..., strn] by their lenght
    """

    d = {k: len(k) for k in ls}
    ls_t = sorted(ls, key=lambda x: d[x], reverse=reverse)
    return ls_t
