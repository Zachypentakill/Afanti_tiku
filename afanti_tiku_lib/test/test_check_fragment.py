from afanti_tiku_lib.utils.check_fragment import check_html_valid


htmls = [
    ('<a>略', False),
    ('略', False),
    ('google', True),
    ('<img src="abc">', True),
    ('&nbsp;   &nbsp; 略', False)
]


def test():
    for html_string, fg in htmls:
        flag = check_html_valid(html_string)
        print(repr(html_string), fg, '==>', flag)


if __name__ == '__main__':
    test()
