# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re
import sys

from afanti_tiku_lib.html.extract import (get_html_element,
                                          find_valid_elements,
                                          remove_start_tag)
from afanti_tiku_lib.html.beautify_html import remove_tag


KEY_SYMS = { '⎛', '⎡', '⎧', '{'}

re_left = re.compile('left:\s*([-\d]+)px')
re_top = re.compile('top:\s*([-\d]+)px')
re_width = re.compile('width:\s*([-\d]+)px')

DEBUG = False

def printt(*args):
    if DEBUG:
        print(*args)


def _is_in(keys, content):
    for key in keys:
        if key in content:
            return True
    return False


class ParseFormatError(Exception): pass


class Span(object):

    def __init__(self, span):
        self.span = span
        self.left = int(re_left.search(span).group(1))
        self.top = int(re_top.search(span).group(1))
        self.text = remove_tag('<span ', span)

        mod = re_width.search(span)
        if mod:
            self.width = int(mod.group(1))
        else:
            self.width = None


    def __repr__(self):
        return '<span {}>'.format(self.text)


class Node(object):

    def __init__(self, spans):
        self.node_format = None
        self.sub_nodes = []
        self.spans = spans
        self.values = list()
        self.is_str = False

        if not spans:
            self.node_format = '{}{}'
            self.is_str = True


    def __str__(self):

        if self.is_str:
            v1 = self.values
            v2 = [str(sub_node) for sub_node in self.sub_nodes]
            latex = self.node_format.format(''.join(v1), ''.join(v2))
        else:
            values = [str(sub_node) for sub_node in self.sub_nodes]
            latex = self.node_format.format(*values)

        printt(latex)
        return latex


    def parse_format(self):
        if self.is_frac():
            printt('is_frac')
            return None

        if self.is_bracket():
            printt('is_bracket', self.spans)
            return None

        if self.is_string():
            printt('is_string', self.spans)
            return None

        if self.is_sqrt():
            printt('is_sqrt')
            return None

        if self.is_equations():
            printt('is_equations')
            return None

        raise ParseFormatError('[no format]:{}'.format(self.spans))


    def is_string(self):
        first_span = self.spans[0]
        if len(self.spans) > 1:
            second_span = self.spans[1]
        else:
            second_span = None

        text = first_span.text

        if first_span.span.startswith('<img'):
            return False

        if 'line-horizon' in text:
            return False

        if text in KEY_SYMS:
            return False

        spans = self.spans[1:]
        subsups = self.find_subsups(spans, first_span)
        if subsups:
            tag, upper_spans, v3 = subsups
            if tag == 'sup':
                self.node_format = '{}^{{{}}}{}'
            elif tag == 'sub':
                self.node_format = '{}_{{{}}}{}'

            self.sub_nodes = [Node(self.spans[:1]), Node(upper_spans), Node(v3)]

            # print('&&&&&&&&&', self.spans[:1], upper_spans, v3)
            return True


        # print('second_span', second_span)
        # print('---------', first_span, second_span, first_span.top, second_span.top)
        # if second_span and not _is_in(('⎛', '⎡', '\'', '='), second_span.text):
            # if first_span.top - second_span.top >= 4:
                # upper_spans = [second_span]
                # v3 = []
                # printt('upper_spans', upper_spans)
                # for i, span in enumerate(self.spans[2:]):
                    # if first_span.top - span.top >= 4:
                        # upper_spans.append(span)
                    # else:
                        # v3 = self.spans[2:][i:]
                        # break

                # self.node_format = '{}^{{{}}}{}'
                # self.sub_nodes = [Node(self.spans[:1]), Node(upper_spans), Node(v3)]
                # print('*********', self.spans[:1], upper_spans, v3)
                # return True

        self.is_str = True
        self.node_format = '{}{}'
        self.values = [text]
        self.sub_nodes = [Node(self.spans[1:])]

        return True


    def find_subsups(self, spans, root_span):
        if not spans:
            return False

        if _is_in(('\'', '=', '-', '+', '%'), root_span.text):
            return False

        floor = root_span.top
        left = root_span.left     # for case, is_equations

        first_span = spans[0]

        #
        #
        if not _is_in(('⎛', '⎡', '\'', '='), first_span.text):
                # and not _is_in(('line-horizon',), first_span.span):

            if floor - first_span.top >= 4 and left < first_span.left:

                if _is_in(('⎛', '⎡', '[', '{'), first_span.text):
                    bracket, vz = self.find_bracket(spans)
                    if not self.is_all_supper(bracket, first_span):
                        return False

                if _is_in(('line-horizon',), first_span.span):
                    frac, vz = self.find_frac(spans)
                    if not self.is_all_supper(frac, first_span):
                        return False

                if _is_in(('<img',), first_span.span):
                    sqrt, vz = self.find_sqrt(spans)
                    if not self.is_all_supper(sqrt, first_span):
                        return False

                upper_spans = [first_span]
                v3 = []
                printt('upper_spans', upper_spans)
                for i, span in enumerate(spans[1:]):
                    if floor - span.top >= 4 and left < span.left:
                        upper_spans.append(span)
                    else:
                        v3 = spans[1:][i:]
                        break

                return 'sup', upper_spans, v3

            elif floor - first_span.top <= -7 and left < first_span.left:
                upper_spans = [first_span]
                v3 = []
                printt('upper_spans', upper_spans)
                for i, span in enumerate(spans[1:]):
                    if floor - span.top <= -7 and left < span.left:
                        upper_spans.append(span)
                    else:
                        v3 = spans[1:][i:]
                        break

                return 'sub', upper_spans, v3
            else:
                return False
        else:
            return False


    def is_frac(self):
        if not self.spans:
            return False

        first_span = self.spans[0]
        text = first_span.text

        if text.strip():
            return False

        if first_span.span.startswith('<img'):
            return False

        if 'line-horizon' not in first_span.span:
            return False

        v1 = []
        v2 = []
        v3 = []
        for i, span in enumerate(self.spans[1:]):
            if span.left - first_span.left < first_span.width:
                if span.top - first_span.top < -1:
                    v1.append(span)
                else:
                    v2.append(span)
            else:
                v3 = self.spans[1:][i:]
                break

        # print(self.spans)
        # print('v1', v1)
        # print('v2', v2)
        self.node_format = '\\frac{{{}}}{{{}}}{}'
        self.sub_nodes = [Node(v1), Node(v2), Node(v3)]

        return True


    def is_bracket(self):

        printt('[IN BRACKET]', self.spans)

        if len(self.spans) < 2:
            return False

        first_span = self.spans[0]
        text = first_span.text

        if not text:
            return False

        begin_tag = None
        end_tag = None
        if '⎛' in text:
            begin_tag = '⎛'
            end_tag = '⎠'
        elif '⎡' in text:
            begin_tag = '⎡'
            end_tag = '⎦'
        elif '{' in text:
            begin_tag = '{'
            end_tag = '}'

        if not begin_tag:
            return False

        if begin_tag == '{' and self.spans[1].text.strip() != '}':
            return False

        i = 0
        for i, span in enumerate(self.spans[1:]):
            # print('0000000000', span)
            if end_tag in span.text:
                break

        second_span = self.spans[1:][i]

        # print('.......', first_span, second_span)

        v1 = []
        v2 = []
        for ii, span in enumerate(self.spans[1:][i+1:]):
            if first_span.left <= span.left <= second_span.left:
                v1.append(span)
            else:
                v2 = self.spans[1:][i+1:][ii:]
                break

        printt('++++++++++++', v1)
        printt('------------', v2)

        if v2:
            tops = []
            for span in self.spans[1:]:
                if _is_in(('⎜', '|', '⎢', '⎪'), span.text):
                    tops.append(span.top)
                else:
                    break

            if begin_tag == '{':
                tops = [s.top for s in self.spans[:2]]

            top = sum(tops) / len(tops)
            printt('tops', tops)
            printt('top', top)

            fs_span = v2[0]
            if not _is_in(('⎛', '⎡', '\'', '=', '⎧'), fs_span.text) and top - fs_span.top >= 4:
                upper_spans = [fs_span]
                v3 = []
                for i, span in enumerate(v2[1:]):
                    if top - span.top >= 4:
                        upper_spans.append(span)
                    else:
                        v3 = v2[1:][i:]
                        break

                if begin_tag == '⎛':
                    self.node_format = '({})^{{{}}}{}'
                elif begin_tag == '⎡':
                    self.node_format = '[{}]^{{{}}}{}'
                elif begin_tag == '{':
                    self.node_format = '\\{{{}\\}}^{{{}}}{}'
                self.sub_nodes = [Node(v1), Node(upper_spans), Node(v3)]

                printt('ok------------', v3)
                return True


        if begin_tag == '⎛':
            self.node_format = '({}){}'
        elif begin_tag == '⎡':
            self.node_format = '[{}]{}'
        elif begin_tag == '{':
            self.node_format = '\\{{{}\\}}^{{{}}}'
        self.sub_nodes = [Node(v1), Node(v2)]

        return True


    def is_sqrt(self):
        first_span = self.spans[0]
        if not first_span.span.startswith('<img'):
            return False

        second_span = self.spans[1]
        if 'line-horizon' not in second_span.span:
            return False

        left = second_span.left
        width = second_span.width

        v1 = []
        v2 = []
        for i, span in enumerate(self.spans[2:]):
            if span.left - left < width:
                v1.append(span)
            else:
                v2 = self.spans[2:][i:]
                break

        self.node_format = '\\sqrt{{{}}}{}'
        self.sub_nodes = [Node(v1), Node(v2)]

        return True


    def is_equations(self):
        first_span = self.spans[0]
        text = first_span.text

        if '⎧' not in text:
            return False

        spans = self.spans[:]

        for i, span in enumerate(spans[1:]):
            if '⎩' in span.text:
                spans = spans[1:][i+1:]
                break

        #
        # split equations
        # {{
        vz = []
        _spans = []
        # print('spans', spans)
        for i, span in enumerate(spans):
            if i > 0:
                pre_span = spans[i-1]
            else:
                pre_span = spans[i]

            if span.left - pre_span.left > 0 and span.top - pre_span.top <= -15 and not _is_in(('line-horizon',), pre_span.span):
                _spans = spans[:i]
                vz = spans[i:]
                spans = _spans
                break
        # }}

        # print('vz', vz)

        #
        # split rows
        rows = []
        span_list = []
        p = 0
        for i, span in enumerate(spans):
            if p > i:
                continue

            # if span.left == 447:
                # print('vvvvvvvv', span_list, span, i)
                # print(rows)
                # print(spans)

            # print('====', i, span)

            if not _is_in(('⎛', '⎡', '<img', 'line-horizon'), span.span):
                if not span_list:
                    span_list.append(span)
                else:
                    pre_span = span_list[-1]
                    # if span.left == 447:
                        # print('bbbbbbbb', pre_span, span)
                    if pre_span.left >= span.left:
                        rows.append(list(span_list))
                        # span_list = [span]
                        span_list = []
                    span_list.append(span)
            else:
                # find type
                while True:
                    self.spans = spans[i:]
                    if self.is_bracket():
                        # print('is_bracket')
                        break

                    self.spans = spans[i:]
                    if self.is_sqrt():
                        # print('is_sqrt')
                        self.spans = spans[i:]
                        break

                    self.spans = spans[i:]
                    if self.is_frac():
                        # print('is_frac')
                        break

                    raise ParseFormatError('[is_equations] can not find not char')

                _span = None       # first span of last Node at bracket, sqrt, frac
                if self.sub_nodes[-1].spans:
                    _span = self.sub_nodes[-1].spans[0]

                #
                # find all spans of the bracket, sqrt, frac except last Node's
                # spans inside of it
                ii = 0
                _elem_list = []   # contain spans that are in the bracket, sqrt, frac

                if _span:
                    for ii, s in enumerate(spans[i:]):
                        if s.span == _span.span:
                            break
                        _elem_list.append(s)
                else:
                    _elem_list = spans[i:]
                    ii = len(spans)

                #
                # add spans to span_list
                if not span_list:
                    span_list += _elem_list
                else:
                    pre_span = span_list[-1]
                    if pre_span.left >= _elem_list[0].left:
                        rows.append(list(span_list))
                        span_list = []

                    span_list += _elem_list

                p = i + ii

        rows.append(span_list)

        cols = ' \\\\ '.join(['{}'] * len(rows))
        self.node_format = (r'\begin{{cases}} '
                            + cols
                            + r' \end{{cases}}') + '{}'

        # print('rows', rows)
        # print(vz)
        # sys.exit()
        self.sub_nodes = [Node(row) for row in rows] + [Node(vz)]
        return True


    def find_bracket(self, spans):
        if len(spans) < 2:
            return [], spans

        head_span = spans[0]

        begin_tag = None
        end_tag = None
        if '⎛' in head_span.text:
            begin_tag = '⎛'
            end_tag = '⎠'
        elif '⎡' in head_span.text:
            begin_tag = '⎡'
            end_tag = '⎦'
        elif '{' in head_span.text:
            begin_tag = '{'
            end_tag = '}'
        else:
            return [], spans

        if begin_tag == '{' and spans[1].text.strip() != '}':
            return [], spans


        i = 0
        for i, span in enumerate(spans[1:]):
            if end_tag in span.text:
                break

        tail_span = spans[1:][i]

        v1 = []
        v2 = []
        for ii, span in enumerate(spans[1:][i+1:]):
            if head_span.left <= span.left <= tail_span.left:
                v1.append(span)
            else:
                v2 = spans[1:][i+1:][ii:]
                break

        return v1, v2


