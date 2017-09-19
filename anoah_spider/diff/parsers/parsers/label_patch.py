from utils import BaseMixin
from parsers.models import *
from functional import seq
from functools import partial
from tidylib import tidy_document
import re


class LabelPath(BaseMixin):
    NAME = "label_patch"
    model = AnoahQuestion
    model_key = "question_id"
    # fiels = ['question_html_origin','question_html','answer_all_html','answer_all_html_origin']
    fields = ['question_html_origin','question_html','option_html_origin','option_html_origin','fenxi_origin','fenxi_origin']
    container_size = 1000

    def run_parser(self, question):
        print(question.question_id)
        for field in self.fields:
            html = getattr(question, field)
            document, errors = tidy_document(html, options={'numeric-entities':1})
            setattr(question, field, document)
        question.save()

    def multi_update(self, bulk_id):
        questions = AnoahQuestion.objects.filter(question_id__in=bulk_id)
        seq(questions).map(self.run_parser).to_list()

    def start(self):
        self.run()

    def run(self):
        ids = self.get_objects_id()
        bulk_ids = seq(ids).grouped(self.container_size)
        bulk_ids = list(map(list, bulk_ids))
        for bulk_id in bulk_ids:
            self.multi_update(bulk_id)