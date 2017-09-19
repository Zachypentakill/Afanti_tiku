# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re

# https://html.spec.whatwg.org/#void-elements
VOID_TAGS = set([
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'keygen',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
])


re_tag = re.compile(r'<(/|)([a-zA-Z][a-zA-Z0-9:]*)([^<>]*)>')
def _html_split_at(html_string, index, with_style=True):
    mod_iter = re_tag.finditer(html_string)
    stack = []
    start_tags = []

    while True:
        try:
            mod = next(mod_iter)
        except StopIteration:
            break

        start = mod.start()
        if start >= index:
            break

        is_end_tag = mod.group(1) == '/'
        tag = mod.group(2)

        if tag.lower() in VOID_TAGS:   # ignore void tags
            continue

        if is_end_tag:
            if stack and stack[-1] == tag:
                stack.pop()
                start_tags.pop()
        else:
            if with_style:
                start_tag = '<{}{}>'.format(mod.group(2), mod.group(3))
            else:
                start_tag = '<{}>'.format(mod.group(2))
            stack.append(tag)
            start_tags.append(start_tag)

    prefix_tags = ''.join(start_tags)
    suffix_tags = ''.join(['</{}>'.format(t) for t in stack[::-1]])

    return html_string[:index] + suffix_tags, prefix_tags + html_string[index:]


def html_split(html_string, sep, offset=0, regex=False,
               flags=re.U, with_style=True):
    result = []

    start, end, *_ = find_place(html_string, sep, offset=offset,
                                regex=regex, flags=flags)
    if start == end == -1:
        result.append(html_string)
    else:
        hs = html_string[:start] + html_string[end:]
        result += _html_split_at(hs, start, with_style=with_style)

    return result


def find_place(haystack, needle, offset=0, regex=False, flags=re.U):
    if regex:
        return find_place_regex(haystack, needle, offset=offset, flags=flags)
    else:
        return find_place_index(haystack, needle, offset=offset)


def find_place_regex(haystack, needle, offset=0, flags=re.U):
    mod_iter = re.finditer(needle, haystack, flags=flags)

    mod = None
    for _ in range(offset + 1):
        try:
            mod = next(mod_iter)
        except StopIteration:
            mod = None
            break

    if not mod:
        return -1, -1, None
    else:
        return mod.start(), mod.end(), mod


def find_place_index(haystack, needle, offset=0):
    index = 0
    for _ in range(offset + 1):
        index = haystack.find(needle, index)
        if index == -1:
            break

    if index > -1:
        return index, index + len(needle)
    else:
        return -1, -1
