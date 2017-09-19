# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import logging
import re

from afanti_tiku_lib.html.extract import find_valid_elements, remove_start_tag


def remove_extra_info(text):
    pattern = re.compile(r'\(20\d{2}.*?\)', re.I|re.S)
    item = re.match(pattern, text)
    if item:
        return text.replace(item.group(0), '') 
        
    return text


if __name__=='__main__':
    pass
