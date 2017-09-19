# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re

from afanti_tiku_lib.html.extract import (get_html_element,
                                          find_valid_elements,
                                          remove_start_tag)
from afanti_tiku_lib.latex.util import latex_excape
from afanti_tiku_lib.html.beautify_html import remove_tag


# old_img_url = 'http://img.jyeoo.net/images/part/8730D.png'


class ParseFormatError(Exception): pass


def _is_in(keys, content):
    for key in keys:
        if key in content:
            return True
    return False


def _which_in(keys, content):
    for key in keys:
        if key in content:
            return key
    return None


re_x_format = re.compile(r'^(\\x[a-z]+)\[\s*\]\{')


class Node(object):

    def __init__(self):
        self.html_string = None
        self.node_format = None
        self.value_strs = list()
        self.values = list()
        self.is_str = False
        self.md5 = False      # check url md5


    def __str__(self):

        if self.is_str:
            latex = self.html_string
        else:
            values = [''.join([str(node) for node in value]) for value in self.values]
            # try:
                # t = self.node_format.format(*values)
            # except:
                # print('html_string:', self.html_string)
                # print('values:', values)
                # raise TypeError()
            # return t

            self.correct_format(values)
            latex = self.node_format.format(*values)

        latex = self.fix_any(latex)
        # return self.no_table_format(latex)
        return latex


    def correct_format(self, values):

        #
        # for case, http://www.jyeoo.com/bio/ques/detail/2032b033-643c-4eaa-9ef2-2738f522519c
        #
        if self.node_format.startswith('\\stackrel'):
            v0 = values[0]
            v1 = values[1]
            if v0.startswith('\\x'):
                self.node_format = '{}{}'
                if v1:
                    if re_x_format.search(v0):
                        ev0 = re_x_format.sub(r'\1[{}]{{'.format(v1), v0, 1)
                    else:
                        ev0 = v0.replace('{', '[{}]{{'.format(v1), 1)
                    values[0] = ev0
                    values[1] = ''
                else:
                    values[0] = v0
                    values[0] = ''


    def parse_format(self):
        if self.is_str:
            raise TypeError('node is a str')

        if not self.html_string[:10].lower().startswith('<table'):
            raise TypeError('is_not_table:\n{}'.format(self.html_string))

        if self.is_frac():
            return None

        if self.is_sqrt():
            return None

        if self.is_sqrt_n():
            return None

        if self.is_equations():
            return None

        # if self.is_integral():
        if self.is_subsup():
            return None

        if self.is_subsup2():
            return None

        if self.is_lim():
            return None

        if self.is_overrightarrow():
            return None

        if self.is_overparen():
            return None

        if self.is_sum():
            return None

        if self.is_stackrel():
            return None

        if self.is_underset():
            return None

        if self.is_xrightarrow():
            return None

        if self.is_matrix():
            return None

        if self.is_integral():
            return None

        if self.is_underbrace():
            return None

        if self.is_align():
            return None

        raise ParseFormatError('[no format]:{}'.format(self.html_string))

    def get_values(self):
        for value_str in self.value_strs:
            sub_nodes = self.get_sub_nodes(value_str)
            self.values.append(sub_nodes)


    def get_sub_nodes(self, value_str):
        sub_nodes = list()

        elems = find_valid_elements(value_str, '<table', flags=re.I)
        begin = 0
        for elem in elems:
            index = value_str.find(elem, begin)
            html_elem = value_str[begin:index]
            if html_elem.strip():
                sub_node = Node()
                sub_node.md5 = self.md5
                sub_node.html_string = latex_excape(html_elem)
                sub_node.is_str = True
                sub_node.node_format = '{}'
                sub_nodes.append(sub_node)

            begin = index + len(elem)

            sub_node = Node()
            sub_node.md5 = self.md5
            sub_node.html_string = elem
            sub_nodes.append(sub_node)

        html_elem = value_str[begin:]
        if html_elem.strip():
            sub_node = Node()
            sub_node.md5 = self.md5
            sub_node.html_string = latex_excape(html_elem)
            sub_node.is_str = True
            sub_node.node_format = '{}'
            sub_nodes.append(sub_node)

        return sub_nodes


    def is_frac(self):
        # or is_overline

        trs = find_valid_elements(self.html_string, '<tr>', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(self.html_string, '<td', flags=re.I)

        if len(tds) != 2:
            return False

        index = tds[0].find('>') + 1
        if 'border-bottom' in tds[0][:index]:

            # is_xlongequal
            # {{
            td = remove_start_tag(tds[0])
            if td.startswith('<table '):
                tables = find_valid_elements(td, '<table ', flags=re.I)
                if len(tables) == 1:
                    tds_t = find_valid_elements(tables[0], '<td', flags=re.I)
                    if len(tds_t) == 2:
                        if tds_t[1] == '<td style="font-size: 90%"><div style="border-top:1px solid black;line-height:1px">.</div></td>' \
                                or tds_t[1] == '<td style="font-size:90%"><div style="border-top:1px solid black;line-height:1px">.</div></td>':
                            td = remove_start_tag(tds_t[0])
                            td2 = remove_start_tag(tds[1])
                            self.node_format = '\\xlongequal[{}]{{{}}}'
                            self.value_strs = [td2, td]
                            return True
            # }}

            self.node_format = r'\frac{{{}}}{{{}}}'
            tds = [remove_start_tag(td) for td in tds]

            self.value_strs = tds
            return True

        if '<table' not in tds[0]:

            # is_overline
            # {{
            if 'border-top' in tds[0]:
                self.node_format = r'\overline{{{}}}'
                tds = [remove_start_tag(td) for td in tds]
                self.value_strs = tds[1:]
                return True
            # }}

            # is_sub if not is_underbrace
            # {{
            index = tds[1].find('>') + 1
            td1 = remove_start_tag(tds[1])
            _keys1 = ['8cd1f5182b8ab176140b3249472323ac',
                    '99129c72930ac651065df803ef39d322']
            _keys2 = ['/part/H123U.png']
            if not _is_in(_keys1 + _keys2, td1):
                if 'style="font-size:90%"' in tds[1][:index]:
                    td0 = remove_start_tag(tds[0])
                    self.node_format = r'{}_{{{}}}'
                    self.value_strs = [td0, td1]
                    return True
            # }}

        # is_underbrace
        # {{
        # case http://www.jyeoo.com/math/ques/detail/2fe3a71c-3616-441f-aa05-30f90f58310b
        td0 = remove_start_tag(tds[0])
        if self.is_underbrace(html_string=td0):
            if tds[1].startswith('<td style="font-size:90%">'):
                td1 = remove_start_tag(tds[1])
                self.node_format = '{}_{{{}}}'
                self.value_strs = [td0, td1]
                return True
        # }}

        # is_xlongequal 2
        # {{
        if td0.startswith('<table ') and self.is_xlongequal2(html_string=td0):
            if tds[1] == '<td style="font-size: 90%"><div style="border-top:1px solid black;line-height:1px">.</div></td>' \
                or tds[1] == '<td style="font-size:90%"><div style="border-top:1px solid black;line-height:1px">.</div></td>':
                return True
            else:
                self.node_format = None
                self.value_strs = []
        # }}

        return False


    def is_underbrace(self, html_string=None):
        html_string = html_string or self.html_string

        trs = find_valid_elements(html_string, '<tr>', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(html_string, '<td', flags=re.I)

        if len(tds) != 2:
            return False

        _keys1 = ['8cd1f5182b8ab176140b3249472323ac',
                  '99129c72930ac651065df803ef39d322']
        _keys2 = ['/part/H123U.png']
        if self.md5 is True:
            if not _is_in(_keys1 + _keys2, tds[1]):
                return False
        else:
            if not _is_in(_keys2 + _keys1, tds[1]):
                return False

        td = remove_start_tag(tds[0])
        self.node_format = '\\underbrace{{{}}}'
        self.value_strs = [td]
        return True


    def is_xlongequal2(self, html_string=None):
        # case http://www.jyeoo.com/chemistry/ques/detail/b6e8a3b9-d9e5-48ae-903d-40fd3f05e969

        html_string = html_string or self.html_string

        tds = find_valid_elements(html_string, '<td', flags=re.I)
        if len(tds) == 2:
            if tds[1] == '<td style="font-size: 90%"><div style="border-top:1px solid black;line-height:1px">.</div></td>' \
                    or tds[1] == '<td style="font-size:90%"><div style="border-top:1px solid black;line-height:1px">.</div></td>':
                td = remove_start_tag(tds[0])
                self.node_format = '\\xlongequal{{{}}}'
                self.value_strs = [td]
                return True
        return False


    def is_sqrt(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 1:
            return False

        tds = find_valid_elements(trs[0], '<td', with_tag=False, flags=re.I)
        if tds and len(tds) == 2:
            _keys1 = ['02d3676c15d163b68f7c8690c7237c0a',
                      'b5a0e6f59b3540d7c2e032a6d5cc5ae7']
            _keys2 = ['/part/8730D.png']
            if self.md5 is True:
                if not _is_in(_keys1 + _keys2, tds[0]):
                    return False
            else:
                if not _is_in(_keys2 + _keys1, tds[0]):
                    return False
        else:
            return False

        self.node_format = r'\sqrt{{{}}}'
        self.value_strs = [tds[1]]
        return True


    def is_sqrt_n(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(trs[1], '<td', flags=re.I)
        if len(tds) != 1:
            return False

        if '<table' in tds[0]:
            return False

        _keys1 = ['02d3676c15d163b68f7c8690c7237c0a',
                  'b5a0e6f59b3540d7c2e032a6d5cc5ae7']
        _keys2 = ['/part/8730D.png']

        if self.md5 is True:
            if not _is_in(_keys1 + _keys2, tds[0]):
                return False
        else:
            if not _is_in(_keys2 + _keys1, tds[0]):
                return False

        tds = find_valid_elements(trs[0], '<td', with_tag=False, flags=re.I)
        if len(tds) != 2:
            raise ParseFormatError('[is_sqrt_n]:{}'.format(self.html_string))

        self.node_format = r'\sqrt[{}]{{{}}}'
        self.value_strs = tds
        return True


    def is_equations(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 1:
            return False

        # trs[0] = re.sub(r'<td[^<>]*/>', '<td></td>', trs[0], flags=re.I)
        tds = find_valid_elements(trs[0], '<td', with_tag=True, flags=re.I)
        if len(tds) != 3:
            return False

        # brace is at left
        _keys1 = ['6f28da9c3ca14300d4593acc9aad9153',
                  '87030ac64f2d9671babadb5ba43bdb62']
        _keys2 = ['/part/123L.png']

        if _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[0]):

            if '<table' in tds[0]:
                return False

            td = remove_start_tag(tds[1])
            trs = find_valid_elements(td, '<tr', with_tag=False, flags=re.I)
            rows = list()

            for tr in trs:
                tds = find_valid_elements(tr, '<td', with_tag=False, flags=re.I)
                if tds:
                    rows.append(tds)

            if not rows:
                raise ParseFormatError('[is_equations]:{}'.format(self.html_string))

            cols = ' \\\\ '.join([' & '.join(['{}']*len(tds)) for tds in rows])
            self.node_format = (r'\begin{{cases}} '
                                + cols
                                + r' \end{{cases}}')

            for row in rows:
                self.value_strs += row

            return True

        # brace is at right
        elif _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[2]):

            if '<table' in tds[2]:
                return False

            td = remove_start_tag(tds[1])
            trs = find_valid_elements(td, '<tr', with_tag=False, flags=re.I)
            rows = list()

            for tr in trs:
                tds = find_valid_elements(tr, '<td', with_tag=False, flags=re.I)
                if tds:
                    rows.append(tds)

            if not rows:
                raise ParseFormatError('[is_equations]:{}'.format(self.html_string))

            cols = ' \\\\ '.join([' & '.join(['{}']*len(tds)) for tds in rows])
            self.node_format = (  r'\left.'
                                + r'\begin{{array}}{{l}} '
                                + cols
                                + r' \end{{array}}'
                                + r' \right\}}')

            for row in rows:
                self.value_strs += row

            return True

        else:
            return False


    def is_subsup(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 1:
            return False

        tds = find_valid_elements(trs[0], '<td', with_tag=True, flags=re.I)
        tds = [remove_start_tag(td) for td in tds]
        if len(tds) != 2:
            return False

        if '"msubsup' not in tds[1]:
            return False

        divs = find_valid_elements(tds[1], '<div [^<>]+"msubsup', regex=True, flags=re.I)
        if len(divs) != 2:
            raise ParseFormatError('[is_subsup]:{}'.format(self.html_string))

        e = tds[0]
        sub = ''
        sup = ''
        for div in divs:
            index = div.find('>') + 1
            if 'msubsup_sup' in div[:index]:
                sup = remove_start_tag(div)
            elif 'msubsup_sub' in div[:index]:
                sub = remove_start_tag(div)
            else:
                raise ParseFormatError('[is_subsup][not sub or sup]:{}'.format(self.html_string))

        self.node_format = '{{{}}}^{{{}}}_{{{}}}'
        self.value_strs = [e, sup, sub]
        return True


    def is_subsup2(self):
        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(self.html_string, '<td', flags=re.I)
        if len(tds) != 2:
            return False

        index1 = tds[1].find('>') + 1
        if 'style="font-size:90%"' not in tds[1][:index1]:
            return False

        tds0 = remove_start_tag(tds[0])
        trs2 = find_valid_elements(tds0, '<tr', flags=re.I)
        if len(trs2) != 2:
            return False

        if 'style="font-size: 90%"' not in trs2[0]:
            return False

        tds2 = find_valid_elements(tds0, '<td', with_tag=False, flags=re.I)
        if len(tds2) != 2:
            return False

        if '<table' in tds2[1]:
            return False

        tds1 = remove_start_tag(tds[1])

        self.node_format = '{}^{{{}}}_{{{}}}'
        self.value_strs = [tds2[1], tds2[0], tds1]
        return True


    def is_lim(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(trs[0], '<td', flags=re.I)
        if len(tds) != 1:
            return False

        if '<table' in tds[0]:
            return False

        if '<td>lim</td>' not in tds[0]:
            return False

        tds = find_valid_elements(trs[1], '<td', with_tag=False, flags=re.I)
        if len(tds) != 1:
            raise ParseFormatError('[is_lim]:{}'.format(self.html_string))

        self.node_format = r'\lim\limits_{{{}}}'
        # self.value_strs = [tds[0].replace('→', r'\to ')]
        self.value_strs = [tds[0]]
        return True



    def is_overrightarrow(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(trs[0], '<td', flags=re.I)
        if len(tds) != 1:
            return False

        if '<table' in tds[0]:
            return False

        _keys1 = ['6bd6a72411898992479ded42ef82f09c',
                  'a11fdee4d4b49f96bbe3814ad58f817b']
        _keys2 = ['/part/8594.png']

        if self.md5 is True:
            if not _is_in(_keys2 + _keys1, tds[0]):
                return False
        else:
            if not _is_in(_keys1 + _keys2, tds[0]):
                return False

        tds = find_valid_elements(trs[1], '<td', with_tag=False, flags=re.I)
        if len(tds) != 1:
            raise ParseFormatError('[is_overrightarrow]:{}'.format(self.html_string))

        self.node_format = r'\overrightarrow{{{}}}'
        self.value_strs = tds
        return True



    def is_overparen(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(trs[0], '<td', flags=re.I)
        if len(tds) != 1:
            return False

        if '<table' in tds[0]:
            return False

        _keys1 = ['7c229fcab3c2cd74bf9054ddd5f18383',
                  'b339cff44a322d9b88562650f4ed6061']
        _keys2 = ['/part/94.png']

        if self.md5 is True:
            if not _is_in(_keys2 + _keys1, tds[0]):
                return False
        else:
            if not _is_in(_keys1 + _keys2, tds[0]):
                return False

        tds = find_valid_elements(trs[1], '<td', with_tag=False, flags=re.I)
        if len(tds) != 1:
            raise ParseFormatError('[is_overparen]:{}'.format(self.html_string))

        self.node_format = r'\overparen{{{}}}'
        self.value_strs = tds
        return True


    def is_sum(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 3:
            return False

        tds = find_valid_elements(self.html_string, '<td', with_tag=False, flags=re.I)
        if len(tds) != 3:
            return False

        if '<table' in tds[1]:
            return False


        # is_lim
        # {{
        if tds[1] == 'lim':
            self.node_format = r'\lim\limits_{{{}}}'
            self.value_strs = [tds[2]]
            return True
        # }}


        # is_sum
        # {{
        _keys1 = ['19d3e9593386103f95e71affc87e62ea',
                  '5f4100b557a7c8116b2a45e4435b67ae']
        _keys2 = ['/part/8721.png']

        if _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[1]):
            self.node_format = r'\sum^{{{}}}_{{{}}}'
            self.value_strs = [tds[0], tds[2]]
            return True
        # }}


        # is_prod
        # {{
        _keys1 = ['b9331d3ee2218a431c9203512001f479',
                  '9b0bbd95adbebda854a4ec3b1c2ab2e6']
        _keys2 = ['/part/8719.png']

        if _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[1]):
            self.node_format = r'\prod^{{{}}}_{{{}}}'
            self.value_strs = [tds[0], tds[2]]
            return True
        # }}

        return False


    def is_stackrel(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(self.html_string, '<td', flags=re.I)
        if len(tds) != 2:
            return False


        index1 = tds[0].find('>') + 1
        if 'style="font-size: 90%"' not in tds[0][:index1]:
            return False

        # is_underrightarrow
        # change to is_xrightarrow
        if '<table' not in tds[1]:

            _keys1 = ['6bd6a72411898992479ded42ef82f09c',
                      'a11fdee4d4b49f96bbe3814ad58f817b']
            _keys2 = ['/part/8594.png']

            if _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[1]):
                td = remove_start_tag(tds[0])
                self.node_format = '\\xrightarrow{{{}}}'
                self.value_strs = [td]
                return True

        #
        # is_xrightleftharpoons
        # for case, http://www.jyeoo.com/bio2/ques/detail/7003bd54-0861-4152-985a-3c7678ade246
        #
        # {{
        _keys1 = ['ee5caff647b9b23babff8113e9147821',
                  '341e5bdc05923e0895e330d9c062477f']
        _keys2 = ['/part/8652L.png']

        if _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[1]):
            if '<table' in tds[1]:
                return False

            td = remove_start_tag(tds[0])
            self.node_format = '\\xrightleftharpoons{{{}}}'
            self.value_strs = [td]
            return True
        # }}

        tds = [remove_start_tag(td) for td in tds]
        self.node_format = r'\stackrel{{{}}}{{{}}}'
        self.value_strs = tds
        return True


    def is_underset(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(self.html_string, '<td', flags=re.I)
        if len(tds) != 2:
            return False

        index = tds[1].find('>') + 1
        if 'style="font-size: 90%"' not in tds[1][:index]:
            return False

        # for uncommon integral
        _keys1 = ['7ea7ce25490319b1bc0a30f02283c465',
                  '3d579d20afec8779d54985a5acf51879']
        _keys2 = ['/part/8747.png']

        if _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[0]):
            if '<table' not in tds[0]:
                tds = [remove_start_tag(td) for td in tds]
                self.node_format = '\\underset{{{}}}{{\int}}'
                self.value_strs = tds[-1:]
                return True

        tds = [remove_start_tag(td) for td in tds]
        self.node_format = '\\underset{{{}}}{{{}}}'
        self.value_strs = tds[::-1]
        return True


    def is_xrightarrow(self):
        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 3:
            return False

        tds = find_valid_elements(self.html_string, '<td', with_tag=False, flags=re.I)
        if len(tds) != 3:
            return False

        _keys1 = ['6bd6a72411898992479ded42ef82f09c',
                  'a11fdee4d4b49f96bbe3814ad58f817b']
        _keys2 = ['/part/8594.png']

        if _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[1]):
            if '<table' in tds[1]:
                return False

            if tds[2].strip():
                self.node_format = '\\xrightarrow[{}]{{{}}}'
                self.value_strs = [tds[2], tds[0]]
            else:
                self.node_format = '\\xrightarrow{{{}}}'
                self.value_strs = tds[:1]
            return True

        #
        # is_xrightleftharpoons
        #
        # \xrightleftharpoons is defined as:
        # \Newextarrow{\xrightleftharpoons}{10,10}{0x21CC}
        # \Newextarrow is at "extpfeil.js"
        #
        # {{
        _keys1 = ['ee5caff647b9b23babff8113e9147821',
                  '341e5bdc05923e0895e330d9c062477f']
        _keys2 = ['/part/8652L.png']

        if _is_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False], tds[1]):
            if '<table' in tds[1]:
                return False

            self.node_format = '\\xrightleftharpoons[{}]{{{}}}'
            self.value_strs = [tds[2], tds[0]]
            return True
        # }}

        return False


    def is_matrix(self):
        _keys1 = ['deec35943d40f25c3ee53cecf6d466c6',
                  '1f43c8398021a4d9a40916bd8b23e89b']
        _keys2 = ['/part/40U.png']

        matrix_t = 'pmatrix'

        key = _which_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False],
                        self.html_string)

        if key:
            return self.is_matrix_g(key, matrix_t)

        ############################################

        _keys1 = ['6070855b9d1bd27093fe86ddc8214049',
                  '8beed86c241fd41c2771b725bf421ae3']
        _keys2 = ['/part/91.png']

        matrix_t = 'bmatrix'

        key = _which_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False],
                        self.html_string)

        if key:
            return self.is_matrix_g(key, matrix_t)

        ############################################

        _keys1 = ['fc388ec8eb9708ef473e61f6b2002eec',
                  'da0158ef27c6ca95cdeb4952dcdb5f55']
        _keys2 = ['/part/P.png']

        matrix_t = 'vmatrix'

        key = _which_in((_keys1 + _keys2, _keys2 + _keys1)[self.md5 is False],
                        self.html_string)

        if key:
            return self.is_matrix_g(key, matrix_t)

        ############################################

        return False


    def is_matrix_g(self, key, matrix_t):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 1:
            return False

        _tds = find_valid_elements(trs[0], '<td', with_tag=True, flags=re.I)
        if len(_tds) != 3:
            return False

        if '<table' in _tds[0]:
            return False

        if key not in _tds[0] and key not in _tds[2]:
            return False

        td = remove_start_tag(_tds[1])
        trs = find_valid_elements(td, '<tr>', with_tag=True, flags=re.I)
        trs = [remove_start_tag(tr) for tr in trs]
        row_size = len(trs)
        if not row_size:
            raise ParseFormatError('[is_{}][not row]:{}'.format(matrix_t,
                                                                self.html_string))

        rows = list()
        for tr in trs:
            tds = find_valid_elements(tr, '<td', with_tag=True, flags=re.I)
            tds = [remove_start_tag(td) for td in tds]
            rows.append(tds)

        if not rows:
            raise ParseFormatError('[is_{}][not col]:{}'.format(matrix_t,
                                                                self.html_string))

        buckets = list()
        for row in rows:
            buckets.append( ' & '.join(['{}'] * len(row)) )
        bucket = r' \\ '.join(buckets)
        cols = max([len(row) for row in rows])

        for row in rows:
            self.value_strs += row

        #
        # unformated case
        # e.g. http://www.jyeoo.com/math2/ques/detail/80c73320-61e5-4df3-bab7-3134bd8bf834
        #
        # https://kogler.wordpress.com/2008/03/21/latex-multiline-equations-systems-and-matrices/
        #
        pare_l = '.'
        pare_r = '.'
        if matrix_t == 'pmatrix':
            pare_l = '('
            pare_r = ')'
        elif matrix_t == 'bmatrix':
            pare_l = '['
            pare_r = ']'
        elif matrix_t == 'vmatrix':
            pare_l = '|'
            pare_r = '|'

        if key in _tds[0] and key in _tds[2]:
            self.node_format = r'\begin{{%s}} ' % matrix_t + bucket + ' \end{{%s}}' % matrix_t
        elif key in _tds[0] and key not in _tds[2]:
            self.node_format = r'\left%s \begin{{array}}{{%s}} ' % (pare_l, 'c'*cols) + bucket + r' \end{{array}} \right.'
        elif key not in _tds[0] and key in _tds[2]:
            self.node_format = r'\left. \begin{{array}}{{%s}} ' % 'c'*cols + bucket + r' \end{{array}} \right%s' % pare_r

        return True


    def is_integral(self):

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 2:
            return False

        tds = find_valid_elements(self.html_string, '<td', flags=re.I)
        if len(tds) != 2:
            return False

        index = tds[1].find('>') + 1
        if 'style="font-size: 90%"' not in tds[1][:index]:
            return False


        tds = [remove_start_tag(td) for td in tds]
        self.node_format = '\\underset{{{}}}{{{}}}'
        self.value_strs = tds[::-1]
        return True


    def is_align(self):
        """
        e.g. \(\begin{align} -CAGGATCCC & - \\ -GTCCTAGGG & - \end{align}\)
        """

        trs = find_valid_elements(self.html_string, '<tr', flags=re.I)
        if len(trs) != 1:
            return False

        tds = find_valid_elements(self.html_string, '<td', with_tag=False, flags=re.I)
        if len(tds) != 3:
            return False

        if not (tds[0] == '' and tds[2] == ''):
            return False

        if not tds[1].startswith('<table'):
            return False

        index = tds[1].find('>') + 1
        if 'text-align: left' not in tds[1][:index]:
            return False

        trs = find_valid_elements(tds[1], '<tr', flags=re.I)
        value_strs = list()
        rows = list()
        for tr in trs:
            tds = find_valid_elements(tr, '<td', with_tag=False, flags=re.I)
            value_strs += tds
            rows.append(' & '.join(['{}'] * len(tds)))

        self.node_format = '\\begin{{align}} %s \\end{{align}}' % ' \\\\ '.join(rows)
        self.value_strs = value_strs
        return True


    @staticmethod
    def no_table_format(html_string):
        if '<img' in html_string:
            html_string = convert_img_to_latex(html_string)

        html_string = html_string.replace('∏limit{s}', '\prod\limits ')
        html_string = html_string.replace('πlimit{s}', '\prod\limits ')
        html_string = html_string.replace('∑limit{s}', '\sum\limits ')
        html_string = html_string.replace('∫limit{s}', '\int\limits ')

        html_string = html_string.replace('%', ' \\%')

        if 'underpoint' in html_string:
            underpoints = get_html_element('<bdo [^<>]+underpoint',
                                           html_string,
                                           with_tag=True,
                                           regex=True,
                                           flags=re.I)

            for underpoint in set(underpoints):
                t = remove_start_tag(underpoint)
                underpoint_tex = '\\underset{{˙}}{{{}}}'.format(t)
                html_string = html_string.replace(underpoint, underpoint_tex)

        while True:
            spans = find_valid_elements(html_string, '<span ', flags=re.I)
            if not spans:
                break
            for span in spans:
                index = span.find('>') + 1
                if 'vertical-align:sub' in span[:index]:
                    n_span = remove_start_tag(span)
                    html_string = html_string.replace(span, '_{%s}' % n_span, 1)
                elif 'vertical-align:sup' in span[:index]:
                    n_span = remove_start_tag(span)
                    html_string = html_string.replace(span, '^{%s}' % n_span, 1)

        html_string = re.sub(r'<(span|font)>', '', html_string, flags=re.I)
        html_string = re.sub(r'</(span|font)>', '', html_string, flags=re.I)

        return html_string


    @staticmethod
    def fix_any(html_string):
        html_string = remove_tag('<div', html_string, flags=re.I)
        html_string = html_string.replace('&nbsp;', ' ')
        return html_string


