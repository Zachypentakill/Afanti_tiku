# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from afanti_tiku_lib.html.extract import get_html_element, remove_start_tag
from afanti_tiku_lib.compat import compat_str

import re

import bs4


def beautify_html(html_string):
    '''
    慎重使用


    '''


    # html_string = ''.join([i.strip() + ' ' for i in StringIO(html_string).readlines()])
    # html_string = get_html_element('<body', html_string)[0]
    html_string = html_string.strip()

    # remove style tag
    html_string = remove_style_tag(html_string)

    # remove comment
    html_string = re.sub(r'<![^<>]+>', '', html_string)

    # remove '\x1f'
    # html_string = re.sub(r'(\d)\x1f(\d)', r'\1\2', html_string)

    # remove h1,
    html_string = re.sub(r'<(/|)(h\d*|strong|font|em|[\w]+:[\w]+|xml)[^<>]*>',
                         '', html_string, flags=re.I)

    # remove b
    html_string = remove_tag('<b>', html_string, flags=re.I)

    # remove a
    html_string = remove_a_tag(html_string)

    # fix super and sub tag
    tags = get_html_element('<span [^<>]+[^\w<>](super|sub|underline)[^\w<>]',
                            html_string, regex=True, flags=re.I)
    for tag in tags:
        if 'super' in tag.lower():
            text = re.sub(r'<span [^<>]+>', '<sup>', tag, flags=re.I)[:-7] + '</sup>'
        elif 'underline' in tag.lower():
            text = re.sub(r'<span [^<>]+>', '<u>', tag, flags=re.I)[:-7] + '</u>'
        else:
            text = re.sub(r'<span [^<>]+>', '<sub>', tag, flags=re.I)[:-7] + '</sub>'
        html_string = html_string.replace(tag, text, 1)

    # clear table
    # tables = get_html_element('<table', html_string)
    # for table in tables:
        # if 'border-bottom:' in table:
            # continue
        # t = re.sub(r'<table[^<>]*>', '<table style="border: 1px solid black; border-collapse: collapse;">', table, flags=re.I)
        # t = re.sub(r'<tr[^<>]*>', '<tr>', t, flags=re.I)
        # t = re.sub(r'<td[^<>]*>', '<td style="border: 1px solid black; border-collapse: collapse;">', t, flags=re.I)
        # t = re.sub(r'<th[^<>]*>', '<th style="border: 1px solid black; border-collapse: collapse;">', t, flags=re.I)
        # html_string = html_string.replace(table, t, 1)

    # remove verbose span
    # while True:
        # spans = get_html_element('<span (?:tyle\s*=[^<>]+?font-family)', html_string, regex=True)
        # if not spans:
            # break
        # for span in spans:
            # sub_span = re.sub(r'^<span[^<>]*>', '', span, flags=re.I)[:-7]
            # html_string = html_string.replace(span, sub_span, 1)

    html_string = remove_tag('<span (?:style\s*=[^<>]+?font-family)',
                             html_string, regex=True, flags=re.I)

    html_string = center_image(html_string)

    # DO NOT remove p, div style
    # html_string = re.sub(r'<(p|div|br) [^<>]+>', r'<\1>', html_string, flags=re.I)

    # remove word spercial tag
    # dirty_elems = get_html_element('<([\w]+:[\w]+|xml)', html_string, regex=True)
    # for elem in dirty_elems:
        # html_string = html_string.replace(elem, '', 1)


    # remove empty elements
    # html_string = re.sub(r'\s*<(\w+)>(&nbsp;|\s|　|)*</\1>\s*', ' ', html_string)
    html_string = remove_empty_elements(html_string)

    # remove more &nbsp;
    html_string = limit_nbsp(html_string)

    # replace (  )
    # html_string = html_string.replace('）', ')').replace('（', '(')

    # remove unclosed tags
    # html_string = remove_unclosed_tags(html_string)
    return html_string


re_tag = re.compile('<(/|)[a-zA-Z][a-zA-Z0-9:]*[^<>]*>')
re_empty_str = re.compile(r'(\s|　|\xa0|&#xa0;|&nbsp;)*')
def remove_empty_elements(html_string, filter=None):
    #
    # filter is function return True or False,
    # True, then remove the elem,
    # False, then remain it
    #
    def _filter(elem):
        elem = elem.lower()
        if 'aft_' in elem \
                or 'afanti_' in elem \
                or '<u>' in elem \
                or '<img ' in elem:
            return False
        else:
            return True

    _filter = _filter or filter
    elems = get_html_element('<([a-zA-Z][a-zA-Z0-9:]*)', html_string, regex=True)
    elems = list(set(elems))
    elems = sorted(elems, key=lambda x: len(x), reverse=True)
    for elem in elems:
        elem_text = re_tag.sub('', elem)
        elem_text = re_empty_str.sub('', elem_text)
        if not elem_text:
            if _filter and not _filter(elem):
                continue
            html_string = html_string.replace(elem, '')

    return html_string.strip()


