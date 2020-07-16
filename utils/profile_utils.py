import time
import logging


def profile(f):
    def new_f(*args, **kwargs):
        start = time.time()
        try:
            return f(*args, **kwargs)
        finally:
            end = time.time()
            logging.info("profiler: %s took %.2fms." % (f.__name__, 1000 * (end - start)))

    return new_f
