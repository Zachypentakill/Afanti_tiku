# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql, OrmMysql

import unittest



class TestMysqlPool(unittest.TestCase):

    def test_common_mysql(self):
        mysql_conn = CommonMysql('test').connection()
        mysql_cursor = mysql_conn.cursor()

        mysql_cursor.execute('show databases')
        dbs = mysql_cursor.fetchall()
        self.assertEqual(('test',) in dbs, True)

    def test_orm_mysql(self):
        mysql_db = OrmMysql('test').connection()
        cursor = mysql_db.execute_sql('show databases')
        dbs = cursor.fetchall()
        self.assertEqual(('test',) in dbs, True)

if __name__ == '__main__':
    unittest.main()
