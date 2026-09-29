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
