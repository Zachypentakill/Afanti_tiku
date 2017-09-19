from clawer.models import *
import json


class FindTypeParser(object):
    NAME = 'find_type'

    def start(self):
        self.run()

    def run(self):
        ids = AnoahPageHtml.objects.all().values_list('html_id')
        ids = list(map(lambda x: x[0], ids))
        subjects = set()
        for _id in ids[:12000]:
            print(_id)
            page = AnoahPageHtml.objects.get(html_id=_id)
            json_data = json.loads(page.html)
            # subjects.add((json_data['qtypeId'], json_data['qtypeName']))
            if json_data['qtypeId'] == '21':
                print(json_data['qtypeName'])
                print(page.key)
                break



