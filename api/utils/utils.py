import datetime
from toolz import functoolz as F
from typing import List, Any
import pathos.multiprocessing as PM
import xml.dom.minidom as DOM
import multiprocessing.dummy
import subprocess
import itertools
import traceback
import time
import json
import mmh3
import os


class InvalidParametersException(Exception):
    pass


@F.curry
def eq(a, b):
    return a == b


def dosubproc(cmd):
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True).communicate()


def dosubproc_outlines(cmd):
    return dosubproc(cmd)[0].decode('utf8').split('\n')


def flatten(xs):
    return list(itertools.chain.from_iterable(xs))


def rfile(filename, func=lambda x: x):
    with open(filename, 'r') as f:
        return func(f.read())


def wfile(filename, x, func=lambda x: x):
    with open(filename, 'w') as f:
        f.write(func(x))


def rjson(filename):
    return rfile(filename, lambda x: json.loads(x))


def wjson(filename, blob):
    wfile(filename, blob, lambda x: json.dumps(x, indent=4))


def pretty_xml(xml):
    return DOM.parseString(xml).toprettyxml(indent='    ')


def pretty_xml_else(xml, default):
    try:
        return pretty_xml(xml)
    except:
        return default


def readlines(filename):
    with open(filename, 'r') as f:
        return f.readlines()


def trimlines(lines):
    return list(map(lambda x: x.strip(), lines))


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def hashx(x: str) -> str:
    return hex(mmh3.hash128(x))[2:]


def hashxs(xs: List[str]) -> List[str]:
    return list(map(hashx, xs))


def show(x: Any, msg='', f=lambda x: x) -> Any:
    print(msg + str(f(x)))
    return x


def forever(f):
    while True:
        f()


def wait(f, wait_seconds):
    time.sleep(wait_seconds)
    return f()


def until(f, timeout=60) -> None:
    seconds = 0
    while seconds < timeout:
        if f():
            break
        time.sleep(1)
        seconds += 1


def tmap(f, xs, num_threads=4):
    return multiprocessing.dummy.Pool(num_threads).map(f, xs)


@F.curry
def ppmap(num_procs, f, xs):
    return pmap(f, xs, num_procs)


def pmap(f, xs, num_procs=4):
    '''
    Parallel Map.
    The pool spawns threads and never closes them.  Fixed the memory
    leak on our server by doing the following below.
    Note: not modifying the state as done below will cause
    pmap to fail when run more than twice in the same process.
    This has been reproduced reliably in the repl, and was fixed
    by mutating the state of the pool.  Icky.
    https://github.com/uqfoundation/pathos/issues/46
    '''
    pool = PM.ProcessingPool(num_procs)
    result = pool.map(f, xs)
    pool.close()
    PM.__STATE['pool'] = None
    return result


def lossy_map(f, xs, map=map):
    return list(filter(
        lambda x: x is not None,
        map(lambda x: attempt(lambda: f(x)), xs)))


def attempt(f, fail=lambda e: None):
    try:
        return f()
    except Exception as e:
        return fail(e)


def throw(e):
    raise e


def print_stack_trace(e):
    print(traceback.print_exc())


def print_stack_trace_raise(e):
    print(traceback.print_exc())
    raise e


def retry(f, num_attempts=10, fail=throw):
    if num_attempts > 0:
        if num_attempts < num_attempts:
            print('retry {}'.format(num_attempts))
        time.sleep(1)
        return attempt(f, lambda e: retry(f, num_attempts-1, fail))
    else:
        return attempt(f, fail)


def all_files_from_dir(dir):
    return flatten(map(
        lambda x: map(
            lambda y: x[0] + '/' + y, x[2]),
        os.walk(dir)))


def reverse_dict(d):
    return dict(map(lambda x: reversed(x), d.items()))


def fmt_result(result):
    return [F.compose(dict, list, zip)(result.keys(), x) for x in result]


def make_jsonable(result_set):
    for row in result_set:
        for key, value in row.items():
            if type(value) == datetime.datetime:
                row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    return result_set