def parse(node):
    if node.node_format is None:
        node.parse_format()

    for sub_node in node.sub_nodes:
        parse(sub_node)


def to_latex(html_string, raw=False):
    xb_math_span_list = get_html_element('<span [^<>]*?math-model',
                                         html_string,
                                         regex = True,
                                         with_tag=True,
                                         flags=re.I)

    for xb_math_span_ori in xb_math_span_list:
        xb_math_span = remove_start_tag(xb_math_span_ori)

        spans = get_spans(xb_math_span)
        root_node = Node(spans)
        parse(root_node)

        latex = str(root_node)

        if raw is False:
            latex_span = '<span class="afanti-latex">\( {} \)</span>'.format(latex)
            html_string = html_string.replace(xb_math_span_ori, latex_span)
        else:
            html_string = html_string.replace(xb_math_span_ori, '\( {} \)'.format(latex))

    return html_string



def get_spans(html_string):
    imgs = get_html_element('<img ', html_string, only_tag=True)
    for img in imgs:
        html_string = html_string.replace(img, img + '</img>')

    rs = []
    spans = find_valid_elements(html_string, '<(span|img) ', with_tag=True, regex=True)
    for span in spans:
        rs.append(Span(span))

    # format_spans(rs)
    return rs


def format_spans():
    pass
