"""SESSION 22 - From observer to an event bus.

    python 22_event_bus.py         the checks
    python 22_event_bus.py demo    one publish, four things happen

THE SITUATION
    Session 08's observer was ONE publisher with a list of listeners.
    Registration still had to own the list, so everything that wanted to react
    had to know about Registration.

THE IDEA
    Move the list out into a bus. Anyone publishes, anyone subscribes, and
    neither knows the other exists. A handler may publish further events, so
    one registration can cause an invoice which causes an email.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. subscribe(event_type, handler) - a dict of type -> list of handlers.
       Key it on the TYPE OBJECT, not a string name. A typo in a string is a
       handler that silently never runs; a typo in a class name is a NameError
       right now.
    2. publish(event) - append to trace FIRST, then call the handlers for that
       exact type. Log the fact before acting on it.
    3. Loop protection: a handler that publishes the event it listens to would
       hang your program. Count depth and raise RuntimeError past MAX_DEPTH.
       Use try/finally, or one exception leaves the counter stuck above zero
       and the bus is poisoned for good.
    4. Write the five remaining checks at the bottom. Use a FRESH EventBus for
       each group, or handlers from an earlier group are still subscribed and
       quietly ruin your counts.

THE TWIST AND THE COST ARE THE SAME THING TODAY
    Run `python 22_event_bus.py demo`. One publish() produces four effects.
    Now answer, WITHOUT scrolling up to the wiring: which handler ran third?

    That silence is the real cost of event-driven architecture, and it is why
    the trace is not optional at scale. Everything sold to you as
    "observability" is people paying this exact bill.
"""
import sys
from check import check, check_raises


class StudentRegistered:
    def __init__(self, student, course):
        self.student, self.course = student, course


class InvoiceIssued:
    def __init__(self, student, amount):
        self.student, self.amount = student, amount


class PaymentReceived:
    def __init__(self, student, amount):
        self.student, self.amount = student, amount


class EventBus:
    MAX_DEPTH = 10

    def __init__(self):
        self.handlers = {}
        self.trace = []
        self._depth = 0

    def subscribe(self, event_type, handler):
        raise NotImplementedError    # TODO

    def publish(self, event):
        raise NotImplementedError    # TODO: trace, depth guard, dispatch


def demo():
    bus = EventBus()
    bus.subscribe(StudentRegistered,
                  lambda e: print("  email: welcome to", e.course))
    bus.subscribe(StudentRegistered,
                  lambda e: bus.publish(InvoiceIssued(e.student, 120.0)))
    bus.subscribe(InvoiceIssued,
                  lambda e: print("  email: invoice for %.2f lv" % e.amount))
    bus.subscribe(InvoiceIssued,
                  lambda e: print("  ledger: +%.2f lv receivable" % e.amount))
    print("publishing ONE event:")
    bus.publish(StudentRegistered("s001", "Software Architecture"))
    print("\ncausal trace:")
    for i, event in enumerate(bus.trace, 1):
        print(f"  {i}. {type(event).__name__}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        print("SESSION 22 - event bus")

        # ---- STEP 1: written first, because without it this HANGS --------
        bus = EventBus()
        bus.subscribe(StudentRegistered,
                      lambda e: bus.publish(StudentRegistered(e.student,
                                                              e.course)))
        check_raises("loop protection", RuntimeError, bus.publish,
                     StudentRegistered("s001", "c01"))

        # YOUR TURN - a FRESH EventBus() for each group, or earlier
        # handlers are still subscribed and will ruin your counts:
        #   handler receives its event    subscribe a lambda appending
        #                                 e.student, publish one
        #                                 StudentRegistered
        #   handler ignores other events  publish a PaymentReceived on the
        #                                 SAME bus, check the list did not
        #                                 change. A bus that calls every
        #                                 handler for every event passes
        #                                 the first check too - this is the
        #                                 one that proves routing is real.
        #   two handlers, one event       check sorted(order). Do you
        #                                 actually promise the order
        #                                 handlers run in? If not, do not
        #                                 check it.
        #   handlers may publish further events
        #                                 a StudentRegistered handler that
        #                                 publishes InvoiceIssued, and an
        #                                 InvoiceIssued handler recording
        #                                 the amount
        #   trace records the chain       [type(e).__name__ for e in
        #                                 bus.trace] - both events, in
        #                                 order. The trace is the only
        #                                 thing that can ever answer "why
        #                                 did this invoice exist".
