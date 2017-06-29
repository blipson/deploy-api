from functools import wraps
import time


def now():
    return int(round(time.time() * 1000))


def timed(f):
    @wraps(f)
    def timer(*args, **kwargs):
        starttime = now()
        result = f(*args, **kwargs)
        print('[Stats] ' +
              str({'function': f.__name__,
                   'runtime_ms': int(now() - starttime)}))
        return result

    return timer
