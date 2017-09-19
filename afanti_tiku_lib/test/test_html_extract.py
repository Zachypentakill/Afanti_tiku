# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import unittest

from afanti_tiku_lib.html.extract import (
    get_html_element,
    find_valid_elements,
)


class TextHtmlExtract(unittest.TestCase):

    html_string = '''
        <p> p1 <div id="div">
        <p> target </p> </div> <pre>
        code</pre> </p> <b> </b>
        '''

    def test_get_html_element(self):

        e = get_html_element((
            dict(e='<p>', with_tag=False),
            dict(e='<div', with_tag=False),
            dict(e='<p>', with_tag=False),
        ), self.html_string)[0]

        self.assertEqual(e, ' target ')

    def test_find_valid_elements(self):

        es = find_valid_elements(self.html_string)
        self.assertEqual(es, ['<p> p1 <div id="div">\n        <p> target </p> </div> <pre>\n        code</pre> </p>', '<b> </b>'])


if __name__ == '__main__':
    unittest.main()
