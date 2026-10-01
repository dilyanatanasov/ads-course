"""SESSION 05 - Strategy II: feature flags.

    python 05_feature_flags.py         the checks
    python 05_feature_flags.py demo    every flag state, side by side

THE SITUATION
    Session 04 gave you interchangeable grading rules. But you still chose one
    IN CODE - `Gradebook(BulgarianScale())` - which means changing your mind
    means editing a file, committing it, and deploying.

    The registrar wants the new percentage scale tried on a few students from
    Monday. If it goes wrong she wants it off by Tuesday morning. She is not
    going to wait for a release, and she is not going to phone you at 7am.

    A rule you can swap but not swap AT RUNTIME is only half a strategy.

THE IDEA
    A strategy chosen from configuration instead of from code. That is the
    whole idea. Every "feature flag platform" you will ever be sold is this,
    plus a web page to edit the config and a bill.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL lines, because the methods below
    raise NotImplementedError until you write them. The last line of the
    traceback names the method to start with.

THE GOAL
    Make the grading rule changeable WHILE THE PROGRAM IS RUNNING.

    Two things decide whether you got it right, and both are easy to miss.

    1. Read the flag inside strategy_for(), on EVERY call - not in __init__.
       Read it once at construction and the only way to change a flag is to
       restart, which is the one thing a flag exists to avoid.

    2. Pass the STUDENT to is_on(). A 30 percent rollout is decided per
       student: bucket_of() turns a student id into a number from 0 to 99,
       and the student is in if that number is below 30. It cannot be
       random - the same student must get the same answer every time they
       ask. hash(subject) % 100 is enough.

       One thing to know, not to fix today: Python's hash() of a string
       changes each time the program starts, so the rollout count moves
       from run to run. Real systems use a hash that never changes.

THE TWIST
    The registrar phones: turn it off. You change one line of config. No
    deploy, no restart, no commit. Compare that with session 01, where
    "change the grading rule" meant editing an if/elif chain.

THE COST - and this one is not really about code
    Every flag DOUBLES your number of code paths. Two flags is four
    combinations and you are testing one of them. Flags are debt with an
    expiry date: a flag still in the codebase a year after the rollout
    finished is a bug that has not happened yet.

    And the part that is not technical at all. A 50% rollout means two
    students in the same seminar, with the same score, got graded by
    different rules. That is fine for a button colour. Is it fine for a
    grade? Nobody in this room can answer that with code, and that is
    precisely why you must ask before you ship it.
"""
import sys
from abc import ABC, abstractmethod
from check import check

# The one flag this session uses. A NAME, not a magic string typed out in
# several places - because a typo in a flag name is a flag that silently
# never turns on, and nothing will tell you.
NEW_GRADING = "new_grading"


class GradingStrategy(ABC):
    @abstractmethod
    def grade(self, score):
        ...


class BulgarianScale(GradingStrategy):
    """From session 04. Unchanged - that is rather the point."""

    def __init__(self, pass_mark=50):
        self.pass_mark = pass_mark

    def grade(self, score):
        if score < self.pass_mark:
            return "2 (Poor)"
        band = (100 - self.pass_mark) / 4
        if score < self.pass_mark + band:
            return "3 (Satisfactory)"
        if score < self.pass_mark + 2 * band:
            return "4 (Good)"
        if score < self.pass_mark + 3 * band:
            return "5 (Very good)"
        return "6 (Excellent)"


class Percentage(GradingStrategy):
    def grade(self, score):
        return f"{round(score)}%"


def bucket_of(subject):
    """Turn a student id into a number from 0 to 99 - their "bucket".

    The same student must always get the same bucket, so it cannot be random.
    """
    # HINT: one line. hash(subject) turns the id into a big number;
    # % 100 cuts that down to 0-99.
    raise NotImplementedError    # TODO


class FeatureFlags:
    """Config, not code. A flag is True, False, or {"percent": n}."""

    def __init__(self, flags=None):
        self._flags = dict(flags or {})

    def set(self, name, value):
        self._flags[name] = value

    def is_on(self, name, subject=None):
        """Is the flag called `name` on for this subject (a student id)?"""
        # HINT: look the flag up with self._flags.get(name). You get back one
        # of three things - handle them in this order:
        #
        #   1. None              nobody set this flag, or the name is
        #                        misspelled. Return False - unknown means OFF.
        #   2. True or False     return it as it is.
        #                        isinstance(rule, bool) tells you it is one.
        #   3. {"percent": 30}   return bucket_of(subject) < rule["percent"]
        #
        # Buckets are 0-99, so 0 percent is nobody and 100 percent is
        # everybody. Case 3 needs nothing extra for them.
        raise NotImplementedError    # TODO


