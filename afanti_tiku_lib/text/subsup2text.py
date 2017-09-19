# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import logging
import re

from afanti_tiku_lib.html.extract import find_valid_elements, remove_start_tag


def subsup_to_text(html_string):
    """
    convert sub/sup to text"

    """
    pattern = re.compile(r'<sup>\s*(?P<mi>.*?)\s*</sup>', re.S|re.I)
    html_string = re.sub(pattern,r' \g<mi> ',html_string)

    pattern = re.compile(r'<sub>\s*(?P<mi>.*?)\s*</sub>', re.S|re.I)
    html_string = re.sub(pattern,r'\g<mi>',html_string)

    return html_string


if __name__=='__main__':
    html_string = "2L 0.2mol•L<SUP>-1</SUP>的Ba（NO<SUB>3</SUB>）"
    print(subsup_to_text(html_string))
    html_string = """<br><p></p>  <p>数列<sub><img width="31" height="24" src="https://qimg.afanti100.com/data/image/question_image/23/50bab9630e054530916265efc6eb6967.png"></sub>满足：　<sub><img width="269" height="69" src="https://qimg.afanti100.com/data/image/question_image/23/00ab2c3ee4c9f5916ae45e36cce971bb.png"></sub></p>"""

    print(subsup_to_text(html_string))
