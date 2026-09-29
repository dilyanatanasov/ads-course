"""SESSION 14 - State machine.

    python 14_state_machine.py

THE SITUATION
    An enrolment is tracked with four booleans: is_submitted, is_confirmed,
    is_cancelled, is_paid. That is 16 combinations, and about five of them
    make sense.

    Somewhere in a real university system there is an enrolment that is both
    cancelled and confirmed, and nobody knows how it got that way.

THE IDEA
    One `state` instead of four flags, plus an explicit table of which moves
    are legal. An illegal move raises immediately, at the line that tried it.
    The eleven impossible combinations become unspellable.

YOUR TASK (25 min)
    1. Fill in TRANSITIONS - state -> the states it may go to.
    2. _to(target, reason) - legal? record it in history, then move. Illegal?
       raise IllegalTransition.
    3. submit, confirm, complete, cancel - each one hop.
    4. confirm() also needs a GUARD: you cannot confirm without payment.
       Notice this does NOT belong in the table. The table says whether a hop
       is legal in principle; the guard says whether it is legal right now,
       for this enrolment. Two different questions.
    5. Write the six remaining checks at the bottom.

    history must be appended by the same method that moves the state. If
    recording is a separate call, someone will forget it - and the one time
    it matters is the one time it was forgotten.

THE COST
    The table is now a thing you maintain, and real business rules are
    messier than a table. The day you find yourself adding a sixth state
    called CONFIRMED_BUT_PENDING_REVIEW, that is the smell.
"""
from check import check, check_raises


class IllegalTransition(Exception):
    pass


class Enrolment:
    TRANSITIONS = {
        # TODO: fill this in. DRAFT can go to SUBMITTED or CANCELLED, etc.
    }

    def __init__(self, student, course):
        self.student = student
        self.course = course
        self.state = "DRAFT"
        self.paid = False
        self.history = []

    def submit(self, reason="submitted by student"):
        raise NotImplementedError    # TODO

    def pay(self):
        self.paid = True

    def confirm(self, reason="confirmed by office"):
        raise NotImplementedError    # TODO: guard on self.paid

    def complete(self, reason="course finished"):
        raise NotImplementedError    # TODO

    def cancel(self, reason):
        raise NotImplementedError    # TODO

    def _to(self, target, reason):
        # TODO: legal? record {"from","to","reason"} in history, then move.
        raise NotImplementedError


if __name__ == "__main__":
    print("SESSION 14 - state machine")

    # ---- STEP 2: the check the boolean version could never pass ----------
    check_raises("cannot confirm a draft", IllegalTransition,
                 Enrolment("s002", "c01").confirm)

    # YOUR TURN - write one check for each, then make them pass.
    # The two easy ones first, so you have a floor to stand on:
    #   starts as draft       a fresh Enrolment's .state
    #   happy path            submit, pay, confirm, complete -> .state
    #
    # Then the three that are each a bug a real system has shipped:
    #   cannot confirm without payment
    #       submit, then confirm with no pay(). This is the GUARD.
    #   cannot confirm after cancelling
    #       submit, cancel, confirm. Somewhere out there is an enrolment
    #       that is both cancelled and confirmed.
    #   history explains how we got here
    #       after cancel("student withdrew"), the last history entry's
    #       reason. You cannot bolt this on afterwards - either the moves
    #       recorded themselves as they happened, or the information is gone.
    #   history has the first hop
    #       e.history[0]["to"]. Decide your entry shape first; this just
    #       holds you to it.
