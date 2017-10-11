# -*- coding: utf-8 -*-

import os
import traceback
import tempfile
import time
import logging

from selenium import webdriver

_DIR = os.path.dirname(os.path.abspath(__file__))

TEMP_DIR = _DIR + '/working/temp_dir'
TEMPLATE = _DIR + '/template.html'

class Phantom(object):

    def __init__(self, template=TEMPLATE, temp_dir=TEMP_DIR):
        self.temp_dir = (temp_dir or TEMP_DIR)

        if not os.path.exists(template):
            raise IOError('template.html is not existed')

        self.template_str = open(template).read()
        self.make_driver()

    def make_temp_file(self, html_string):
        filepath = tempfile.mkstemp(suffix='.html', dir=self.temp_dir)[1]
        with open(filepath, 'w') as fd:
            fd.write(self.template_str % ('file://' + _DIR, html_string))
        return filepath


    def delete_temp_file(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)


    def make_driver(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            del self.driver

        driver = webdriver.PhantomJS()
        # config driver

        self.driver = driver


    def reset_driver(self):
        self.driver.stop_client()
        self.driver.start_client()


    def check_render_over(self):
        while True:
            page_source = self.driver.page_source
            index = page_source.rfind('<div id="position-signal">')
            if page_source.find('class="mjx-math"', index) != -1:
                return True
            else:
                time.sleep(0.009)


    def mathjax_render(self, html_string):
        filepath = self.make_temp_file(html_string)
        while True:
            try:
                self.driver.get('file://' + filepath)
                self.check_render_over()
                break
            except Exception as err:
                logging.error('[driver error]: {}\n{}'.format(err, traceback.format_exc()))
                self.make_driver()

        self.delete_temp_file(filepath)
        page_source = self.driver.page_source
        self.reset_driver()

        return page_source

