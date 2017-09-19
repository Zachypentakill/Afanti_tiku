#encoding:utf-8
from django.core.management.base import BaseCommand, CommandError
from job_manager.models import BaseSpiderTask
import datetime
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        # base_url = "http://sx.zxxk.com/s-9-0-0-0-0--1-0-0-0--0-0-2-30000-12-0-0---p%s.html"
        base_url = "http://sx.zxxk.com/s-%s-%s-%s-0-0--1-0-0-0--0-0-3-6000-12-0-0---p%s.html"
        request_info = {
            "subject":22,
        }
        objs = []
        for grade in range(10,13):
            for year in range(2004,2018):
                for area in range(1,35):
                    for page in range(1,7):
                    objs.append(BaseSpiderTask(
                        task_name = 'xkw_list_task',
                        url = base_url % (grade,area,year,page),
                        request_info = json.dumps(request_info),
                        status = 0,
                        create_at = datetime.datetime.now(),
                        finished_at = datetime.datetime.now()
                        ))
        BaseSpiderTask.objects.bulk_create(objs)


