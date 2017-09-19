from parsers.models import *
from django.db import transaction
from utils import *
from django.db import connection
from functional import seq
import time
from gevent import monkey


monkey.patch_all(socket=True, dns=True, time=True, select=True,
                 thread=False, os=True, ssl=True, httplib=False, aggressive=True)


class UpdateTest(BaseMixin):
    NAME = "update_test"
    model = AnoahQuestion
    model_key = 'question_id'
    container_size = 1000

    def start(self):
        self.run()

    @transaction.non_atomic_requests
    def multi_update(self, bulk_id):
        questions = AnoahQuestion.objects.filter(question_id__in=bulk_id)
        for question in questions.iterator():
            # t1 = time.time()
            # question = AnoahQuestion.objects.get(question_id=_id)
            question.question_html = "<br><html><p>mymusise123</p></html><>"
            question.save()
            # print("use2:%s" % (time.time() - t1))

        # for _id in bulk_id:
        #     AnoahQuestion.objects.filter(question_id=_id).update(question_html='<p>mymusise2</p>')

        # cursor = connection.cursor()
        # for _id in bulk_id:
        #     sql = "select * from anoah_question_20161114 where question_id = %s" % _id
        #     cursor.execute(sql)
        #     sql = "update anoah_question_20161114 set question_html = '' where question_id = %s" % _id
        #     cursor.execute(sql)


    def run(self):
        t1 = time.time()
        ids = self.get_objects_id()
        bulk_ids = seq(ids).grouped(self.container_size)
        bulk_ids = list(map(list, bulk_ids))
        for bulk_id in bulk_ids:
            self.multi_update(bulk_id)
        print("use1:%s" % (time.time() - t1))


    # def run(self):
    #     t1 = time.time()
    #     ids = self.get_objects_id()
    #     for _id in ids:
    #         question = AnoahQuestion.objects.get(question_id=_id)
    #         question.question_html = "<html><p>mymusise run</p></html>"
    #         question.save()
    #     print("use2:%s" % (time.time() - t1))

# from django.db import connection