from clawer.models import *
import hashlib
import requests
import gevent
from gevent import monkey
from django.db.utils import IntegrityError
# from adsl_server.proxy import Proxy
from diff.local_settings import logger
import json
import time


monkey.patch_all(socket=True, dns=True, time=False, select=True,
                 thread=False, os=True, ssl=True, httplib=False, aggressive=True)


class AnoahBaseSpider(object):
    NAME = 'anoah'
    thread_number = 10
    global_id_range = range(1916147, 1841111, -1)
    headers = {
        "GET ": "/1/ HTTP/1.1",
        "Host": "www.anoah.com",
    }
    # _proxy = Proxy()

    def start(self):
        self.run()

    def get_proxy(self):
        proxy = self._proxy.get()
        proxies = {
            "http": proxy
        }
        return proxies

    def save_current_page(self, _id, html, url):
        try:
            AnoahPageHtml.objects.create(
                source_id=_id,
                html=html,
                md5=hashlib.md5(html.encode('utf-8')).hexdigest(),
                key=url,
                request_info=str(self.headers),
            )
        except Exception as e:
            if type(e) == IntegrityError:
                return
            logger.error("[save_error] [%s] [%s]" % (url, e))

    def get_current_page(self, _id):
        url = "http://www.anoah.com/api_cache/?q=json/Qti/get&info={%22param%22:{%22qid%22:%22question:" + str(
            _id) + "%22,%22dataType%22:1}}"
        for i in range(10):  # try 10 times
            # proxies = self.get_proxy()
            proxies = {}
            try:
                res = requests.get(url, headers=self.headers,
                                   proxies=proxies, timeout=20)
            except:
                continue
            if res.text == u'[]':
                break
            try:
                data = json.loads(res.text)
                if data.get('gid'):
                    self.save_current_page(_id, res.text, url)
                    break
            except:
                logger.error("[No_data] [%s] [%s]" % (_id, res.text))
            gevent.sleep(0.1)

    def get_all_page(self, id_range):
        for i in id_range:
            print(i)
            self.get_current_page(i)

    def set_gobal_id(self):
        exit_ids = AnoahPageHtml.objects.all().values_list('source_id')
        exit_ids = list(map(lambda x: x[0], exit_ids))
        exit_ids = list(map(int, exit_ids))
        self.global_id_range = list(set(self.global_id_range) - set(exit_ids))
        self.global_id_range.sort(reverse=True)

    def run(self):
        # self.global_id_range = range(598449, 598469)
        self.set_gobal_id()
        jobs = []
        for i in range(self.thread_number):
            currend_ids = self.global_id_range[i::self.thread_number]
            jobs.append(gevent.spawn(self.get_all_page, currend_ids))
        gevent.joinall(jobs)
