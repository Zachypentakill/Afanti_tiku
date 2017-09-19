from django.core.management.base import BaseCommand, CommandError
from importlib import import_module
import time
import os


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_label', nargs='*',
                            help='Specify the app label(s) to create migrations for.')

    def handle(self, *args, **options):
        for name in args:
            files = os.listdir('parsers/parsers/')
            for file in files:
                try:
                    file_name, extension = file.split('.')
                except ValueError:
                    print("[%s]file is not exit!" % file)
                    continue
                if extension == 'py':
                    file_obj = import_module('parsers.parsers.%s' % file_name)
                    _vars = dir(file_obj)
                    for _var in _vars:
                        attr = getattr(file_obj, _var)
                        if hasattr(attr, 'NAME'):
                            value = getattr(attr, 'NAME')
                            if value == name:
                                obj = attr()
                                try:
                                    obj.start()
                                    return
                                except:
                                    import traceback; traceback.print_exc();
