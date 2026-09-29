"""SESSION 14 - State machine.

    python 14_state_machine.py

THE PAIN
    Four booleans: is_submitted, is_confirmed, is_cancelled, is_paid. That is
    16 combinations, about 5 of them legal. Somewhere in a real system there is
    an enrolment that is both cancelled and confirmed and nobody knows how.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Before any code: on the board, list the four booleans and count
            the combinations. 2^4 = 16. Now cross out the ones that are
            nonsense - cancelled AND confirmed, paid but not submitted.
            About five survive.
            WHY COUNT FIRST: you have just measured the bug surface. Eleven
            states that should not exist, all reachable, none of them
            rejected by anything. The fix is not "be careful with the
            booleans" - it is to make the eleven UNSPELLABLE.

    STEP 2  Write the illegal-transition check before the table exists:
                check_raises("cannot confirm a draft", IllegalTransition,
                             Enrolment("s002", "c01").confirm)
            WHY THIS ONE FIRST: it is the check the boolean version cannot
            pass at all. A bool has no opinion about what came before it.

    STEP 3  Fill in TRANSITIONS as a dict of state -> allowed next states.
            WHY A DICT AND NOT if/elif IN EACH METHOD: the rules end up in
            ONE place you can read in ten seconds and show to the registrar,
            who does not read Python but does know whether a cancelled
            enrolment may be confirmed. A table is a conversation you can
            have with a non-programmer.

    STEP 4  _to() checks the table, appends to history, then moves.
            WHY HISTORY IS APPENDED BY THE SAME METHOD THAT MOVES: if
            recording is a separate call, someone will forget it, and the
            one time it matters is the one time it was forgotten. Make the
            audit trail impossible to skip by making it the same line.

    STEP 5  Add the payment guard to confirm(), and notice it is NOT in the
            table.
            WHY IT CANNOT BE: the table answers "is this hop legal in
            principle". The guard answers "is it legal right now, for this
            enrolment". Two different questions. When people try to encode
            the second one in the table, that is when you get a state called
            CONFIRMED_BUT_PENDING_REVIEW.

YOUR JOB (25 min)
    Replace the booleans with ONE state plus an explicit transition table.
    1. DRAFT, SUBMITTED, CONFIRMED, CANCELLED, COMPLETED
    2. An illegal transition raises IllegalTransition - loudly, immediately
    3. history records every transition with a reason
    STRETCH: a guard - CONFIRMED requires payment first.

THE TWIST
    "How did enrolment 4471 end up cancelled?" Your history answers it. The
    boolean version cannot.

THE DOWNSIDE
    The table is now a thing you must maintain, and real business rules are
    messier than a table. When you find yourself adding a sixth state called
    CONFIRMED_BUT_PENDING_REVIEW, that is the smell.
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

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    # Start with the two easy ones so you have a floor to stand on:
    #
    #   "starts as draft"    a fresh Enrolment's .state
    #   "happy path"         submit, pay, confirm, complete -> .state is ?
    #
    # Then the three that are actually the point. Each one is a bug that a
    # real registration system has shipped:
    #
    #   "cannot confirm without payment"
    #       submit, then confirm with no pay(). This is the GUARD, not the
    #       table - a legal hop that is still refused right now.
    #
    #   "cannot confirm after cancelling"
    #       submit, cancel, confirm. Somewhere out there is an enrolment
    #       that is both cancelled and confirmed. This is the check that
    #       makes it impossible here.
    #
    #   "history explains how we got here"
    #       after cancel("student withdrew"), the last history entry's
    #       reason. THIS is the check that answers the dean's question in
    #       the twist. Notice you cannot bolt it on afterwards - either the
    #       transitions recorded themselves as they happened, or the
    #       information is simply gone.
    #
    #   "history has the first hop"
    #       e.history[0]["to"]. Decide your own history entry shape first;
    #       this check just holds you to it.
    #
    # STRETCH: what stops someone assigning e.state = "CONFIRMED" directly?
    #          Nothing. Write a check that catches it, then make it pass.
