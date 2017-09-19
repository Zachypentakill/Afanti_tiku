# -*- coding: utf-8 -*-

from afanti_tiku_lib.html.format_html import remove_option_value, make_option


options = ['<some>A. test A</some>', 'B. 一般的B.', 'C．特殊的C．']

print('origin options', options)

options = remove_option_value(options)

print('remove_option_value', options)

option = make_option(options)

print('make_option', option)
