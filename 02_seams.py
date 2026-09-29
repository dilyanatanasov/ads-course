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

BUILD IT TOGETHER (15 min - we do this on the projector, you type along)
    Run it before changing anything:   python 02_seams.py
    One check passes, one fails.

    STEP 1  Find this line inside register():

                now = datetime.now()

            The deadline is March 2030. Your computer says it is not 2030.
            So `now` is always before the deadline, and the `raise` line
            underneath CANNOT RUN on any machine in this room.

            That line is not untested. It is UNREACHABLE. And there is no
            argument you can pass to reach it - look at __init__, it accepts
            a `clock` and then ignores it.

    STEP 2  Make the clock come from outside. Two lines.

            In __init__, replacing the comment:

                self.clock = clock or datetime.now

            In register(), replacing the datetime.now() line:

                now = self.clock()

            The brackets are the whole trick. `datetime.now` without them is
            the function itself, which you can store in a variable and call
            later. `datetime.now()` with them runs it now. So line one parks
            a function; line two calls whatever got parked.
            `or` means "use theirs if they gave one, otherwise the real
            clock" - which is why nothing that already used this class breaks.

            Run it. Both checks green.

            THEN ANSWER THIS: what did you change about what the program
            DOES? Nothing. A student registering tomorrow gets identical
            behaviour. What changed is what YOU can reach from outside.
            You did not write a better test - you stopped the design from
            making the test impossible.

    STEP 3  Same move for the message: print() becomes self.notify().
            print() is a one-way door - it throws the text at the screen
            where no code can pick it up again. A function parameter keeps it
            a value you can look at.

    STEP 4  Same move for the fee. You should be able to predict the shape
            before you read the hint. If you can, you have the pattern - and
            the pattern, not the three parameters, is the point of today.

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

    # ---- WE WRITE THESE TWO TOGETHER -------------------------------------
    # Run the file before you change anything. One of these passes and one
    # fails, and the one that PASSES is the more interesting of the two.
    #
    # It passes because the deadline is in 2030 and your computer says it is
    # not 2030 yet, so registration is open. It would pass against literally
    # any code. Come back in 2030 and it starts failing on its own.
    #
    # That is a check that is green for a reason that has nothing to do with
    # your program being right - and you cannot tell the difference from the
    # outside. Keep it in mind every time you see a green line today.
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
    #       You need somewhere for the message to land, so start with an
    #       empty list:   sent = []
    #       Then build a Registration with notify=sent.append - a list's
    #       .append IS a function, so it fits exactly where print() fitted.
    #       Register Maria, then check `sent` holds exactly:
    #           ["Dear Maria, you are registered for Databases."]
    #       Maria's message will not appear on screen. That is the proof.
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
