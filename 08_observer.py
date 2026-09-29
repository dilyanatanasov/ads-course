"""SESSION 08 - Observer.

    python 08_observer.py

THE PAIN
    In session 01, register() printed, logged, counted seats and charged a fee.
    Four unrelated jobs in one method. Every "when a student registers, also..."
    request makes it longer.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Write this check first, with nothing subscribed at all:
                reg.register("Ivan", "Databases")
                check("nobody listening is fine", len(reg.registrations), 1)
            WHY START WITH THE EMPTY CASE: it pins down the most important
            property of the design before any of the interesting code exists
            - registering a student must WORK whether or not anyone is
            listening. Publishing is not part of registering. If you build
            the listeners first you will quietly make them mandatory.

    STEP 2  subscribe() appends to a list. One line.

    STEP 3  register() builds ONE event dict and loops over the listeners.
            WHY A DICT AND NOT THREE ARGUMENTS: every listener takes the same
            shape, so adding a field later does not force you to edit the
            listeners that do not care about it. The event is a contract -
            make it a thing, not a calling convention.

    STEP 4  EmailNotifier only. Run it. Two green.
            WHY ONE LISTENER AT A TIME: if you type all three and something
            breaks, you have three suspects. The whole reason we work in
            small steps is to keep the suspect list at one.

    STEP 5  Now the uncomfortable question, and do not rush past it: what
            happens if EmailNotifier raises? Does AuditLog still run?
            Try it. Decide as a room. Whatever you choose, you are choosing
            - and in a real system that choice is the difference between
            "the email service was down" and "we lost the registration".

YOUR JOB (25 min)
    1. Add subscribe(listener).
    2. register() publishes ONE event instead of doing four things.
    3. Implement EmailNotifier, AuditLog, SeatCounter.
    STRETCH: make one listener raise. Should that stop the others? Decide,
             implement, and defend it.

THE TWIST
    The last check adds an advisor notifier from outside the class, without
    editing Registration at all.

THE DOWNSIDE - the big one
    Read Registration and answer: what happens when a student registers?
    The class does not say. The answer lives in whoever called subscribe(),
    possibly in another file, written by another person, six months ago.
    Easy to extend, hard to follow. Remember this in session 22.
"""
from check import check


class Registration:
    def __init__(self):
        self.registrations = []
        self._listeners = []

    def subscribe(self, listener):
        raise NotImplementedError    # TODO

    def register(self, student, course):
        self.registrations.append((student, course))
        # TODO: publish {"student": ..., "course": ...} to every listener


class EmailNotifier:
    def __init__(self):
        self.sent = []

    def on_registered(self, event):
        raise NotImplementedError    # TODO: "Dear X, you are registered for Y."


class AuditLog:
    def __init__(self):
        self.entries = []

    def on_registered(self, event):
        raise NotImplementedError    # TODO: "REGISTER student course"


class SeatCounter:
    def __init__(self):
        self.taken = {}

    def on_registered(self, event):
        raise NotImplementedError    # TODO: count per course


if __name__ == "__main__":
    print("SESSION 08 - observer")

    # ---- STEP 1: the check we wrote first, with nothing subscribed -------
    reg = Registration()
    reg.register("Ivan", "Databases")
    check("nobody listening is fine", len(reg.registrations), 1)

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    # Subscribe an EmailNotifier, an AuditLog and a SeatCounter to a fresh
    # Registration, then register Ivan and Maria on "Databases". Write one
    # check per behaviour:
    #
    #   "email fired twice"     len(mail.sent)
    #   "audit fired twice"     len(audit.entries)
    #   "seats counted"         seats.taken["Databases"]
    #   "email content"         mail.sent[0] is exactly
    #                           "Dear Ivan, you are registered for Databases."
    #
    # Then the one that matters most - a listener this class never heard of:
    #
    #   "a listener added by someone else"
    #       define an AdvisorNotifier down here, in __main__, outside the
    #       Registration class entirely. Subscribe it. Register Georgi on
    #       "Networks". Check it saw him.
    #       WHY THIS CHECK IS THE POINT OF THE SESSION: it passes without
    #       editing one character of Registration. Compare that with
    #       session 01, where "also notify the advisor" meant opening
    #       register() and making it longer.
    #
    # STRETCH: make one listener raise. Write the check for what you think
    #          SHOULD happen to the others, then make it true. There is no
    #          right answer here - but there is a wrong one, which is not
    #          having decided.
