"""SESSION 08 - Observer.

    python 08_observer.py

THE SITUATION
    In session 01, register() printed a message, wrote an audit line, counted
    a seat and charged a fee. Four unrelated jobs in one method - and every
    new "when a student registers, also..." request made it longer.

THE IDEA
    register() announces ONE event: this student registered. Whoever cares
    signs up to hear it. Registration stops knowing what happens next.

YOUR TASK (25 min)
    1. subscribe(listener) - append to the list.
    2. register() builds ONE event dict and passes it to every listener.
    3. EmailNotifier, AuditLog and SeatCounter - one on_registered each.
    4. Write the five remaining checks at the bottom.

    Registering a student must work whether or not anyone is listening. The
    first check pins that down, and that is why it comes first: publishing is
    not part of registering.

    Build ONE listener, run it, then the next. If you type all three and
    something breaks you have three suspects.

THE COST - the big one
    When you are done, read Registration and answer: what happens when a
    student registers? The class does not say. The answer lives in whoever
    called subscribe() - possibly another file, written by someone else, six
    months ago.

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

    # YOUR TURN - subscribe an EmailNotifier, an AuditLog and a SeatCounter
    # to a FRESH Registration, register Ivan and Maria on "Databases", then
    # write one check for each:
    #   email fired twice     len(mail.sent)
    #   audit fired twice     len(audit.entries)
    #   seats counted         seats.taken["Databases"]
    #   email content         mail.sent[0] is exactly
    #                         "Dear Ivan, you are registered for Databases."
    #
    # Then the one that matters. Define an AdvisorNotifier down here,
    # OUTSIDE the Registration class. Subscribe it. Register Georgi on
    # "Networks":
    #   a listener added by someone else
    #
    # That one passes without editing a character of Registration. In
    # session 01 the same request meant making register() longer.
