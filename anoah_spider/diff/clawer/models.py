from django.db import models
import datetime


class BasePageHtml(models.Model):
    html_id = models.AutoField(primary_key=True)
    source_id = models.IntegerField(unique=True)
    source = models.IntegerField(default=75)
    subject = models.IntegerField(default=0)
    html = models.TextField()
    md5 = models.CharField(max_length=32)
    key = models.CharField(max_length=256)
    request_info = models.TextField()
    info = models.TextField()
    question_type = models.IntegerField(default=0)
    record_time = models.DateTimeField(default=datetime.datetime.now())
    flag = models.IntegerField()
    flag_str = models.CharField(max_length=256)

    class Meta:
        abstract = True


class SubAnoahPageHtml(BasePageHtml):

    class Meta:
        db_table = 'anoah_sub_page_html_archive_0119'
        app_label = 'html'


class AnoahPageHtml(BasePageHtml):

    class Meta:
        db_table = 'anoah_sub_page_html_archive_0209'
        app_label = 'html'


class AnoahPageHtml0119(BasePageHtml):

    class Meta:
        db_table = 'anoah_page_html_archive_0119'
        app_label = 'html'


class AnoahPageHtml1227(BasePageHtml):

    class Meta:
        db_table = 'anoah_page_html_archive_1227'
        app_label = 'html'


class OldAnoahPageHtml(BasePageHtml):

    class Meta:
        db_table = 'anoah_page_html_archive'
        app_label = 'html'
