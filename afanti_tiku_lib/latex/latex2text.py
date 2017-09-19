# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re
from afanti_tiku_lib.latex.util import find_latexes, FindLatexError
from afanti_tiku_lib.latex.util import unify_tag
from afanti_tiku_lib.latex.subsup2latex import subsup_to_latex
from afanti_tiku_lib.html.extract import get_html_element
from afanti_tiku_lib.latex.util import FindLatexError

SYMBOLS = {
'\\alpha': 'α',
'\\And': '&',
'\\angle': '∠',
'\\approx': '≈',
'\\arccos': 'arccos',
'\\arcsin': 'arcsin',
'\\arctan': 'arctan',
'\\ast': '∗',
'\\because': '∵',
'\\beta': 'β',
'\\bigcap': '⋂',
'\\bigcup': '⋃',
'\\bigoplus': '⨁',
'\\bigvee': '⋁',
'\\bigwedge': '⋀',
'\\bot': '⊥',
'\\bullet': '∙',
'\\cap': '∩',
'\\chi': 'χ',
'\\circ': '∘',
'\\cong': '≅',
'\\cos': 'cos',
'\\cot': 'cot',
'\\csc': 'csc',
'\\cup': '∪',
'\\delta': 'δ',
'\\Delta': 'Δ',
'\\div': '÷',
'\\downarrow': '↓',
'\\emptyset': '∅',
'\\epsilon': 'ϵ',
'\\equiv': '≡',
'\\eta': 'η',
'\\exists': '∃',
'\\forall': '∀',
'\\gamma': 'γ',
'\\Gamma': 'Γ',
'\\ge': '≥',
'\\geq': '≥',
'\\gets': '←',
'\\gt': '>',
'\\in': '∈',
'\\infty': '∞',
'\\iota': 'ι',
'\\kappa': 'κ',
'\\lambda': 'λ',
'\\Lambda': 'Λ',
'\\land': '∧',
'\\le': '≤',
'\\leftarrow': '←',
'\\Leftarrow': '⇐',
'\\leq': '≤',
'\\lnot': '¬',
'\\lor': '∨',
'\\lt': '<',
'\\mapsto': '↦',
'\\mp': '∓',
'\\mu': 'μ',
'\\ne': '≠',
'\\nearrow': '↗',
'\\neq': '≠',
'\\notin': '∉',
'\\nu': 'ν',
'\\odot': '⊙',
'\\omega': 'ω',
'\\Omega': 'Ω',
'\\omicron': 'ο',
'\\oplus': '⊕',
'\\parallel': '∥',
'\\phi': 'ϕ',
'\\Phi': 'Φ',
'\\pi': 'π',
'\\Pi': 'Π',
'\\pm': '±',
'\\prec': '≺',
'\\propto': '∝',
'\\psi': 'ψ',
'\\Psi': 'Ψ',
'\\rho': 'ρ',
'\\rightarrow': '→',
'\\Rightarrow': '⇒',
'\\sec': 'sec',
'\\setminus': '∖',
'\\sigma': 'σ',
'\\Sigma': 'Σ',
'\\sim': '∼',
'\\simeq': '≃',
'\\sin': 'sin',
'\\star': '⋆',
'\\subset': '⊂',
'\\subseteq': '⊆',
'\\subsetneq': '⊊',
'\\supset': '⊃',
'\\surd': '√',
'\\tan': 'tan',
'\\tau': 'τ',
'\\therefore': '∴',
'\\theta': 'θ',
'\\Theta': 'Θ',
'\\times': '×',
'\\to': '→',
'\\top': '⊤',
'\\triangle': '△',
'\\uparrow': '↑',
'\\upsilon': 'υ',
'\\Upsilon': 'Υ',
'\\varnothing': '∅',
'\\vdash': '⊢',
'\\vDash': '⊨',
'\\vec': '→',
'\\vee': '∨',
'\\wedge': '∧',
'\\Xi': 'Ξ',
'\\xi': 'ξ',
'\\zeta': 'ζ',

'\\Alpha': 'Α',
'\\Beta': 'Β',
'\\Chi': 'Χ',
'\\Epsilon': 'Ε',
'\\Eta': 'Η',
'\\Iota': 'Ι',
'\\Kappa': 'Κ',
'\\Mu': 'Μ',
'\\Nu': 'Ν',
'\\Omicron': 'Ο',
'\\Rho': 'Ρ',
'\\Tau': 'Τ',
'\\Zeta': 'Ζ',
'\\quad': ' ',
'\\qquad': ' ',
'\\cdot': '⋅',
}


def to_text(mod):
    key = mod.group().lower()
    replace = SYMBOLS.get(key, key)
    return replace


def latex_to_text(latex):
    latex = latex.replace('\\}', '@&&@')\
                 .replace('\\{', '@##@')\
                 # .replace('_{', '')\
                 # .replace('^{', '')\
                 # .replace('＞', '&gt;')\
                 # .replace('＜', '&lt;')\
                 # .replace('\\surd', '√')\

    
    latex = re.sub(r'\\[a-z]+', to_text, latex, flags=re.I)
    latex = re.sub(r'\{(array|cases|align|aligned)\}(\{.+?\})*', '', latex, flags=re.I)
    #latex = re.sub(r'\{(.*?)\}\^\{(.*?)\}',r'\g<1> \g<2> ' , latex, flags=re.I)
    latex = re.sub(r'\^\s*{(.*?)\}',r' \g<1> ' , latex, flags=re.I)
    latex = re.sub(r'\\sqrt\[[\s{]*(\d*)[\s}]*\]', r'\1', latex, flags=re.I)
    latex = latex.replace('}{', ' ')
    latex = re.sub(r'\\[a-z]+', '', latex, flags=re.I)
    latex = latex.replace('{', '')\
                 .replace('}', '')\
                 .replace('@##@', '{')\
                 .replace('@&&@', '}')\
                 .replace('\\', '')\
                 .replace('\\, ', ' ')\
                 .replace('\\  ', ' ')\
                 .replace('\\; ', ' ')\
                 .replace('\\, ', ' ')\
                 .replace('\\! ', '')\
                 .replace('\\%', '%')\
                 .replace('^', '')\
                 .replace('_', '')

    return latex.strip()


def latex_to_str(to_do_text):
    '''
    在latex_to_text基础上，去除公式两侧的$ $和（）等符号
    '''
    try:
        #肯定是从\(开始，从 )\结束
        pattern = re.compile(r'<span class=\"afanti-latex\">(\\\(.*?\\\))</span>', re.I|re.S|re.U)
        items = pattern.findall(to_do_text)
        for latex in items:
            if latex[0:2] == '\\(':
                unify_latex = latex[2:-2]
                unify_latex = latex_to_text(unify_latex)
                to_do_text = to_do_text.replace(latex, unify_latex)
    except FindLatexError:
           pass
    else:
           pass
    return to_do_text





