# -*- coding: utf-8 -*-

import tornado.gen
import os
import tempfile
import logging
import traceback

import asyncio
import multiprocessing

from selenium import webdriver

CONCURRENCY_DEFAULT = multiprocessing.cpu_count()

_DIR = os.path.dirname(os.path.abspath(__file__))

TEMP_DIR = _DIR + '/working/temp_dir'
TEMPLATE = _DIR + '/template.html'


class Driver(object):

    def __init__(self, executable_path='phantomjs'):
        self.executable_path=executable_path
        self.make_driver()

    def make_driver(self):
        self._del_driver()

        self._driver = webdriver.PhantomJS(
            executable_path=self.executable_path,
            service_args=['--load-images=no',
                          '--disk-cache=yes']    # no load images,
                                                 # http://stackoverflow.com/a/20016790
        )
        # config driver

    def _del_driver(self):
        if hasattr(self, '_driver'):
            try:
                # quit browser
                self._driver.quit()
            except Exception as err:
                logging.warn('[Driver._del_driver]: {}'.format(err))
            del self._driver

    def reset_driver(self):
        # self._driver.stop_client()
        # self._driver.start_client()

        # clear localStorage
        self._driver.get('javascript:localStorage.clear();')

        # check number of windows
        while len(self._driver.window_handles) > 1:
            self._driver.close()

    async def check_render_over(self):
        while True:
            page_source = self._driver.page_source
            index = page_source.rfind('<div id="position-signal">')
            if page_source.find('class="mjx-math"', index) != -1:
                return True
            else:
                await tornado.gen.sleep(0.05)

    async def mathjax_render(self, filepath):
        page_source = ''
        while True:
            try:
                self._driver.get('file://' + filepath)
                await self.check_render_over()
                page_source = self._driver.page_source
                self.reset_driver()
                break
            except Exception as err:
                logging.error('[driver error]: {}\n{}'.format(
                    err, traceback.format_exc()))
                self.make_driver()

        return page_source


class TempFile(object):

    def __init__(self, temp_dir=TEMP_DIR, template_str=None):
        assert template_str

        self.temp_dir = (temp_dir or TEMP_DIR)
        self.template_str = template_str

    def make_temp_file(self, html_string):
        temp_file = tempfile.NamedTemporaryFile(suffix='.html', dir=self.temp_dir)
        temp_file.write((self.template_str % ('file://' + _DIR, html_string)).encode('utf8'))
        temp_file.seek(0)
        return temp_file

    def delete_temp_file(self, temp_file):
        if os.path.exists(temp_file.name):
            temp_file.close()


class APhantom(object):

    def __init__(self, template=TEMPLATE,
                 temp_dir=TEMP_DIR,
                 concurrency=CONCURRENCY_DEFAULT,
                 executable_path='phantomjs'):
        self.drivers = [None] * concurrency
        self.free_drivers_queue = asyncio.queues.Queue()
        self.concurrency = concurrency
        self.executable_path = executable_path

        if not os.path.exists(template):
            raise IOError('template.html is not existed')

        template_str = open(template).read()
        self.tempfile = TempFile(temp_dir=temp_dir, template_str=template_str)

        self.init_queue()

    def init_queue(self):
        for i in range(self.concurrency):
            self.free_drivers_queue._queue.append(i)

    def _get_driver(self, index):
        driver = self.drivers[index]
        if driver is not None:
            return driver

        driver = Driver(executable_path=self.executable_path)
        driver.index = index
        Driver.is_free = True
        self.drivers[index] = driver
        return driver

    def _del_driver(self, index):
        driver = self.drivers[index]
        driver._del_driver()
        self.drivers[index] = None

    async def render(self, html_string):

        index = await self.free_drivers_queue.get()
        driver = self._get_driver(index)
        driver.is_free = False

        page_source = await self._render(index, driver, html_string)
        driver.is_free = True
        await self.free_drivers_queue.put(index)
        return page_source

    async def _render(self, index, driver, html_string):
        temp_file = self.tempfile.make_temp_file(html_string)
        # print('render:', index, html_string)
        page_source = await driver.mathjax_render(temp_file.name)
        self.tempfile.delete_temp_file(temp_file)
        return page_source
