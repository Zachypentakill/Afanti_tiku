# -*- coding: utf-8 -*-

import json

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute

from parser import Wln100QuestionParser

mysql = CommonMysql('html_archive')
mysql_conn = mysql.connection()

parser = Wln100QuestionParser()

def test():
    sql = 'select * from wln100_spider_html_archive_table where `key` = "wln100_qs_76285"'
    row = execute(mysql_conn, sql)
    qs_json = json.loads(row[0][3])
    print(qs_json)

    sql = 'select * from wln100_spider_html_archive_table where `key` = "wln100_as_76285"'
    as_json = execute(mysql_conn, sql)[0][3]
    as_json = json.loads(as_json)

    cols = parser.parse('url', qs_json, as_json, row[0][2])
    print(json.dumps(cols, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    test()