re_nbsp = re.compile(r'(\s*&nbsp;\s*){6,}', flags=re.I)
def limit_nbsp(html_string):
    html_string = re_nbsp.sub('&nbsp;' * 6, html_string)
    return html_string


def center_image(html_string):
    imgs = get_html_element('<img', html_string, only_tag=True, flags=re.I)
    for img in imgs:
        try:
            src = re.search(r"""src\s*=\s*["'][^"'<>]+?["']""", img, flags=re.I).group()
        except Exception:
            continue

        w = ''
        mod = re.search(r'\W(width\s*(:|=)\s*[^<>]+?)(;|\s|/|>)', img, flags=re.I)
        if mod:
            w = mod.group(1)
            w = re.sub(r'\s*:\s*', '=', w, 1)
            if '"' not in w and '\'' not in w:
                w = w.replace('=', '="', 1) + '"'

        h = ''
        mod = re.search(r'\W(height\s*(:|=)\s*[^<>]+?)(;|\s|/|>)', img, flags=re.I)
        if mod:
            h = mod.group(1)
            h = re.sub(r'\s*:\s*', '=', h, 1)
            if '"' not in h and '\'' not in h:
                h = h.replace('=', '="', 1) + '"'

        style = ' '.join((src, w, h)).strip()
        new_img = '<img %s style="vertical-align: middle;">' % style
        html_string = html_string.replace(img, new_img)

    return html_string


def remove_element(tag, html_string, regex=False,
                   flags=re.U, check=None):
    return remove_tag(tag, html_string, regex=regex,
                      flags=flags, all=True, check=check)


def remove_tag(tag, html_string, regex=False, flags=re.U,
               all=False, check=None):
    '''
    if all is True, remove matched elements including it's text
    '''

    if regex is False:
        if tag.lower() not in html_string.lower():
            return html_string
    else:
        if re.search(tag, html_string, flags=flags) is None:
            return html_string

    es = get_html_element(tag, html_string, regex=regex, flags=flags)
    for e in es:
        if check is not None and check(e) is False:
            continue

        if all:
            content = ''
        else:
            content = re.sub(r'^<[^<>]+>', '', e)
            content = re.sub(r'</[^<>]+>$', '', content)

            # sindex = e.find('>') + 1
            # eindex = e.rfind('<')
            # content = e[sindex:eindex]

        html_string = html_string.replace(e, content)
    return html_string


def remove_style_tag(html_string):
    if '<style' not in html_string.lower():
        return html_string
    else:
        return remove_tag('<style', html_string, flags=re.I)


def remove_span_tag(html_string):
    if '<span' not in html_string.lower():
        return html_string
    else:
        return remove_tag('<span', html_string, flags=re.I)


def remove_a_tag(html_string, all=False):
    def check(elem):
        if 'href' in elem.lower():
            return True
        else:
            return False

    if '<a ' not in html_string.lower():
        return html_string
    else:
        return remove_tag('<a ', html_string, flags=re.I, check=check, all=all)


re_start_br = re.compile(r'^(\s|&nbsp;|<br[\s/]*>)', flags=re.I)
re_end_br = re.compile(r'(\s|&nbsp;|<br[\s/]*>)$', flags=re.I)
def remove_start_end_br(html_string):
    if not html_string.strip():
        return ''

    html_string = re_start_br.sub('', html_string)
    html_string = re_end_br.sub('', html_string)
    return html_string


def remove_bgcolor_attribute_complicated(html_string):
    '''
    删除html片段中的标签的style属性中的bgcolor与background-color信息
    利用bs遍历所有标签，如果标签有style属性，并且属性中有bgcolor等信息，删除该信息
    '''
    if not html_string:
        return ''
    soup = bs4.BeautifulSoup(html_string, 'lxml')
    for tag in soup.descendants:
        if isinstance(tag, bs4.element.Tag):
            if tag.attrs:
                style = tag.attrs.get('style')
                if not style:
                    continue
                for key in ['bgcolor', 'background-color']:
                    if key in style.lower():
                        pattern = re.compile('%s\s*?:\s*?[^;]+(?=;)'%key, flags=re.U|re.I)
                        style = pattern.sub('', style)
                        tag.attrs['style'] = style
    if '<body>' in html_string:
        html_string = compat_str(soup)
    else:
        html_string = compat_str(soup.body).replace('<body>', '').replace('</body>', '')
    return html_string


def remove_bgcolor_attribute(html_string):
    '''
    删除html片段中的标签的style属性中的bgcolor与background-color信息
    利用正则表达式匹配标签，替换掉style属性中的bgcolor信息与background-color信息
    '''
    pattern = re.compile(r'''(\<[a-z]\w*?\s+?style=['"][^<>"']*?)'\
            '(;?(?:bgcolor|background_color):[^<>'"]+)(?=[;'"])''', flags=re.U|re.I)
    def sub_func(match):
        return match.group(1)
    x = pattern.sub(sub_func, html_string)
    return x

