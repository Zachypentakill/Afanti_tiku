# -*- coding: utf-8 -*-

import pandas as pd
import re
import time
from multiprocessing import Process,Pool

def openfile(path):
    data = pd.read_csv(path)
    return data

def parse_duilian(data):
    a = len(data)
    list_numbers = []
    for i in range(a):
        for duilian_url in data.iloc[i, 1:2]:
            if duilian_url not in list_numbers:
                list_numbers.append(duilian_url)

    with open('duilian_shengyu_url.txt', 'wt') as f1:
        for i in list_numbers:
            f1.writelines(i +  ',')
    f1.close()
    return list_numbers
    # for j in range(a):
    #     for xialians in data.iloc[j,4:5]:
    #         if '横批' in xialians:
    #             items = {}
    #             xialian = re.findall('(.+?)横批', xialians)
    #             hengpi = re.findall('横批:(.+?)',xialians)
    #             xialians = xialian[0]
    #             #items = {'{}'.format(j):hengpi[0]}
    #             xialian_list.append(xialians)
    #             list_numbers.append(items)
    #         else:
    #             xialian_list.append(xialians)
    # with open('xialian_duilian_parse.csv', 'wt') as f2:
    #     for j in xialian_list:
    #         f2.writelines(j + '\n')
    # f2.close()





if __name__ == '__main__':
    path1 = u'C:/Users/afanty/Desktop/duilian_parse_temp.csv'
    data = openfile(path=path1)
    new_list = parse_duilian(data=data)
    print(new_list)