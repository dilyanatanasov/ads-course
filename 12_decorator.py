"""SESSION 12 - Decorator.

    python 12_decorator.py

THE SITUATION
    SlowCatalog takes 5ms per lookup and the course page calls it 40 times.
    You need caching. You may NOT edit SlowCatalog - three other teams use it
    and you do not own it.

THE IDEA
    Write a class that WRAPS a Catalog, answers from memory when it can, and
    passes the question on when it cannot. Because it implements Catalog
    itself, anything that accepted the original accepts the wrapper - and
    wrappers can be stacked.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. CachingCatalog.title_of - in the cache? return it. Otherwise ask
       inner, store the answer, return it.
    2. LoggingCatalog.title_of - record the id, then ask inner.
    3. Write the four remaining checks at the bottom.

    Count real.hits, never elapsed time. "It got faster" is a feeling, it
    differs on every laptop, and it will fail randomly on the machine running
    a virus scan. Count the calls that actually reached the slow object.

THE ORDER IS THE LESSON
    These two are the same classes and the same objects:

        LoggingCatalog(CachingCatalog(real))     log outside
        CachingCatalog(LoggingCatalog(real))     cache outside

    After two identical lookups, one logs twice and the other logs once.
    Neither is a bug. Log outside the cache answers "what did callers ask
    for". Cache outside the log answers "what did we actually go and fetch".
    You will want a different one on a different day, and the only thing that
    decides is the order you typed the constructors in.

THE COST
    Four layers deep, a bug appears. Which layer? The call stack is
    log -> cache -> real and each looks innocent. And your cache starts lying
    the moment a course title changes, because nothing invalidates it.
"""
import time
from abc import ABC, abstractmethod
from check import check


class Catalog(ABC):
    @abstractmethod
    def title_of(self, course_id):
        ...


class SlowCatalog(Catalog):
    """Pretends to be a database. Do not edit."""

    def __init__(self, delay=0.005):
        self.delay = delay
        self.hits = 0
        self.data = {"c01": "Databases", "c02": "Computer Networks",
                     "c03": "Software Architecture"}

    def title_of(self, course_id):
        self.hits += 1
        time.sleep(self.delay)
        return self.data.get(course_id, "Unknown")


class CachingCatalog(Catalog):
    def __init__(self, inner):
        self.inner = inner
        self.cache = {}

    def title_of(self, course_id):
        raise NotImplementedError    # TODO


class LoggingCatalog(Catalog):
    def __init__(self, inner):
        self.inner = inner
        self.calls = []

    def title_of(self, course_id):
        raise NotImplementedError    # TODO


if __name__ == "__main__":
    print("SESSION 12 - decorator")
    real = SlowCatalog()
    cached = CachingCatalog(real)
    for _ in range(10):
        cached.title_of("c01")
    check("cache stops repeat lookups", real.hits, 1)

    # YOUR TURN - write one check for each, then make them pass:
    #   logging records calls   wrap a SlowCatalog in a LoggingCatalog, look
    #                           up c01 then c02, check log.calls
    #
    # Then the two stacks. WRITE YOUR PREDICTION DOWN BEFORE RUNNING EITHER.
    # Both do exactly two identical lookups of "c01":
    #
    #   LoggingCatalog(CachingCatalog(real))    log on the OUTSIDE
    #       log outside cache: cache works      real.hits is ?
    #       log outside cache: log sees both    len(stack.calls) is ?
    #
    #   CachingCatalog(LoggingCatalog(real))    cache on the OUTSIDE
    #       cache outside log: log only sees misses
    #                                           len(inner_log.calls) is ?
    #
    # The two log counts differ. If your prediction was wrong, work out WHY
    # out loud before touching the code. Neither arrangement is the bug -
    # not knowing which one you built is.
