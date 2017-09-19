
from afanti_tiku_lib.html.util import html_split


html_strings = [
    'abc g ef<a>g</a>',
    '<a>abc g efg</a>',
    '<a>asdf<b>abc g efg</b></a>',
    '<a>as<p>gggg</p>df<b>abc g efg</b></a>',
    '<a>as<p class="p">ggg</p>df<b>abc g efg</b></a>',
    '<a>a<img>bc g efg</a>',
    '<a>a<br>bc g efg</a>',
]


def test():
    for html_string in html_strings:
        print(repr(html_string), html_split(html_string, ' g '))


if __name__ == '__main__':
    test()
