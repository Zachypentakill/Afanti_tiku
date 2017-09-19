# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import


def is_chinese_char(c):
    '''
    2E80－A4CF　
        包含了中日朝部首补充、康熙部首、表意文字描述符、
        中日朝符号和标点、日文平假名、日文片假名、注音字母、
        谚文兼容字母、象形字注释标志、注音字母扩展、中日朝笔画、
        日文片假名语音扩展、带圈中日朝字母和月份、中日朝兼容、
        中日朝统一表意文字扩展A、易经六十四卦符号、
        中日韩统一表意文字、彝文音节、彝文字根

    F900-FAFF
        中日朝兼容表意文字

    FE30-FE4F
        中日朝兼容形式

    FF00-FFEF
        全角ASCII、全角中英文标点、半宽片假名、半宽平假名、半宽韩文字母
        '''
    if u'\u2E80' <= c <= u'\uA4CF':
        return True
    elif u'\uF900' <= c <= u'\uFAFF':
        return True
    elif u'\uFE30' <= c <= u'\uFE4F':
        return True
    elif u'\uFF00' <= c <= u'\uFFEF':
        return True
    else:
        return False


def is_english_char(c):
    if u'\u0020' <= c <= u'\u007F':
    # if u'\u0020' <= c <= u'\u024F':
        return True
    else:
        return False

#麻烦，直接过一遍是不是中文，001111011010 用这么多的while，看着真累
def find_chinese(string):
    indexes = list()
    lenght = len(string)
    i = 0
    ii = 0
    while True:
        if i >= lenght:
            break

        if not is_english_char(string[i]):
            ii += 1
            if ii >= lenght:
                indexes.append((i, ii))
                print(i,ii)
                break
        
            while True:
                if ii < lenght and not is_english_char(string[ii]):
                    ii += 1
                else:
                    indexes.append((i, ii))
                    i = ii + 1
                    ii = i
                    break
        else:
            i += 1
            ii = i

    return indexes


def safe_chinese(string):
    if not string:
        return string

    indexes = find_chinese(string)
    if not indexes:
        return string

    print(indexes)
    ilist = [0]
    for a, b in indexes:
        ilist.append(a)
        ilist.append(b)

    print(ilist)
    if ilist[-1] != len(string):
        ilist.append(len(string))
    print(ilist)

    chucks = [string[ilist[i]:ilist[i+1]] for i in range(len(ilist) - 1)]
    print(chucks)

    for i in range(1, len(chucks), 2):
        print(i)
        chucks[i] = '\\text{' + chucks[i] + '}'
    print(chucks)
    safe_string = ''.join(chucks)

    return safe_string

if __name__ == '__main__':
    # not englist is safe_chinese? naive
    #string="w½"
    string = "aa啊啊www我xxx们sss"
    r=safe_chinese(string)
    print(r)