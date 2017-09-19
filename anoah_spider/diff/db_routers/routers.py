class HtmlRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to html_db.
        """
        if model._meta.app_label == 'html':
            return 'html_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to html_db.
        """
        if model._meta.app_label == 'html':
            return 'html_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'html' or \
           obj2._meta.app_label == 'html':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'html_db'
        database.
        """
        if app_label == 'html':
            return db == 'html_db'
        return None

class GeventRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to html_db.
        """
        if model._meta.app_label == 'gevent':
            return 'gevent_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to gevent_db.
        """
        if model._meta.app_label == 'gevent':
            return 'gevent_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'gevent' or \
           obj2._meta.app_label == 'gevent':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'gevent_db'
        database.
        """
        if app_label == 'gevent':
            return db == 'gevent_db'
        return None