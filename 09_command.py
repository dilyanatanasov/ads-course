"""SESSION 09 - Command.

    python 09_command.py

THE SITUATION
    The dean asks what the office did last night, and which of it can be
    undone. Nobody can answer, because the office called functions, and
    functions leave no trace.

THE IDEA
    Stop calling the action. Build an OBJECT that represents the action, then
    decide later when - or whether - to run it.

    Once an action is an object you get undo, retry, queueing and an audit
    trail almost for free. This is the pattern behind every task queue you
    will ever use, and session 23 puts one on disk.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. RegisterCommand and CancelCommand, each with execute() and undo().
    2. CommandBus.run(command) - execute it, record it in history.
    3. CommandBus.undo_last().
    4. run(command, attempts=3) - retry on exception.
    5. Write the two remaining checks at the bottom.

    Undo is the requirement that makes an object necessary. A function can
    register a student; only an object can remember enough to take it back.

    Retry belongs on the BUS, not in the commands. The bus is the one place
    that sees every command, so it is where a rule affecting all of them
    goes. Hold that thought until session 13.

THE COST
    Every action now needs a class. A one-line operation became fifteen
    lines. Use this when you need undo, retry or audit - not because it looks
    professional.
"""
from check import check


class Enrolments:
    def __init__(self):
        self.rows = set()


class RegisterCommand:
    def __init__(self, store, student, course):
        self.store, self.student, self.course = store, student, course

    def execute(self):
        raise NotImplementedError    # TODO

    def undo(self):
        raise NotImplementedError    # TODO


class CancelCommand:
    def __init__(self, store, student, course):
        self.store, self.student, self.course = store, student, course

    def execute(self):
        raise NotImplementedError    # TODO

    def undo(self):
        raise NotImplementedError    # TODO


class CommandBus:
    def __init__(self):
        self.history = []

    def run(self, command, attempts=1):
        raise NotImplementedError    # TODO: retry, then record in history

    def undo_last(self):
        raise NotImplementedError    # TODO


if __name__ == "__main__":
    print("SESSION 09 - command")
    store, bus = Enrolments(), CommandBus()

    # ---- STEP 1: the pair of checks we wrote first ------------------------
    # execute then undo. Written together, because "it ran" is only half a
    # claim - undo is what the object exists for.
    bus.run(RegisterCommand(store, "s001", "c01"))
    check("execute", ("s001", "c01") in store.rows, True)

    bus.undo_last()
    check("undo", ("s001", "c01") in store.rows, False)

    # YOUR TURN - write one check for each, then make them pass:
    #   history is an audit trail
    #       run a RegisterCommand then a CancelCommand, check
    #       len(bus.history). Decide first: does undo_last() remove the
    #       entry, or is undoing itself part of the history? Either is
    #       defensible - your check says which you chose.
    #
    #   retried until it worked
    #       define a Flaky command down here that raises the first two
    #       times and succeeds on the third. Count the calls in a dict -
    #       calls = {"n": 0} - not a plain int, or the closure fights you.
    #       Run it with attempts=3.
