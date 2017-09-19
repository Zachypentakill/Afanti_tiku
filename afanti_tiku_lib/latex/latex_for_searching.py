# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from afanti_tiku_lib.latex.latex2text import to_text

import re

def latex_for_searching(html_string):
    """格式化latex"""
    html_string = html_string.replace('\\% ', '%')\
                             .replace('\\, ', ' ')\
                             .replace('\\  ', ' ')\
                             .replace('\\; ', ' ')\
                             .replace('\\, ', ' ')\
                             .replace('\\! ', '')\
                             .replace('\\vec{', '{')\
                             .replace('\\overleftarrow', '')\
                             .replace('\\overleftarrow{', '{')\
                             .replace('\\overrightarrow', '')\
                             .replace('\\overrightarrow{', '{')\
                             .replace('\\widehat', '')\
                             .replace('\\widehat{', '{')\
                             .replace('\\overline ', '')\
                             .replace('\\overline{', '{')\
                             .replace('\\underline', '')\
                             .replace('\\underline{', '{')\
                             .replace('\\overbrace', '')\
                             .replace('\\overbrace{', '{')\
                             .replace('\\underbrace', '')\
                             .replace('\\underbrace{', '{')\
                             .replace('\\\\', ' ')\
                             .replace('\\{', '')\
                             .replace('\\}', '')

    html_string = re.sub(r'\\[a-z]+', to_text, html_string, flags=re.I)

    html_string = re.sub(r'\\(t|c|d|)frac\s*\{', '\\^frac{', html_string)

    html_string = re.sub(r'\\sqrt\s*\{', '\\^sqrt{', html_string)
    html_string = re.sub(r'\\sqrt\s*\[', '\\^sqrt[', html_string)

    html_string = re.sub(r'\\begin\s*\{array\}(\{.+?\}|)', '', html_string)
    html_string = re.sub(r'\\begin\s*\{.+?\}', '', html_string)
    html_string = re.sub(r'\\end\s*\{.+?\}', '', html_string)

    html_string = re.sub(r'\\[a-z]+\s*', ' ', html_string, flags=re.I)
    html_string = re.sub(r'\\[a-z]+\s*{', '{', html_string, flags=re.I)

    html_string = html_string.replace('\\^frac{', '\\frac{')\
                             .replace('\\^sqrt{', '\\sqrt{')\
                             .replace('\\^sqrt[', '\\sqrt[')

    return html_string

