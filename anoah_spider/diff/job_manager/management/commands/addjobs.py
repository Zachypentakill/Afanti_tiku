from django.core.management.base import BaseCommand, CommandError
from job_manager.models import BaseSpiderTask
from rq.job import Job
from rq import Queue
import django_rq
import time

class Command(BaseCommand):
    def handle(self, *args, **options):
        redis_conn = django_rq.get_connection()

        task_name = "xkw_doc_task"

        q = Queue(task_name,connection=redis_conn)
        q.empty()
        all_job_ids = (job for job in q.job_ids)
        locks = BaseSpiderTask.objects.filter(task_name=task_name,status=1)
        locks.update(status=0)
        tasks = BaseSpiderTask.objects.filter(task_name=task_name,status=0)
        for task in tasks:
            if str(task.id) not in all_job_ids:
                job = Job.create(id="%s"%task.id,func=lambda x:True,connection=redis_conn)
                q.enqueue_job(job)
        print "\ncurrent judge task count:[%s]\n"%q.count