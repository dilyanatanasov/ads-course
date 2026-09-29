"""SESSION 02 - Seams.

    python 02_seams.py

THE SITUATION
    Same registration system. Registration closes on 1 March 2030, and the
    code below refuses late registrations correctly.

THE PROBLEM
    You cannot prove it. Today is not 2030, so `now` is always before the
    deadline and the line that refuses a late registration NEVER RUNS. To see
    it work you would have to change your computer's clock. People really do
    this.

    Three decisions are made INSIDE register(), where no caller can reach
    them: what time it is, where the message goes, and what the fee is.

    A SEAM is a place where you can change what the code does without editing
    the code. This class has none. That is the whole problem.

YOUR TASK (25 min)
    Turn those three decisions into constructor parameters.

      1. clock      a function returning "now"        default: datetime.now
      2. notify     a function taking a string        default: print
      3. fee_rule   a function taking a course dict, returning leva

    Each one is ONE line in __init__ and ONE line in register().
    The behaviour must not change. Only what you can OBSERVE changes.

WE DO THE FIRST ONE TOGETHER
    In __init__:      self.clock = clock or datetime.now
    In register():    now = self.clock()

    No brackets on the first line - you are storing the function itself, to
    run later. Brackets on the second - there you do want to run it. `or`
    means "use theirs if they gave one, otherwise the real clock", which is
    why nothing that already used this class breaks.

    Run it. Both clock checks go green.

    Then answer: what did you change about what the program DOES? Nothing. A
    student registering tomorrow sees identical behaviour. You changed what
    you can REACH from outside - and that is what made the test possible.

THE COST
    Every seam is another parameter, and a class with nine of them is its own
    kind of unreadable. Open a seam for things genuinely outside your control
    - time, the network, the filesystem, money - not everywhere you could.
"""
from datetime import datetime
from check import check, check_raises

DEADLINE = datetime(2030, 3, 1)


class Registration:
    def __init__(self, clock=None, notify=None, fee_rule=None):
        # These three are accepted and then IGNORED. Read the method below -
        # nothing uses them. Making them real is your job today.
        self.registrations = []
        self.charged = []

    def register(self, student, course):
        now = datetime.now()                    # TODO: seam 1
        if now > DEADLINE:
            raise ValueError("registration closed on 1 March 2030")

        fee = 120                               # TODO: seam 3
        self.charged.append((student, fee))
        self.registrations.append((student, course))

        print(f"Dear {student}, you are registered for {course['title']}.")  # TODO: seam 2
        return True


if __name__ == "__main__":
    print("SESSION 02 - seams")
    course = {"id": "c01", "title": "Databases", "credits": 6}

    # Run this before changing anything. One passes, one fails - and the one
    # that PASSES only does so because it is not 2030 yet. It would pass
    # against any code at all. Green does not always mean correct.
    before = Registration(clock=lambda: datetime(2030, 2, 20))
    check("open before the deadline", before.register("Ivan", course), True)

    after = Registration(clock=lambda: datetime(2030, 3, 2))
    check_raises("closed after the deadline", ValueError,
                 after.register, "Ivan", course)

    # YOUR TURN - write one check for each, then make them pass:
    #   the message can be captured instead of printed
    #   the fee rule can be swapped from outside - 25 lv per credit
    #   Registration() with no arguments still works
    #
    # Each seam is one line in __init__ and one line in register().
