__author__ = 'msd'
import redis
import config
r = redis.Redis(host=config.REDIS_HOST)


class storage_store_exception(Exception):
    print('An error occured! error code: s01')
    pass


def store(key, value):
    k = r.set(key, value)
    if not k:
        raise storage_store_exception()


def get(key):
    return r.get(key)


def exists(key):
    return r.exists(key)


def remove(key):
    r.delete(key)
