"""SESSION 05 - Strategy II: feature flags.

    python 05_feature_flags.py         the checks
    python 05_feature_flags.py demo    every flag state, side by side

THE PAIN
    Session 04 gave you interchangeable grading rules. But you still chose one
    IN CODE - `Gradebook(BulgarianScale())` - which means changing your mind
    means editing a file, committing it, and deploying.

    The registrar wants the new percentage scale tried on a few students from
    Monday. If it goes wrong she wants it off by Tuesday morning. She is not
    going to wait for a release, and she is not going to phone you at 7am.

    A rule you can swap but not swap AT RUNTIME is only half a strategy.

WHAT A FEATURE FLAG ACTUALLY IS
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

    2. bucket_of() must give the SAME answer in every process. Write it with
       hash(subject) % 100 first and watch the last check fail - then run:

           python -c "print(hash('s001') % 100)"

       twice, and see why. Python randomises string hashing per process, so
       two servers would put the same student in different buckets and the
       feature would flicker on and off depending on which one answered.
       Use hashlib instead. "It worked on my machine" and "it works" are
       different claims.

THE TWIST
    The registrar phones: turn it off. You change one line of config. No
    deploy, no restart, no commit. Compare that with session 01, where
    "change the grading rule" meant editing an if/elif chain.

THE DOWNSIDE - and this one is not really about code
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
import hashlib
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


def bucket_of(subject, salt=""):
    """A 0-99 bucket for this subject. Must be the SAME in every process.

    Start with hash(subject) % 100, run the file twice, and watch it change.
    Then fix it with hashlib.
    """
    raise NotImplementedError    # TODO


class FeatureFlags:
    """Config, not code. A flag is True, False, or {"percent": n}."""

    def __init__(self, flags=None):
        self._flags = dict(flags or {})

    def set(self, name, value):
        self._flags[name] = value

    def is_on(self, name, subject=None):
        # A flag is one of three things. Handle them in this order:
        #   never set        -> False   (a typo in config must mean OFF)
        #   True or False    -> itself
        #   {"percent": n}   -> bucket_of(subject, name) < n
        # No special case for 0 or 100 - work out why not. Buckets are 0-99.
        raise NotImplementedError


class Gradebook:
    def __init__(self, flags, current, candidate):
        self.flags = flags
        self.current = current
        self.candidate = candidate

    def strategy_for(self, student_id):
        # TODO: ask self.flags whether NEW_GRADING is on for this student.
        # On -> self.candidate. Off -> self.current. Ask on EVERY call.
        raise NotImplementedError

    def grade(self, student_id, score):
        # TODO: two lines. Get the strategy from strategy_for(student_id),
        # then ask THAT object to grade the score. Note this method uses
        # student_id for nothing except choosing the rule - once you have
        # the rule, it only needs a number.
        raise NotImplementedError


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
        print(f"      {sid}  bucket {bucket_of(sid, NEW_GRADING):>2}  "
              f"-> {book.grade(sid, 73)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
        raise SystemExit

    print("SESSION 05 - feature flags")
    flags = FeatureFlags()
    book = Gradebook(flags, current=BulgarianScale(), candidate=Percentage())

    # ---- STEP 1: the check we wrote first ---------------------------------
    # The Gradebook above was built BEFORE this line runs, and is never
    # rebuilt. If you read the flag in __init__, this cannot pass.
    flags.set(NEW_GRADING, True)
    check("flag on, same object", book.grade("s001", 73), "73%")

    # YOUR TURN - two checks, then make them pass:
    #   unknown flag is off             a FRESH FeatureFlags, nothing set,
    #                                   grade s001 on 73 -> the OLD rule
    #   flipped back with no restart    set it False on the SAME objects and
    #                                   grade again. This is the 7am phone call.

    # ---- GIVEN, and it is the point of the session -------------------------
    # 56 is not a number from your machine. It is the number from every
    # machine, forever, because sha256 gives the same answer in every process.
    # A rollout only means something if all your servers agree who is in it.
    #
    # This CANNOT pass with hash(). Write bucket_of with hash() first, run it
    # twice, and watch the number change. Then look up hashlib.
    flags.set(NEW_GRADING, {"percent": 30})
    rolled = sum(1 for i in range(200)
                 if book.grade(f"s{i:03d}", 73) == "73%")
    check("30 percent rolls out the same way on every machine", rolled, 56)
    print(f"        (rolled out to {rolled} of 200)")
