# -*- coding:utf8 -*-
from __future__ import unicode_literals, absolute_import
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import afanti_tiku_lib
import re
import os
import chardet
import codecs


'''
!!!!
不兼容py3
'''
top_dir = os.path.dirname(afanti_tiku_lib.__file__)
city_file = os.path.join(top_dir, 'utils/city.txt')
province_file = os.path.join(top_dir, 'utils/province.txt')

dict_subject = {'语文': 1, '数学': 2, '英语': 3, '物理': 5, '化学': 6, '地理': 7, '历史': 8, '生物': 9, '政治': 10}
dict_grade = {'一年级': 1, '二年级': 2, '三年级': 3, '四年级': 4, '五年级': 5, '六年级': 6, '小学': 6, '七年级': 7, '八年级': 8, '九年级': 9,
              '初一': 7, '初二': 8, '初三': 9, '初中': 9, '高一': 11, '高二': 12, '高三': 13, '高中': 13}
dict_type = {'期中': 1, '期末': 2, '模拟': 3, '中考': 4, '高考': 5, '同步': 6, '训练': 7, '练习': 8, '测试': 9, '复习': 10, '题集': 11,'一模':12,
             '二模':13, '三模':14, '月考':15,'质检':16,'竞赛':17, '暑假':18, '寒假':19}


with codecs.open(city_file, 'r', 'utf8') as f:
    CITY_LST = [line.strip() for line in f]


with codecs.open(province_file, 'r', 'utf8') as f:
    PROVINCE_LST = [line.strip() for line in f]