class Gradebook:
    def __init__(self, flags, current, candidate):
        self.flags = flags
        self.current = current
        self.candidate = candidate

    def strategy_for(self, student_id):
        """Which grading rule does this student get right now?"""
        # HINT: one if. Ask self.flags.is_on(NEW_GRADING, student_id).
        #   on   -> return self.candidate    the new rule
        #   off  -> return self.current      the rule that already works
        #
        # Ask HERE, every time this method is called - not once in __init__.
        # And pass student_id, or a percentage cannot tell students apart.
        raise NotImplementedError    # TODO

    def grade(self, student_id, score):
        """Grade one score with whichever rule this student gets."""
        # HINT: two lines.
        #   1. get the rule from self.strategy_for(student_id)
        #   2. return what that rule's grade(score) gives back
        raise NotImplementedError    # TODO


def demo():
    """Show how each flag STATE changes what one student sees.

    python 05_feature_flags.py demo
    """
    print("One student - s001 - with a score of 73. Only the FLAG changes.")
    print()
    print(f"  {'FLAG STATE':<26} {'is_on':<7} {'RULE':<16} SEES")
    print("  " + "-" * 62)

    cases = [
        ("never set (absent)",      "absent"),
        ("set to False",            False),
        ("set to True",             True),
        ('{"percent": 30}',         {"percent": 30}),
        ("name misspelled in config", "typo"),
    ]

    for label, value in cases:
        flags = FeatureFlags()
        if value == "typo":
            flags.set("new_gradng", True)          # one letter missing
        elif value != "absent":
            flags.set(NEW_GRADING, value)

        book = Gradebook(flags, current=BulgarianScale(),
                         candidate=Percentage())
        on = flags.is_on(NEW_GRADING, "s001")
        rule = type(book.strategy_for("s001")).__name__
        print(f"  {label:<26} {str(on):<7} {rule:<16} {book.grade('s001', 73)}")

    print()
    print("  ABSENT and FALSE are indistinguishable from outside, on purpose.")
    print("  Both fall back to the rule that was already working. So does a")
    print("  misspelled flag name - which is why that typo is so dangerous:")
    print("  nothing breaks, the new feature simply never happens, and no")
    print("  error is ever printed.")
    print()

    flags = FeatureFlags({NEW_GRADING: {"percent": 30}})
    book = Gradebook(flags, current=BulgarianScale(), candidate=Percentage())
    print("  At 30 percent, the SAME flag gives different students different")
    print("  rules - and the same student always gets the same one:")
    for sid in ("s001", "s002", "s003", "s004", "s005"):
        print(f"      {sid}  bucket {bucket_of(sid):>2}  "
              f"-> {book.grade(sid, 73)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
        raise SystemExit

    print("SESSION 05 - feature flags")
    flags = FeatureFlags()
    book = Gradebook(flags, current=BulgarianScale(), candidate=Percentage())

    # One student, one score, one book. Only the flag changes.
    # A score of 73 is "4 (Good)" on the old rule and "73%" on the new one.

    # ---- 1. nothing set yet: the old rule ----------------------------------
    # YOUR TURN: write a check called "unknown flag is off".
    # book.grade("s001", 73) should give "4 (Good)".

    # ---- 2. flag ON: the new rule (given) ----------------------------------
    # The book was built before this line and is never rebuilt. If you read
    # the flag in __init__, this cannot pass.
    flags.set(NEW_GRADING, True)
    check("flag on, same object", book.grade("s001", 73), "73%")

    # ---- 3. flag OFF again: the old rule is back ---------------------------
    # YOUR TURN: set the flag to False on the SAME flags object, then write a
    # check called "flipped back with no restart". The SAME book should give
    # "4 (Good)" again. This is the registrar's 7am phone call.

    # ---- 4. 30 percent: some students, not all (given) ---------------------
    # A percentage is decided one student at a time. If this says 0 or 200,
    # the flag is being asked without the student - everybody lands in the
    # same bucket and the rollout is all or nothing.
    flags.set(NEW_GRADING, {"percent": 30})
    rolled = sum(1 for i in range(200)
                 if book.grade(f"s{i:03d}", 73) == "73%")
    check("30 percent reaches some students, not all", 0 < rolled < 200, True)
    print(f"        (rolled out to {rolled} of 200 - about 60 is right)")
