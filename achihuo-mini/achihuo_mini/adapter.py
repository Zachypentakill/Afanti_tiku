import os
import json
import signal

from functools import wraps
from .models import CacheInferface, QueueInferface
from .arg import parse_arguments
from .exceptions import NotCommand
from .utils import (
    md5_string,
    serialize_obj,
    unserialize_obj
)
from .settings import (
    LOCAL_CACHE_DIR,
    PIDS,
    KILL_SIGNAL,
    KILL_TERM,
)


def hash_key(func):
    @wraps(func)
    def wrapper(*args):
        self = args[0]
        h = md5_string(args[1])
        rs = func(self, h)
        return rs
    return wrapper


class Adapter:

    def __init__(self, queue, cache):
        assert isinstance(queue, QueueInferface)
        assert isinstance(cache, CacheInferface)

        if not cache.initiated:
            cache.initiate()
        self._queue = queue
        self._cache = cache
        self._current_tasks = {}
        self.tdx = 0


    @property
    def queue(self):
        return self._queue


    @property
    def cache(self):
        return self._cache


    def parse_args(self, argv):
        args = parse_arguments(argv)
        if not args.xxx:
            raise NotCommand()

        args.comd = args.xxx[0]
        args.opts = args.xxx[1:]

        return args


    def register(self, namespace):
        self._cache.register(namespace)


    def get_pids(self, script_filename):
        pid_file = os.path.join(LOCAL_CACHE_DIR, script_filename + '.pids.json')
        if not os.path.exists(pid_file):
            return dict(PIDS)

        pids = json.load(open(pid_file))
        return pids


    def save_pids(self, pids, script_filename):
        pid_file = os.path.join(LOCAL_CACHE_DIR, script_filename + '.pids.json')
        if not os.path.exists(LOCAL_CACHE_DIR):
            os.makedirs(LOCAL_CACHE_DIR)

        with open(pid_file, 'w') as fd:
            json.dump(pids, fd)


    def kill(self, pid):
        os.kill(pid, KILL_SIGNAL.value)


    def restore_current_tasks(self):
        '''
        put all current tasks to queue
        '''
        for k, v in self._current_tasks.items():
            self._queue.put(v, priority=True)   # max_priority


    def get_task(self):
        '''
        get one task from queue
        '''
        task = self._queue.get()
        if not task:
            return 0, task
        else:
            tdx = self.tdx
            self.tdx += 1

            # add task to current tasks
            self._current_tasks[tdx] = task
            u_task = unserialize_obj(task)
            return tdx, u_task


    def task_over(self, tdx):
        '''
        asynchronous task is over, then remove it from current tasks
        '''
        try:
            del self._current_tasks[tdx]
        except Exception:
            pass


    def add_task(self, task, priority=0):
        '''
        add one task to queue
        '''
        s_task = serialize_obj(task)
        self._queue.put(s_task, priority=priority)


    @hash_key
    def task_done(self, task_name):
        '''
        task is done, then save it to task_table
        '''
        self._cache.table_set(0, task_name, 1)


    @hash_key
    def is_task_done(self, task_name):
        '''
        task_name in task_table
        '''
        return self._cache.in_table(0, task_name)


    @hash_key
    def queue_add(self, task_name):
        '''
        add one 'task_name' to current_task_table
        '''
        self._cache.table_incr(1, task_name, 1)


    @hash_key
    def is_in_queue(self, task_name):
        '''
        task_name in current_task_table
        '''
        return self._cache.in_table(1, task_name)


    @hash_key
    def queue_remove(self, task_name):
        '''
        subtract one 'task_name' from current_task_table
        '''
        val = self._cache.table_incr(1, task_name, -1)
        if not val or val < 1:
            self._cache.table_del(1, task_name)


    @hash_key
    def miss_task(self, task_name):
        '''
        ignore one task, remove it from task_table and current_task_table
        '''

        self._cache.table_del(0, task_name)
        self._cache.table_del(1, task_name)

    def clear_cache(self):
        self._cache.table_clear(0)
        self._cache.table_clear(1)

    def clear_queue(self):
        self._queue.delete()
