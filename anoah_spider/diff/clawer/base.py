from job_manager.models import BaseSpiderTask
from rq.job import Job
from rq import Queue
import django_rq
import urllib2
import time



class BaseSpider(object):
    NAME = "base"
    task_name = ""
    redis_conn = django_rq.get_connection()
    task_model = BaseSpiderTask
    _current_job = None
    _current_task = None


    def _get_job(self):
        queue = Queue(self.task_name, connection=self.redis_conn)
        return queue.dequeue()

    def get_current_job(self):
        self._current_job = self._get_job()
        return self._current_job

    def get_current_task(self):
        self.get_current_job()
        if not self._current_job:
            return None
        self._current_task = self.task_model.objects.filter(
            task_name=self.task_name, id=self._current_job.id).first()
        self._current_task.lock()
        self._current_task.save()
        return self._current_task

    def run(self):
        pass