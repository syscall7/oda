import collections
from hashlib import sha1
import logging
from oda.apps.odaweb.middleware import get_current_request


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            return None

    def set(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value

def sha1_hash(fh):
    fh.seek(0)
    s = sha1()
    while True:
        data = fh.read(8192)
        if not data:
            break
        s.update(data)
    fh.seek(0)
    return s.hexdigest()

def sha1_hash_contents(data):
    s = sha1()
    s.update(data)
    return s.hexdigest()


import string
import random
def id_generator(size=8, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for x in range(size))


class RequestUserFilter(logging.Filter):
    def filter(self, record):
        request = get_current_request()
        if request:
            record.requestNum = request.requestNum
            record.remoteAddr = request.META.get('REMOTE_ADDR')
        else:
            record.requestNum = '?'
            record.remoteAddr = '?'
        return True