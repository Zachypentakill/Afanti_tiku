# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os
import tempfile
import logging
import json
import functools

from concurrent.futures import ThreadPoolExecutor

from afanti_tiku_lib.latex.util import (
    latex_clear,
    is_latex,
    fix_underline,
    fix_latex_underline,
)

from afanti_tiku_lib.latex.chinese import safe_chinese


# \usepackage{ltmath}

# \usepackage{yhmath}
# for \wideparen{AB}

# Include LaTeX packages and commands here.
TEX_HEADER = r'''\documentclass{article}
\usepackage{CJKutf8}
\usepackage{yhmath}
\usepackage{amsmath}
\usepackage{amscd}
\usepackage{amsthm}
\usepackage{amssymb}
\usepackage{bm}
\newcommand{\mx}[1]{\mathbf{\bm{#1}}} % Matrix command
\newcommand{\vc}[1]{\mathbf{\bm{#1}}} % Vector command
\newcommand{\T}{\text{T}}             % Transpose
\pagestyle{empty}
\begin{document}
\begin{CJK}{UTF8}{gbsn}'''

TEX_FOOTER = r'''\end{CJK}\end{document}'''


DEFAULT_OUTFILE = 'default_latex2png.png'


class NotDirectory(Exception): pass


def to_png(raw_tex, outfile=None, dpi=200, check=True,
           only_dvi=False, replace=False):
    if not raw_tex:
        return False

    outfile = os.path.abspath(outfile or DEFAULT_OUTFILE)

    # if replace is True, old png will be replaced by new generated png
    if replace is False and os.path.exists(outfile):
        return True

    outdir = os.path.dirname(outfile)
    if not os.path.isdir(outdir):
        raise NotDirectory('directory does not exist: %s' % outdir)

    tex = latex_clear(raw_tex)
    if check is True:
        if not is_latex(tex):
            tex = fix_underline(tex)
            return tex

    tex = fix_latex_underline(tex)
    tex = safe_chinese(tex)

    texfile = tempfile.mkstemp(suffix='.tex', dir=outdir)[1]
    basefile = os.path.splitext(texfile)[0]
    dvifile = basefile + '.dvi'
    temps = [basefile + ext for ext in ('.tex', '.aux', '.log')]

    tex = '%s\n%s\n%s\n' % (TEX_HEADER, '$${}$$'.format(tex), TEX_FOOTER)
    with open(texfile, 'wb') as fd:
        fd.write(tex.encode('utf-8'))

    try:
        status = latex2dvi(texfile, dvifile)
        if status:
            logging.error('[latex2dvi]:{}'.format(
                json.dumps(raw_tex, ensure_ascii=False)))
            return False

        if only_dvi:
            os.rename(dvifile, outfile)
            return True
        else:
            temps.append(dvifile)

        status = dvi2png(dvifile, outfile, dpi=dpi)
        if status:
            logging.error('[dvi2png]:{}'.format(
                json.dumps(raw_tex, ensure_ascii=False)))
            return False
        return True
    finally:
        remove_files(temps)


def to_pngs(texes, texes_outfile, dpi=200, threads=2,
            check=True, only_dvi=False, replace=False):
    '''
    texes are collection of (tex, tex_outfile)
    '''

    pool = ThreadPoolExecutor(max_workers=(max(len(texes), threads)))
    map_iter = pool.map(functools.partial(to_png,
                                          check=check,
                                          only_dvi=only_dvi,
                                          replace=replace),
                        texes, texes_outfile, )
    results = [result for result in map_iter]
    return results


def remove_files(files):
    for file in files:
        if os.path.isfile(file):
            os.remove(file)


def latex2dvi(texfile, dvifile):
    outdir = os.path.dirname(dvifile)
    cmd = 'latex -halt-on-error -interaction=batchmode -output-directory "{}" "{}"'.format(outdir, texfile)
    cmd += ' 2>%s 1>%s' % (os.devnull, os.devnull)
    latex_status = os.system(cmd)
    return latex_status


def dvi2png(dvifile, outfile, dpi=200):
    cmd = 'dvipng'
    if dpi:
        cmd += ' -D %s' % dpi
    cmd += ' -T tight -x 1000 -z 9 -bg Transparent --truecolor -o "%s" "%s" ' \
        % (outfile, dvifile)
    cmd += ' 2>%s 1>%s' % (os.devnull, os.devnull)
    status = os.system(cmd)
    return status

