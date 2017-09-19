# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from afanti_tiku_lib.dbs.html_archive import execute, select_one_sql
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql


mysql = CommonMysql('html_archive')
mysql_conn = mysql.connection()


def test_execute():
    sql = select_one_sql('jyeoo_spider_html_archive_table', ('key',), key=True)
    result = execute(mysql_conn, sql, values=('http://www.jyeoo.com/bio/ques/detail/00070579-3662-4ae4-8171-2608f9a82807',), throw=True)
    print(result == [('http://www.jyeoo.com/bio/ques/detail/00070579-3662-4ae4-8171-2608f9a82807',)])


if __name__ == '__main__':
    test_execute()
