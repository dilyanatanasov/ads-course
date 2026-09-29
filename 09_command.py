"""SESSION 09 - Command.

    python 09_command.py

THE IDEA IN ONE LINE
    Stop calling the action. Build an object that REPRESENTS the action, then
    decide later when - or whether - to run it.

    Once an action is an object you get undo, retry, queueing and audit almost
    for free. This is the pattern behind every task queue you will ever use.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Write the undo check first:
                bus.run(RegisterCommand(store, "s001", "c01"))
                bus.undo_last()
                check("undo", ("s001", "c01") in store.rows, False)
            WHY UNDO FIRST: undo is the requirement that makes an object
            necessary. A function can register a student. Only an object can
            remember ENOUGH to take it back. Write this check first and the
            design is forced; write it last and you will wonder all session
            why we did not just call a function.

    STEP 2  RegisterCommand.execute() adds, undo() removes.
            WHY THE COMMAND HOLDS store AND the arguments: it has to be
            runnable LATER, by someone who was not there when it was
            created. That is what turns it into something you can queue,
            retry, log or ship across a network - and it is exactly what
            session 23 does with it.

    STEP 3  CommandBus.run() calls execute() and appends to history.
            WHY THE BUS OWNS HISTORY AND NOT THE COMMAND: one command knows
            about itself. Only the bus sees the ORDER. "What did we do last
            night" is a question about order.

    STEP 4  Add attempts. Wrap execute() in a loop with try/except.
            WHY RETRY LIVES HERE AND NOT IN THE COMMAND: put it in
            RegisterCommand and you write it again in CancelCommand, and in
            every command anyone adds for the next three years. The bus is
            the one place that sees every command, so it is the one place a
            cross-cutting rule belongs. Hold that thought until session 13.

    STEP 5  Ask the room: `bus.run(Flaky(), attempts=3)` retries three times.
            What if execute() already charged a card before it failed?
            Nobody has to solve it today - but everyone should feel it.
            Session 23 is where it comes back with a name.

YOUR JOB (25 min)
    1. RegisterCommand and CancelCommand with execute() and undo().
    2. CommandBus with run(), undo_last() and a history list.
    3. run(command, attempts=3) retries on exception.
    STRETCH: redo().

THE TWIST
    The dean asks "what did we do last night?" With commands that is
    bus.history. Without them it does not exist.

THE DOWNSIDE
    Every action now needs a class. A one-line operation became fifteen lines.
    Use this when you need undo/retry/audit. Not because it looks professional.
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

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    #   "history is an audit trail"
    #       run a RegisterCommand and then a CancelCommand, and check
    #       len(bus.history). Decide first: does undo_last() REMOVE the entry
    #       from history, or is undoing itself part of the history? Both are
    #       defensible. Your check has to say which one you chose.
    #
    #   "retried until it worked"
    #       define a Flaky command down here that raises the first two times
    #       and succeeds on the third. Count the calls in a dict - `calls =
    #       {"n": 0}` - not a plain int, or the closure will fight you.
    #       Run it with attempts=3 and check the count.
    #       WHY A FAKE AND NOT A REAL FAILURE: you cannot make a real network
    #       fail twice and then work, on demand, in a classroom. A fake that
    #       fails on schedule is the only way to check retry logic at all -
    #       and it only works because run() takes any object with execute().
    #       That is session 02's seam, paying off.
    #
    # STRETCH: redo(). Write the check first and the API will design itself.