def convert_img_to_latex(html_string):
    imgs = get_html_element('<img ', html_string, only_tag=True)
    for img in imgs:

        # for ∑
        if _is_in(('19d3e9593386103f95e71affc87e62ea',
                   '5f4100b557a7c8116b2a45e4435b67ae',
                   '/part/8721.png'), img):
            html_string = html_string.replace(img, '\\sum ')

        # for ∏
        if _is_in(('b9331d3ee2218a431c9203512001f479',
                   '9b0bbd95adbebda854a4ec3b1c2ab2e6',
                   '/part/8719.png'), img):
            html_string = html_string.replace(img, '\\prod ')

        # for ∫
        if _is_in(('7ea7ce25490319b1bc0a30f02283c465',
                   '3d579d20afec8779d54985a5acf51879',
                   '/part/8747.png'), img):
            html_string = html_string.replace(img, '\\int ')

        # for ⋃
        if _is_in(('c7fdd6777f4de5a1f490f96c17a414b3',
                   'cd0da1bb4f8a3b0e0656578988afb49a',
                   '/part/8746.png'), img):
            html_string = html_string.replace(img, '\\bigcup ')

        # for ⋂
        if _is_in(('429c05d3df51962ccb70c6a9306e78ff',
                   '6c9dd31c5750dd38b991f3616df1517c',
                   '/part/8745.png'), img):
            html_string = html_string.replace(img, '\\bigcup ')

    return html_string


