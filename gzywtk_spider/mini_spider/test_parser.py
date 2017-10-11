# -*- coding: utf-8 -*-

import json

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.dbs.sql import select_sql

from parser import GzywtkParser

parser = GzywtkParser(download=False)

mysql = CommonMysql('html_archive')
mysql_conn = mysql.connection()


def test():
    sql = select_sql('gzywtk_spider_html_archive_table',
                     ('key', 'html'),
                     condition='where `key` = "http://www.gzywtk.com/tmshow/16650.html"')
                     # condition='where html_id > 0 limit 1')
    rows = execute(mysql_conn, sql)

    for row in rows:
        url = row[0]
        html_string = row[1]

        cols = parser.parse(html_string, url)

        print(json.dumps(cols, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    test()
