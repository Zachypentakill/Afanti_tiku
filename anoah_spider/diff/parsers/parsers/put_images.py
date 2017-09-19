from parsers.models import AnoahQuestion


class ImageCover(object):
    NAME = "image_cover"
    model = AnoahQuestion
    fields = ['fenxi','option_html','question_html_origin','option_html_origin','fenxi_origin', 'answer_all_html_origin' ,'answer_all_html']

    def set_magic(self):
        from afanti_tiku_lib.html.magic import HtmlMagic
        self.html_magic = HtmlMagic(75, archive_image=True, download=True)

    def get_objects_id(self):
        ids = self.model.objects.all().values_list('question_id')
        ids = list(map(lambda x: x[0], ids))
        return ids

    def has_cover(self, html):
        return True if 'http://qimg.afanti100.com/data' in html else False

    def is_image_in(self, question):
        def in_question(field):
            print(question.question_id)
            html = getattr(question, field)
            if not html:
                return False
            if self.has_cover(html):
                return False
            return True if '<img' in html else False
        return in_question

    def bewitch_html(self, question):
        def bewitch_question(field):
            new_html = self.html_magic.bewitch(
                getattr(question, field), spider_url=question.spider_url)
            setattr(question, field, new_html)
        return bewitch_question

    def run_parser(self, _id):
        q = self.model.objects.get(question_id=_id)
        magic = self.bewitch_html(q)
        has_image = self.is_image_in(q)
        is_change = list(map(magic, filter(has_image, self.fields)))
        is_change and q.save()

    def start(self):
        self.run()

    def run(self):
        self.set_magic()
        all_ids = self.get_objects_id()
        list(map(self.run_parser, all_ids))
