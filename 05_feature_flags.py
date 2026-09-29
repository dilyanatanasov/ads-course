"""SESSION 05 - Strategy II: feature flags.

    python 05_feature_flags.py

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

    2. bucket_of() must give the SAME answer in every process. Start with the
       obvious version, hash(subject) % 100, then run this twice:

           python -c "print(hash('s001') % 100)"

       Two different numbers. Python randomises string hashing per process,
       so two servers would put the same student in different buckets and the
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
        # TODO: missing -> False. True/False -> itself.
        # {"percent": n} -> bucket_of(subject, name) < n
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
        raise NotImplementedError    # TODO


if __name__ == "__main__":
    print("SESSION 05 - feature flags")
    flags = FeatureFlags()
    book = Gradebook(flags, current=BulgarianScale(), candidate=Percentage())

    # ---- STEP 1: the check we wrote first ---------------------------------
    # The Gradebook above was built BEFORE this line runs, and is never
    # rebuilt. If you read the flag in __init__, this cannot pass.
    flags.set(NEW_GRADING, True)
    check("flag on, same object", book.grade("s001", 73), "73%")

    # YOUR TURN - write one check for each, then make them pass:
    #   unknown flag is off             nothing set -> the OLD rule
    #   flipped back with no restart    set it False on the SAME objects
    #   0 percent reaches nobody        {"percent": 0}, across 200 students
    #   100 percent reaches everybody   {"percent": 100}
    #   same student, same answer       at 50%, grade s001 fifty times
    #   50 percent splits the cohort    count of 200 - check a RANGE, not an
    #                                   exact number. A hash is not a shuffle.
    #
    # The 200 students are f"s{i:03d}" for i in range(200).
