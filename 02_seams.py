"""SESSION 02 - Seams.

    python 02_seams.py

A SEAM is a place where you can change what the code does without editing the
code. Last week's monolith has almost none, which is why the change requests
hurt.

THE PAIN
    Registration below hardcodes three things:
      1. WHEN it is - datetime.now() is baked into the method
      2. WHERE output goes - print()
      3. WHAT the fee rule is - a literal 120

    Consequence: the registration deadline is UNVERIFIABLE. To find out what
    happens after 1 March you would have to change your computer's clock.
    That is not a joke - people really do this.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    We write the CHECK first, every time, and the reason is not discipline.
    It is that the check is impossible to write against the current code, and
    finding that out is how you discover the design is wrong.

    STEP 1  Try to write the first check: "registration is closed on 2 March".
            Go on. Try.
            WHY THIS STEP EXISTS: you cannot. There is no way to tell this
            class what day it is. The only way to run that line is to change
            your computer's clock. The check did not fail - it could not be
            WRITTEN. That is the difference between a bug and a design
            problem, and it is the whole of today.

    STEP 2  Now make it writable. `clock` becomes a constructor parameter,
            and register() calls self.clock() instead of datetime.now().
            WHY A DEFAULT: `clock=None` -> `self.clock = clock or datetime.now`
            means every existing caller keeps working untouched. A seam you
            have to update 40 call sites for is a seam nobody opens.
            Run it. The first check goes green, and it is now a check you
            could not have had at all five minutes ago.

    STEP 3  Same move for output. `notify` replaces print().
            WHY: print() is a one-way door - it throws the message away where
            no code can reach it. A function parameter keeps the message a
            VALUE. `notify=sent.append` and suddenly the message is in a list
            you can look at. Nothing about the program changed; everything
            about what you can observe did.

    STEP 4  Same move for the fee. `fee_rule` takes the course, returns leva.
            WHY LAST: by now you should be able to predict the shape before I
            type it. If you can, you have the pattern.

YOUR JOB (25 min)
    Finish the checks listed at the bottom, then make them pass.
      1. clock    - a function returning "now". Defaults to datetime.now.
      2. notify   - a function taking a string. Defaults to print.
      3. fee_rule - a function taking a course dict, returning leva.

    Nothing about the behaviour changes. Everything about what you can OBSERVE
    changes.

THE TWIST
    With a fake clock you can ask "what happens on 2 March?" in 0.001 seconds.
    Without one, you cannot ask it at all. Feature flags, A/B tests, staging
    environments and every test suite on earth are built out of seams.

THE DOWNSIDE - the real one
    Every seam is another parameter. A class with nine injected collaborators
    is its own kind of unreadable, and you will meet one. The rule of thumb:
    open a seam where the thing is genuinely OUT OF YOUR CONTROL - time,
    randomness, the network, the filesystem, the user - not everywhere you
    could.
"""
from datetime import datetime
from check import check, check_raises

DEADLINE = datetime(2030, 3, 1)


class Registration:
    def __init__(self, clock=None, notify=None, fee_rule=None):
        # TODO: keep these, give them sensible defaults, and USE them below.
        # Right now they are accepted and ignored - so the checks run, and
        # every one of them fails. That is your to-do list.
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

    # ---- STEP 1+2: seam 1, the fake clock. WE WRITE THESE TOGETHER ------
    # Read these two and notice what they buy you: the deadline is now a
    # thing you can ASK ABOUT, in a millisecond, without touching a clock.
    before = Registration(clock=lambda: datetime(2030, 2, 20))
    check("open before the deadline", before.register("Ivan", course), True)

    after = Registration(clock=lambda: datetime(2030, 3, 2))
    check_raises("closed after the deadline", ValueError,
                 after.register, "Ivan", course)

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    # Four behaviours. Write the check FIRST, watch it fail, then open the
    # seam that makes it pass. If a check looks impossible to write, that is
    # the point - it means the seam is still missing. Say so out loud.
    #
    # seam 2 - capture output instead of printing it
    #   "notification captured, not printed"
    #       build a Registration with notify=sent.append, register Maria,
    #       and check `sent` holds exactly:
    #           ["Dear Maria, you are registered for Databases."]
    #
    # seam 3 - swap the pricing rule from outside
    #   "fee rule swapped without editing register()"
    #       pass fee_rule=lambda c: c["credits"] * 25, register Georgi,
    #       and check `.charged`. Work out the number yourself first -
    #       the course is 6 credits.
    #
    # and the defaults must still work
    #   "defaults are still sensible"
    #       Registration() with no arguments at all should still have a
    #       callable fee_rule. WHY THIS CHECK EARNS ITS PLACE: it is the one
    #       that catches you breaking every existing caller.
    #
    # STRETCH: write a check that proves the default clock is the REAL clock,
    #          without waiting for March. Harder than it sounds - discuss.
