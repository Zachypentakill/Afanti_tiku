#! -*- coding: utf-8 -*-

import unittest

from afanti_tiku_lib.html.magic import HtmlMagic
from afanti_tiku_lib.html.beautify_html import center_image

def main():
    html_string = '''
<TBODY>
    <TR>
        <TD>若
            <IMG style="WIDTH: 18px; HEIGHT: 16px; VERTICAL-ALIGN: middle" src="http://pic1.mofangge.com/upload/papers/c02/20120814/20120814192716662863.png">=3，
            <IMG style="WIDTH: 18px; HEIGHT: 14px; VERTICAL-ALIGN: middle" src="http://pic1.mofangge.com/upload/papers/c02/20120814/20120814192716732789.png">=7，则x﹣y的值为&nbsp;&nbsp;&nbsp;&nbsp;</TD>
    </TR>
    <TR>
        <TD>
            <DIV align=right>[&nbsp;&nbsp;&nbsp;&nbsp; ]</DIV>
        </TD>
    </TR>
    <TR>
        <TD>A．±4&nbsp;&nbsp;&nbsp;&nbsp;
            <BR>B．±10&nbsp;&nbsp;&nbsp;&nbsp;
            <BR>C．﹣4或﹣10&nbsp;&nbsp;&nbsp;&nbsp;
            <BR>D．±4或±10</TD>
    </TR>
</TBODY>
</TABLE>
    '''

    html_magic = HtmlMagic(8, download=True, beautify=False)
    html_string = html_magic.bewitch(
        html_string,
        spider_url='http://www.mofangge.com/html/qDetail/02/c1/201208/1kzkc102222121.html',
        spider_source=8,
    )

    html_string = center_image(html_string)

    print(html_string)

if __name__ == '__main__':
    main()
