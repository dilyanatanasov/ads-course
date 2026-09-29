"""SESSION 12 - Decorator.

    python 12_decorator.py

THE PAIN
    SlowCatalog takes 5ms per lookup. The course page calls it 40 times.
    Add caching WITHOUT editing SlowCatalog - three other teams use it.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Write the check before the cache exists:
                for _ in range(10):
                    cached.title_of("c01")
                check("cache stops repeat lookups", real.hits, 1)
            WHY WE COUNT hits AND NOT TIME: "it got faster" is not a check.
            It is a feeling, it is different on every laptop, and it will
            fail randomly on the one student's machine running a virus scan.
            Count the thing you actually care about - calls that reached the
            slow object. Checks measure behaviour, never mood.

    STEP 2  CachingCatalog.title_of: in the cache? return it. Otherwise ask
            inner, store, return.
            WHY IT IMPLEMENTS Catalog TOO: a decorator is not just a wrapper,
            it is a wrapper THAT PASSES FOR THE REAL THING. That is what lets
            you stack them. Break that and the whole pattern collapses.

    STEP 3  LoggingCatalog the same way. Note neither class knows the other
            exists, and neither knows SlowCatalog exists - they only know
            "something with title_of".

    STEP 4  Now stack them, and predict BEFORE running:
                LoggingCatalog(CachingCatalog(real))     <- log outside
                CachingCatalog(LoggingCatalog(real))     <- cache outside
            Same two classes. Same two objects. Ask the room how many entries
            the log has in each case, after two identical lookups.
            WHY THIS IS THE ENTIRE SESSION: one logs 2, the other logs 1,
            and neither is a bug. Log outside the cache answers "what did
            callers ask for". Cache outside the log answers "what did we
            actually go and fetch". You will want a different one of those
            on a different day, and the ONLY thing that chooses is the order
            you typed the constructors in. That is a design decision hiding
            in punctuation.

YOUR JOB (25 min)
    1. CachingCatalog wraps any Catalog and remembers answers.
    2. LoggingCatalog wraps any Catalog and records calls.
    3. Stack them. Then SWAP THE ORDER and explain what changed.
       That is the whole lesson: wrapping order is a design decision with
       visible consequences.
    STRETCH: TimingCatalog in five lines.

THE DOWNSIDE
    Four layers deep, a bug appears. Which layer? The call stack is
    log -> cache -> timing -> real, and each looks innocent. Also your cache
    starts lying the moment a course title changes and nothing invalidates it.
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

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    #   "logging records calls"
    #       wrap a SlowCatalog in a LoggingCatalog, look up c01 then c02,
    #       and check log.calls.
    #
    # Then the two stacks. WRITE THE PREDICTION DOWN BEFORE YOU RUN EITHER.
    # Both do exactly two identical lookups of "c01":
    #
    #   LoggingCatalog(CachingCatalog(real))    <- log on the OUTSIDE
    #       "log outside cache: cache works"        real.hits is ?
    #       "log outside cache: log sees both"      len(stack.calls) is ?
    #
    #   CachingCatalog(LoggingCatalog(real))    <- cache on the OUTSIDE
    #       "cache outside log: log only sees misses"
    #                                               len(inner_log.calls) is ?
    #
    # The two log counts are different. If your prediction was wrong, do not
    # fix the prediction - work out WHY, out loud, before you touch the code.
    # Neither arrangement is the bug. Being unable to say which one you built
    # is the bug.
    #
    # STRETCH: TimingCatalog in five lines. Then ask where it has to sit in
    #          the stack to measure what you actually meant to measure.