def extract_info_from_paper_name(paper_name):
    '''从试卷中提取年份、地区、学校、学科、试卷类型
    通过观察，得知大多数试卷名称的组合方式为" 年份+地区+学校+年级+试卷类型+学科"
    根据此规律，利用正则依次提取各元素
    '''
    # 年份有两种表示方法2016-2017学年， 2016年
    if isinstance(paper_name, str):
        paper_name = paper_name.decode(chardet.detect(paper_name).get('encoding'))
    origin_paper_name = paper_name
    year_pattern = re.compile(ur'(\d{4}-\d{4}学?年?度?)', flags=re.U)
    tmp_res = year_pattern.findall(paper_name)
    year = tmp_res[0] if tmp_res else None
    if not year:
        year_pattern = re.compile(r'\d{4}年', flags=re.U)
        tmp_res = year_pattern.findall(paper_name)
        year = tmp_res[0] if tmp_res else None
        if not year:
            year_pattern = re.compile(r'(?<=\d)\d{4}(?=\D)', flags=re.U)
            tmp_res = year_pattern.findall(paper_name)
            year = tmp_res[0] if tmp_res else None
    if year:
        paper_name = paper_name.replace(year, '')

    # 城市一般形式为 xx省xx市(地区)xx县(区)，其中市(地区)为必有选项
    # 或者山东卷 形式
    city_pattern = re.compile(r'^((\S{2,5}(省|自治区))?\S{1,8}(市|地区)(\S{1,5}[县区])?)', flags=re.U)
    tmp_res = city_pattern.findall(paper_name)
    city = tmp_res[0][0] if tmp_res and tmp_res[0] else None
    if not city:
        city_pattern = re.compile(r'[^(（试高]{2,3}(?=卷)', flags=re.U)
        tmp_res = city_pattern.findall(paper_name)
        city = tmp_res[0] if tmp_res else None
    if city:
        # 遍历省份列表，判断city是否是城市省份信息，避免错误提取
        for province in PROVINCE_LST:
            if province in city:
                paper_name = paper_name.replace(city, '')
                break
        if city in paper_name:
            city = None


    #学校一般形式为 xx学校  xx中学  三中  中心校
    school_pattern = re.compile(r'^((\S{2,5})?(([一二三四五六七八九十百]+?中)|小学|初中|高中|学校|中学|校|附中))', flags=re.U)
    tmp_res = school_pattern.findall(paper_name)
    school = tmp_res[0][0] if tmp_res and tmp_res[0] else None
    if school:
        paper_name = paper_name.replace(school, '')

    #年级信息一般形式为 九年级(下)  高二 九年级第一学期
    grade_pattern = re.compile(r'(高[一二三](?:年级)?(([(（][上下][）)])|(第[一二]学期))?)', flags=re.U)
    tmp_res = grade_pattern.findall(paper_name)
    grade = tmp_res[0][0] if tmp_res and tmp_res[0] else None
    if not grade:
        grade_pattern = re.compile(r'([一二三四五六七八九]年级(([(（][上下][）)])|(第[一二]学期)))', flags=re.U)
        tmp_res = grade_pattern.findall(paper_name)
        grade = tmp_res[0][0] if tmp_res and tmp_res[0] else None
    if grade:
        paper_name = paper_name.replace(grade, '')
        grade = grade.replace('第一学期', '上').replace('第二学期', '下')
        grade = grade.replace('（', '').replace('）', '')

    subject = None
    subject_lst = ['语文', '数学', '英语', '政治', '历史', '地理', '物理', '化学', '生物']
    for subject_item in subject_lst:
        if subject_item in paper_name:
            subject = subject_item
            break
    if subject:
        paper_name = paper_name.replace(subject, '')

    _type = None
    # 试卷类型列表的排列有优先级，不能随意调换位置
    _type_lst = ['模拟', '期中', '期末', '月考', '同步', '练习', '训练', '测试',  '一模', '二模', '三模', '复习', '中考', '高考', '题集', '质检', '竞赛', '暑假', '寒假']
    for _type_item in _type_lst:
        if _type_item in paper_name:
            _type = _type_item
            break
    if _type:
        paper_name = paper_name.replace(_type, '')
    if _type and not grade:
        if _type in ['一模', '二模', '三模'] and grade is None:
            if origin_paper_name.find('中考') != -1:
                grade = '初三'
            else:
                grade = '高三'
        elif _type in ['高考'] and grade is None:
            grade = '高三'
        elif _type in ['中考'] and grade is None:
            grade = '初三'
        else:
            grade = None

    #出版社一般的格式为 新人教版  沪教版 北师大版
    publisher = None
    publisher_pattern = re.compile(r'\S{2,3}版', flags=re.U)
    res = publisher_pattern.findall(paper_name)
    publisher = res[0] if res else None

    # 僅提取出城市名稱，如果沒有城市名稱，提取省份信息
    city_in_short = None
    if city:
        for city_item in CITY_LST:
            if city_item in city:
                city_in_short = city_item
                break
        if not city_in_short:
            for province_item in PROVINCE_LST:
                if province_item in city:
                    city_in_short = province_item

    # 根據上下學期判斷年份信息
    # 2016-2017學年上學期， 判斷爲2016年， 下學期判斷爲2017年
    if year:
        year_pieces = re.findall('\d{4}', year, flags=re.U)
        if len(year_pieces) == 1:
            year = int(year_pieces[0])
        elif len(year_pieces) == 2:
            min_year, max_year = sorted(map(int, year_pieces))
            if grade:
                if '上' in grade and '下' not in grade:
                    year = min_year
                elif '上' not in grade and '下' in grade:
                    year = max_year
                else:
                    year = min_year
            else:
                year = min_year

    if subject:
        subject_id = dict_subject.get(subject, 0)
    else:
        subject_id = 0
    if grade:
        grade_id = dict_grade.get(grade.replace('上', '').replace('下', ''), 0)
    else:
        grade_id = 0

    if _type:
        _type_id = dict_type.get(_type, 0)
    else:
        _type_id = 0


    return dict(
        year=year,
        city=city,
        school=school,
        grade=grade,
        grade_id=grade_id,
        subject=subject,
        subject_id=subject_id,
        _type=_type,
        _type_id=_type_id,
        publisher=publisher,
        city_in_short=city_in_short
    )


