
from afanti_tiku_lib.html.beautify_html import remove_empty_elements


html_strings = [
    '<a></a>',
    '<b>&nbsp;  \r</b>',
    '<p><b>&nbsp;  \r</b></p>',
    '<p class="aft_put"><b>&nbsp;  \r</b></p>',
    '<u>&nbsp;  </u>',
    '<p>&nbsp;  something</p>',
]


def test():
    for html_string in html_strings:
        print(repr(html_string), '==>', repr(remove_empty_elements(html_string)))


if __name__ == '__main__':
    test()
