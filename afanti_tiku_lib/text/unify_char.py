from html import unescape
from afanti_tiku_lib.compat import compat_html_unescape as unescape


__slots__ = ['unify_char']


special_character = {
    '⁰':'<sup>0</sup>',
    '¹':'<sup>1</sup>',
    '²':'<sup>2</sup>',
    '³':'<sup>3</sup>',
    '⁴':'<sup>4</sup>',
    '⁵':'<sup>5</sup>',
    '⁶':'<sup>6</sup>',
    '⁷':'<sup>7</sup>',
    '⁸':'<sup>8</sup>',
    '⁹':'<sup>9</sup>',
    '⁺':'<sup>+</sup>',
    '⁻':'<sup>-</sup>',
#    '&sup0;':'<sup>0</sup>',
#    '&sup1;':'<sup>1</sup>',
#    '&sup2;':'<sup>2</sup>',
#    '&sup3;':'<sup>3</sup>',
#    '&frac12;':'<span class="afanti-latex">\( \\\frac{1} {2} \)</span>',


    '½':'<span class="afanti-latex">\( \\frac{1} {2} \)</span>',
    '⅓':'<span class="afanti-latex">\( \\frac{1} {3} \)</span>',
    '¼':'<span class="afanti-latex">\( \\frac{1} {4} \)</span>',
    '⅕':'<span class="afanti-latex">\( \\frac{1} {5} \)</span>',
    '⅙':'<span class="afanti-latex">\( \\frac{1} {6} \)</span>',
    '⅛':'<span class="afanti-latex">\( \\frac{1} {8} \)</span>',
    '⅔':'<span class="afanti-latex">\( \\frac{2} {3} \)</span>',
    '⅖':'<span class="afanti-latex">\( \\frac{2} {5} \)</span>',
    '¾':'<span class="afanti-latex">\( \\frac{3} {4} \)</span>',
    '⅗':'<span class="afanti-latex">\( \\frac{3} {5} \)</span>',
    '⅜':'<span class="afanti-latex">\( \\frac{3} {8} \)</span>',
    '⅘':'<span class="afanti-latex">\( \\frac{4} {5} \)</span>',
    '⅚':'<span class="afanti-latex">\( \\frac{5} {6} \)</span>',
    '⅝':'<span class="afanti-latex">\( \\frac{5} {8} \)</span>',
    '⅞':'<span class="afanti-latex">\( \\frac{7} {8} \)</span>',

    '⎧':'',
    '⎪':'',
    '⎨':'',
    '⎩':'',
    '⎡':'',
    '⎣':'',
    '⎢':'',
    '|':'',
    '⎛':'',
    '⎜':'',
    '⎝':'',
    '⎞':'',
    '⎠':'',
    '⎫':'',
    '⎮':'',
    '⎬':'',
    '⎭':'',
    '丨':'',

}

def unify_char(html):
    html = unescape(html)
    
    for k,v in special_character.items():
        html = html.replace(k, v)

    return html
