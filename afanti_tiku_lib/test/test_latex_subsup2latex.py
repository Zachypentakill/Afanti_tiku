# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from afanti_tiku_lib.latex.subsup2latex import subsup_to_latex


subsups = [
'a<sup>   1    </sup>',
'(a+b)  <sub>1</sub>',
'((a+b)*(a-b))<sup>2</sup>',
'abc  <sub>1</sub>',
'你<sub>1</sub>',
'$  <sub>1</sub>',
]


def test():
    for ss in subsups:
        print(subsup_to_latex(ss))


if __name__ == '__main__':
    test()
