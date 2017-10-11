# -*- coding: utf-8 -*-

import os
import json
import re

from afanti_tiku_lib.html.extract import get_html_element
from afanti_tiku_lib.html.beautify_html import remove_tag


_DIR = os.path.dirname(os.path.abspath(__file__))
COMPRESSED_CLASS_PATH = _DIR + '/compressed_class.json'


class ParserError(Exception): pass

class Parser(object):

    def __init__(self, compress_class_path = COMPRESSED_CLASS_PATH):
        compress_class_path = (compress_class_path or COMPRESSED_CLASS_PATH)
        self.compress_class_json = json.load(open(compress_class_path))


    def get_render_html(self, raw_render_html):
        elem = get_html_element('<div id="-mathjax-render-div-">',
                                raw_render_html,
                                with_tag=False,
                                limit=1)
        if not elem:
            raise ParserError('Cant\'t find <div id="-mathjax-render-div-">')

        elem = self.remove_some_elem(elem[0])

        return elem.strip()


    def remove_some_elem(self, elem):
        elem = elem.replace('<span class="MathJax_Preview"></span>', '')\
                   .replace(' style=""', '')\
                   .replace('MJXc-processed', '')
        elem = remove_tag('<script ', elem, all=True)
        elem = remove_tag('<span class="MathJax_Preview">', elem, all=True)
        elem = re.sub(r' id=".+?"', '', elem)
        elem = self.compress_class(elem)
        return elem


    def compress_class(self, elem):
        for item in self.compress_class_json:
            mjx_cls, comp_cls = item
            elem = elem.replace(mjx_cls, comp_cls)
        return elem
