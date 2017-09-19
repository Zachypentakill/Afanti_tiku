from django.db import models


class BaseSpiderTask(models.Model):
    task_name = models.CharField(max_length=128)
    url = models.CharField(max_length=1024)
    request_info = models.TextField()
    status = models.IntegerField(default=0)
    create_at = models.DateTimeField()
    finished_at = models.DateTimeField()

    class Meta:
        db_table = "base_spider_task"

    def free(self):
        self.status = 0

    def lock(self):
        self.status = 1

    def done(self):
        self.status = 2
