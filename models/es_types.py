# -*-coding:utf8-*-
import os
import sys
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text, Nested, Boolean, analyzer, InnerObjectWrapper, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

# Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

#ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class Article(DocType):
    #suggest = Completion(analyzer= ik_analyzer)
    title = Text(analyzer= 'ik_max_word')
    subject = Integer()
    grade = Keyword()
    pattern = Text(analyzer= 'ik_max_word')
    province = Text(analyzer= 'ik_max_word')
    year = Text(analyzer= 'ik_max_word')
    ti_number = Keyword()
    watch_number = Integer()
    spider_source = Integer()
    html = Text(analyzer= 'ik_max_word')
    spider_url = Keyword()
    source_id = Integer()

    class Meta:
        index = 'yitiku'
        doc_type = "article"

#     def save(self, ** kwargs):
#         self.lines = len(self.body.split())
#         return super(Article, self).save(** kwargs)
#
#     def is_published(self):
#         return datetime.now() > self.published_from
#
# # create the mappings in elasticsearch
#
#
# # create and save and article
# article = Article(meta={'id': 42}, title='Hello world!', tags=['test'])
# article.body = ''' looong text '''
# article.published_from = datetime.now()
# article.save()
#
# article = Article.get(id=42)
# print(article.is_published())
#
# # Display cluster health
# print(connections.get_connection().cluster.health())

if __name__ == '__main__':
    Article.init()