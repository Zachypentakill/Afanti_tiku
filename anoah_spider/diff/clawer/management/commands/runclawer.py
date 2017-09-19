from django.core.management.base import BaseCommand, CommandError
from importlib import import_module
import gevent
from gevent import monkey
import time
import os

class Command(BaseCommand):
    jobs = []

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_label', nargs='*',
                            help='Specify the app label(s) to create migrations for.')
        parser.add_argument('-n',
                            help='the number of thread')

    def run_thread(self):
        pass

    def start(self):
        gevent.joinall(self.jobs)

    def handle(self, *args, **options):
        thread_number = int(options.get('n')) if options.get('n') else 1
        for name in args:
            files = os.listdir('clawer/spiders/')
            for file in files:
                try:
                    file_name, extension = file.split('.')
                except ValueError:
                    # raise ValueError(
                    #    "Error loading object '%s': not a full path" % name)
                    print("[%s]file is not exit!" % file)
                    continue
                if extension == 'py':
                    file_obj = import_module('clawer.spiders.%s' % file_name)
                    _vars = dir(file_obj)
                    for _var in _vars:
                        attr = getattr(file_obj, _var)
                        if hasattr(attr, 'NAME'):
                            value = getattr(attr, 'NAME')
                            if value == name:
                                obj = attr()
                                try:
                                    print(file)
                                    return obj.start()
                                except:
                                    import traceback
                                    traceback.print_exc()
            print("No clawer")
