# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re

from afanti_tiku_lib.compat import compat_str


def _find_one_element(tag, tag_end, string, start=0, with_tag=True):
    """
    find first element with tag

    No use it directly.
    """

    _string = string
    string = _string.lower()

    tag = tag.lower()
    tag_end = tag_end.lower()

    start = string.find(tag, start)
    tag_index = start
    tag_end_index = start

    while True:
        i = string.find(tag, tag_index + len(tag))

        # ignore same pre tag's element, e.g. <p, <pre
        if i != -1 and string[i+len(tag)] not in (' ', '>'):
            tag_index += len(tag)
            continue

        ii = string.find(tag_end, tag_end_index + len(tag_end) - 1)
        if i == -1 or i > ii:
            if ii != -1:
                result = _string[start:ii + len(tag_end)]
            else:
                result = None
            break
        elif i < ii:
            tag_index = i
            tag_end_index = ii

    if not result:
        return None

    if with_tag is False:
        return re.sub('^' + tag + '.*?>', '', result)[:-len(tag_end)]
    return result

def get_html_text(string, subs=''): # subs is substitute
    return re.sub(r'<.+?>', subs, string)

def _limit_re_iter(re_iter, limit=None):
    if limit is None:
        re_list = list(re_iter)
        return re_list

    elif limit == 0:
        return list()

    elif limit < 0:
        re_list = list(re_iter)
        return re_list[limit:]

    elif limit > 0:
        re_list = list()
        for count in range(limit):
            try:
                item = next(re_iter)
                re_list.append(item)
            except StopIteration:
                break
        return re_list

def _get_html_element_with_sub_tags(args, html):
    result = [html]
    for arg in args:
        tmp_result = list()
        for s in result:
            tmp_result += _get_html_element_list(
                                arg.get('e'),
                                s,
                                with_tag=arg.get('with_tag', True),
                                regex=arg.get('regex', False),
                                flags=arg.get('flags', re.U),
                                limit=arg.get('limit', None),
                                only_tag=arg.get('only_tag', False),
                                text=arg.get('text', False))
        result = tmp_result
    return result

def _get_html_element_list(element, html,
                          with_tag=True,
                          regex=False,
                          flags=re.U,
                          limit=None,
                          only_tag=False,
                          text=False):
    element_list = []
    if not regex:
        element = re.escape(element)

    tags_iter = re.finditer(element, html, flags=flags)
    tags_list = list()

    # handle argument 'limit'
    if limit is None:
        tags_list = _limit_re_iter(tags_iter, limit)
    elif type(limit) is int:
        tags_list = _limit_re_iter(tags_iter, limit)
    elif type(limit) is slice:
        stop = limit.stop
        tags_list = _limit_re_iter(tags_iter, stop)[limit]
    else:
        raise TypeError('"limit" must be a int or slice')

    for index, it in enumerate(tags_list):
        # find first tag from matched place
        if index == len(tags_list) - 1:
            _mod = re.search(r'(<[\w:\d]+)',
                                html[it.start():],
                                flags=re.U)
        else:
            _mod = re.search(r'(<[\w:\d]+)',
                                html[it.start(): tags_list[index + 1].end()],
                                flags=re.U)
        if not _mod:
            continue

        tag = _mod.group(1)
        tag_end = tag.replace('<', '</') + '>'

        # only find tag header
        # for '<img ... >' like without end tag
        if only_tag:
            if index == len(tags_list) - 1:
                _mod_t = re.search(r'<[^<>]+?>', html[it.start():])
            else:
                _mod_t = re.search(
                    r'<[^<>]+?>',
                    html[it.start(): tags_list[index + 1].start()])
            if _mod_t:
                element_list.append(_mod_t.group())
            continue

        elem = _find_one_element(tag, tag_end, html,
                                 start=it.start(),
                                 with_tag=with_tag)
        if text:
            elem = get_html_text(elem)
        if elem is not None:
            element_list.append(elem)

    return element_list

def get_html_element(element, html,
                     with_tag=True,
                     regex=False,
                     flags=re.U,
                     limit=None,
                     only_tag=False,
                     text=False):
    if element and \
        type(element) in (list, tuple) and \
        type(element[0]) is dict:

        elems = _get_html_element_with_sub_tags(element, html)

    elif type(element) is compat_str:
        elems = _get_html_element_list(element, html,
                                       with_tag=with_tag,
                                       regex=regex,
                                       flags=flags,
                                       limit=limit,
                                       only_tag=only_tag,
                                       text=text)
    else:
        raise TypeError('element - {} is not supported'.format(type(element)))

    return elems

def find_valid_elements(string,
                        element='',
                        with_tag=True,
                        regex=False,
                        flags=re.U,
                        only_tag=False,
                        text=False,
                        max_loop=1500):
    start=0
    result = []
    for count in range(max_loop):
        start = string.find('<', start)
        if start == -1 or start == len(string) - 1:
            # start == len(string) - 1
            # like 'something <'
            return result
        if string[start+1] == '/':
            start += 2
            continue
        if element:
            e = get_html_element(element, string[start:],
                                 limit=1,
                                 with_tag=True,
                                 regex=regex,
                                 flags=flags,
                                 only_tag=False,
                                 text=text)
        else:
            e = get_html_element('<[\w:\d]+', string[start:],
                                 limit=1,
                                 with_tag=True,
                                 regex=True,
                                 flags=flags,
                                 only_tag=False,
                                 text=text)
        if not e:
            # not find one element
            # return the result
            return result

        if only_tag is False:
            if with_tag is False:
                ne = [remove_start_tag(i) for i in e]
                result += ne
            else:
                result += e
        else:
            et = e[0]
            index = et.find('>') + 1
            result.append(et[:index])

        e = e[0]
        next = string.find(e, start)
        start = next + len(e)


def remove_start_tag(html_string):
    start = html_string.find('>') + 1
    end = html_string.rfind('<')
    return html_string[start:end]
