from parsers.models import AnoahQuestion
from utils import BaseMixin
from functional import seq
from functools import partial


class ReplacePos(BaseMixin):
    NAME = "replace_pos"
    fields = ['question_html_origin']
    model = AnoahQuestion
    model_key = 'question_id'

    def replace_pop(self, html):
        html = html.replace('<pos></pos>', '____')
        html = html.replace('</pos></pos>', '____')
        html = html.replace(u'（</pos>）', u'（____）')
        return html

    def setfields(self, obj):
        worker = partial(setattr, obj)
        def getfield(field):
            worker(field, self.replace_pop(getattr(obj, field)))
        return getfield

    def has_pos_filter(self, html):
        labels = ['<pos></pos>', '</pos></pos>', u'（</pos>）']
        for label in labels:
            if label in html:
                return True
        return False

    def has_pos(self, obj):
        return (seq(self.fields)
                .map(partial(getattr, obj))
                .filter(self.has_pos_filter)
                )

    def run(self, obj):
        if not self.has_pos(obj):
            return
        print(obj.question_id)
        seq(self.fields).for_each(self.setfields(obj))
        obj.save()


    # def run(self):
    #     self.run_all(self.test_pos)