def to_latex(html_string, raw=False, md5=False):
    jy_math_span_list = get_html_element('<span [^<>]*?mathtag="math',
                                         html_string,
                                         regex = True,
                                         with_tag=True,
                                         flags=re.I)

    latexes = []

    for jy_math_span_ori in jy_math_span_list:
        jy_math_span = remove_start_tag(jy_math_span_ori)

        # if not <table, no need to convert
        if '<table' not in jy_math_span.lower():
            html_string = html_string.replace(jy_math_span_ori, jy_math_span)
            continue

        jy_math_span = re.sub(r'(<td[^<>]*)/>', r'\1></td>', jy_math_span, flags=re.I)
        root_node = Node()
        if md5 is True:
            root_node.md5 = True
        root_node.node_format = '{}'
        root_node.value_strs = [jy_math_span]
        parse(root_node)
        latex = convert(root_node).strip()
        latex = Node.no_table_format(latex)

        latexes.append(latex)

        if raw is False:
            latex_span = '<span class="afanti-latex">\( {} \)</span>'.format(latex)
            html_string = html_string.replace(jy_math_span_ori, latex_span)
        else:
            html_string = html_string.replace(jy_math_span_ori, '\( {} \)'.format(latex))

    return html_string.strip(), latexes


def parse(node):
    if node.is_str:
        return None

    if node.node_format is None:
        node.parse_format()

    node.get_values()

    for value in node.values:
        for sub_node in value:
            parse(sub_node)


def convert(root_node):
    return str(root_node)

