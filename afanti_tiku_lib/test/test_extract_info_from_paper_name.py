#-*- encoding:utf8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import unittest

from afanti_tiku_lib.utils.extract_info_from_paper_name import extract_info_from_paper_name


class TestExtract(unittest.TestCase):
    def test_extract_info_from_paper_name(self):
        case_lst = self.get_case_lst()
        for paper_name, expect_dict in case_lst:
            res = extract_info_from_paper_name(paper_name)
            '''調試用代碼
            print paper_name
            print 'key\texpct\tres'
            for key in res.keys():
                print key, '\t', expect_dict[key], '\t', res[key]
            '''
            self.assertEqual(res, expect_dict)

    def get_case_lst(self):
        case_lst = []

        paper_name = '2012-2013学年冀教版六年级（上）期末数学试卷（1）'
        expect_dict = dict(
            publisher='冀教版',
            _type='期末',
            city=None,
            grade='六年级上',
            school=None,
            year=2012,
            city_in_short=None,
            subject='数学'
        )
        case_lst.append((paper_name, expect_dict))


        paper_name = '第24章《相似形》常考题集（12）：24.3相似三角形的性质'
        expect_dict = dict(
            publisher=None,
            _type='题集',
            city=None,
            grade=None,
            school=None,
            year=None,
            city_in_short=None,
            subject=None
        )
        case_lst.append((paper_name, expect_dict))


        paper_name = '2013年福建省泉州市永春三中中考物理二模试卷'
        expect_dict = dict(
            publisher=None,
            _type='二模',
            city='福建省泉州市',
            grade='初三',
            school='永春三中',
            year=2013,
            city_in_short='泉州',
            subject='物理'
        )
        case_lst.append((paper_name, expect_dict))


        paper_name = '2014-2015学年山西省吕梁市离石区吕梁学院附中高一（上）第四次月考生物试卷'
        expect_dict = dict(
            publisher=None,
            _type='月考',
            city='山西省吕梁市离石区',
            grade='高一上',
            school='吕梁学院附中',
            year=2014,
            city_in_short='吕梁',
            subject='生物'
        )
        case_lst.append((paper_name, expect_dict))


        paper_name = '2014-2015学年天津市实验中学高三（上）第一次月考数学试卷（理科）'
        expect_dict = dict(
            publisher=None,
            _type='月考',
            city='天津市',
            grade='高三上',
            school='实验中学',
            year=2014,
            city_in_short='天津',
            subject='数学'
        )
        case_lst.append((paper_name, expect_dict))

        paper_name = '2009年江苏省南通市如皋实验初中中考数学二模试卷（顾琰黄亚军）'
        expect_dict = dict(
            publisher=None,
            _type='二模',
            city='江苏省南通市',
            grade='初三',
            school='如皋实验初中',
            year=2009,
            city_in_short='南通',
            subject='数学'
        )
        case_lst.append((paper_name, expect_dict))

        return case_lst

if __name__ == '__main__':
    unittest.main()
