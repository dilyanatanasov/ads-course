"""SESSION 22 - From observer to an event bus.

    python 22_event_bus.py         checks
    python 22_event_bus.py demo    one publish, six things happen

Session 08's observer was one publisher with a list of listeners. An event bus
generalises it: anyone publishes, anyone subscribes, neither knows the other.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Write the loop-protection check first:
                bus.subscribe(StudentRegistered,
                              lambda e: bus.publish(StudentRegistered(...)))
                check_raises("loop protection", RuntimeError, bus.publish, ...)
            WHY THE DISASTER FIRST: without the guard this does not fail, it
            HANGS - and a hang in a classroom costs you ten minutes and
            everyone's attention. More importantly, you cannot add loop
            protection later without redesigning publish(). Some properties
            have to be built in from the first line, and "this terminates"
            is one of them.

    STEP 2  subscribe(): a dict of event TYPE -> list of handlers.
            WHY KEYED ON THE TYPE OBJECT ITSELF and not a string name: a
            typo in a string is a handler that silently never runs, and you
            will not find out until the invoice does not go out. A typo in a
            class name is a NameError, right now.

    STEP 3  publish(): append to trace, then dispatch to handlers of that
            exact type.
            WHY TRACE COMES FIRST: if a handler explodes, you still want the
            record that the event happened. Log the fact before you act on
            it - the same reason the queue in session 23 writes the file
            before anyone touches it.

    STEP 4  Now the depth counter, with try/finally.
            WHY finally: an exception must not leave _depth stuck above
            zero, or the bus is permanently poisoned and every later
            publish raises. Shared mutable state that survives a failure is
            session 07 in a new costume.

    STEP 5  Run `python 22_event_bus.py demo`, then ask - without letting
            anyone scroll up to the wiring - WHICH HANDLER RAN THIRD?
            WHY LET THEM SIT IN IT: that silence is the cost of event-driven
            architecture, and it is the reason the trace is not a nice
            extra. Everything the industry sells as "observability" is
            people paying this exact bill at scale.

YOUR JOB (25 min)
    1. subscribe(event_type, handler) and publish(event)
    2. A handler may publish further events (registration -> invoice -> email)
    3. trace records every event, in order
    4. Loop protection: a handler that publishes the event it listens to would
       hang your program. Raise RuntimeError past MAX_DEPTH.

THE TWIST AND THE DOWNSIDE ARE THE SAME THING TODAY
    Run `python 22_event_bus.py demo`. One publish() produces four effects.
    Now answer WITHOUT reading the wiring: which handler ran third?

    That is the real cost of event-driven architecture, and it is why the trace
    is not optional at scale. Everything you read about "observability" is
    people paying this bill.
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

        # ---- NOW YOU WRITE THE REST --------------------------------------
        # Use a FRESH EventBus() for each group - handlers from an earlier
        # group will otherwise still be subscribed and quietly ruin your
        # counts. (Ask yourself why that is the same problem as session 07.)
        #
        #   "handler receives its event"
        #       subscribe a lambda that appends e.student, publish one
        #       StudentRegistered, check what it collected.
        #
        #   "handler ignores other events"
        #       now publish a PaymentReceived on the SAME bus and check the
        #       list did NOT change.
        #       WHY THIS CHECK EARNS ITS PLACE: a bus that calls every
        #       handler for every event also passes the first check. This is
        #       the one that proves the routing is real.
        #
        #   "two handlers, one event"
        #       two handlers on the same type. Check sorted(order).
        #       WHY sorted(): do you actually promise the order handlers
        #       run in? Decide. If you do not promise it, do not check it -
        #       a check that asserts an accident will fail the day someone
        #       changes something unrelated.
        #
        #   "handlers may publish further events"
        #       a handler on StudentRegistered that publishes InvoiceIssued,
        #       and a handler on InvoiceIssued that records the amount.
        #       This is the chain that makes the demo interesting.
        #
        #   "trace records the chain"
        #       [type(e).__name__ for e in bus.trace] - both events, in the
        #       order they happened.
        #       WHY THE TRACE IS THE REAL DELIVERABLE: it is the only thing
        #       that can answer "why did this invoice exist". Build it now,
        #       while the system is four lines long and you still can.
