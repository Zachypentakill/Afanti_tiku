#encoding:utf-8
from django.db import models


class BaseQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    html_id = models.IntegerField()
    spider_source = models.IntegerField(default=75)
    spider_url = models.CharField(max_length=256)
    knowledge_point = models.CharField(max_length=512)
    subject = models.IntegerField(default=0)
    zhuanti = models.CharField(max_length=256,default='')
    exam_year = models.IntegerField(default=0)
    exam_city = models.CharField(max_length=128,default='')
    difficulty = models.IntegerField(default=0)
    question_type = models.IntegerField(default=0)
    question_quality = models.IntegerField(default=0)
    question_html = models.TextField(default='')
    option_html = models.TextField(default='')
    answer_all_html = models.TextField(default='')
    jieda = models.TextField(default='')
    fenxi = models.TextField(default='')
    dianping = models.TextField(default='')
    question_html_origin = models.TextField(default='')
    option_html_origin = models.TextField(default='')
    answer_all_html_origin = models.TextField(default='')
    jieda_origin = models.TextField(default='')
    fenxi_origin = models.TextField(default='')
    dianping_origin = models.TextField(default='')
    flag = models.IntegerField(default=1994)
    is_rendered = models.IntegerField(default=0)

    class Meta:
        abstract = True


class AnoahQuestion(BaseQuestion):

    class Meta:
        db_table = 'anoah_question_20170209'


class AnoahQuestion0119(BaseQuestion):

    class Meta:
        db_table = 'anoah_question_20160119'


class AnoahQuestion1227(BaseQuestion):

    class Meta:
        db_table = 'anoah_question_20161227'


class OldQuestion(BaseQuestion):

    class Meta:
        db_table = 'anoah_question_20161114'


class OfflineQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    spider_source = models.IntegerField(default=75)
    spider_url = models.CharField(max_length=256)
    knowledge_point = models.CharField(max_length=512)
    subject = models.IntegerField()
    zhuanti = models.CharField(max_length=256,default='')
    exam_year = models.IntegerField(default=0)
    exam_city = models.CharField(max_length=128,default='')
    question_type = models.IntegerField(default=0)
    question_quality = models.IntegerField(default=0)
    question_html = models.TextField()
    option_html = models.TextField()
    answer_all_html = models.TextField()
    jieda = models.TextField()
    fenxi = models.TextField()
    dianping = models.TextField()
    flag = models.IntegerField(default=0)

    class Meta:
        db_table = 'anoah_question_20161117'