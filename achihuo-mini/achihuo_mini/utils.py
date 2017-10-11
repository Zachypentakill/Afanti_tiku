import hashlib
import pickle

DEFAULT_ENCODING = 'utf-8'


def has_http_policy(obj):
    if not isinstance(obj, str):
        return False
    else:
        if obj.startswith('http'):
            return True
        else:
            return False


def md5_string(string, encoding=DEFAULT_ENCODING):
    if not isinstance(string, str):
        try:
            string = string.decode(DEFAULT_ENCODING)
        except Exception:
            raise TypeError('string must be unicode')

    return hashlib.md5(string.encode(DEFAULT_ENCODING)).hexdigest()


def serialize_obj(obj):
    return pickle.dumps(obj)

def unserialize_obj(obj):
    return pickle.loads(obj)

