# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os
from concurrent.futures import ThreadPoolExecutor


def to_latex(raw_mathml, outfile=None):
    if not raw_mathml:
        return ''

    if not raw_mathml[:20].lower().startswith('<xhtml xmlns='):
        mathml = '<XHTML xmlns="http://www.w3.org/1998/Math/MathML">{}</XHTML>'.format(raw_mathml)
    else:
        mathml = raw_mathml

    latex = os.popen('echo "{}" | Xalan - {}'.format(
        mathml.replace('"', '\\"'),
        os.path.join(
            os.path.dirname(__file__),
            'xsltml', 'mmltex.xsl'
        )
    )).read()

    if outfile:
        with open(outfile, 'w') as fd:
            fd.write(latex)

    return latex


def to_latexes(raw_mathmls, threads=2):
    pool = ThreadPoolExecutor(max_workers=threads)
    map_iter = pool.map(to_latex, raw_mathmls)
    latexes = [latex for latex in map_iter]

    return latexes
