#encoding:utf-8
from django.core.management.base import BaseCommand, CommandError
from job_manager.models import BaseSpiderTask
from parsers.models import ZxxkPaper
import datetime
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        request_info = {
            "subject":2,
        }
        url_head = "http://download.zxxk.com/?UrlID=29&InfoID=%s"
        objs = []
        paper_ids = ZxxkPaper.objects.filter(paper_status=1).values_list('id')
        print paper_ids.count()
        for paper_id in paper_ids:
            paper = ZxxkPaper.objects.get(id=paper_id[0])
            BaseSpiderTask.objects.create(
                task_name = 'xkw_doc_task',
                url = url_head % paper.paper_id,
                request_info = json.dumps(request_info),
                status = 0,
                create_at = datetime.datetime.now(),
                finished_at = datetime.datetime.now()
                )
        # BaseSpiderTask.objects.bulk_create(objs)


