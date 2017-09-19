# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from afanti_tiku_lib.dbs.postgresql_pool import CommonPostgresql, OrmPostgresql

import unittest


class TestPostgresqlPool(unittest.TestCase):

    def test_common_postgresql(self):
        ps_conn = CommonPostgresql('postgres').connection()
        ps_cursor = ps_conn.cursor()

        ps_cursor.execute('select exists(select relname from pg_class where relname=\'pg_statistic\')')
        result = ps_cursor.fetchall()
        self.assertEqual((True,) in result, True)

    def test_orm_postgresql(self):
        ps_db = OrmPostgresql('postgres').connection()
        cursor = ps_db.execute_sql('select exists(select relname from pg_class where relname=\'pg_statistic\')')
        result = cursor.fetchall()
        self.assertEqual((True,) in result, True)

if __name__ == '__main__':
    unittest.main()
