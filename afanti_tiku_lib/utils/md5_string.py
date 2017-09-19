# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import hashlib

from afanti_tiku_lib.compat import compat_str

from .get_pure_text import get_pure_text

def md5_string(string):
    if type(string) is not compat_str:
        try:
            string = string.decode('utf-8')
        except Exception:
            raise TypeError('string must be unicode')

    return hashlib.md5(string.encode('utf-8')).hexdigest()


def get_pure_text_md5(html):
    '''获取一段html的纯文本的md5'''
    text = get_pure_text(html, False, False, 'htmlparser')
    return md5_string(text)


