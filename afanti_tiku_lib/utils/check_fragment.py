# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re
from afanti_tiku_lib.utils.get_pure_text import get_pure_text


IMG_PATTERN = re.compile(r'<img\s[^<>]*?src', flags=re.I)
BACKGROUND_IMG_PATTERN = re.compile(
    r"""background(?:-image|):\s*?url[(\s'"\\]+([^'"()\s\\]+)""", flags=re.I)
ENGLISH_SYMBOL_PATTERN = re.compile(r"""[\[\]:;.,?%&!_\-()\\'"\/\{\}]""")
CHINESE_SYMBOL_PATTERN = re.compile(r'[。，？！…—：‘’“”、…·﹕〈〉《》｛｝【】╚╗└┐]')
BLANK_PATTERN = re.compile(r'\s', flags=re.U)


def has_html_img(html):
    '''
    判断html中是否有图片信息
    '''

    # 判断有无常规的图片标签
    mod1 = IMG_PATTERN.search(html)

    # 判断在background属性中的图片
    mod2 = BACKGROUND_IMG_PATTERN.search(html)

    if mod1 or mod2:
        return True
    else:
        return False


def check_html_valid(html):
    pure_text = get_pure_text(
                    html,
                    parser='htmlparser',
                    del_stopwords_flag=False,
                    filter_symbol_flag=False)

    has_img_flag = has_html_img(html)

    pure_text = BLANK_PATTERN.sub('', pure_text)
    pure_text = ENGLISH_SYMBOL_PATTERN.sub('', pure_text)
    pure_text = CHINESE_SYMBOL_PATTERN.sub('', pure_text)
    pure_text = pure_text.replace('略', '')\
                         .replace('nbsp', '')
    pure_text = pure_text.strip()

    if pure_text == '':
        if has_img_flag:
            return True
        else:
            return False
    else:
        return True
