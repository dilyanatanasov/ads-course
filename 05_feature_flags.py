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

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Write this check first, and read it carefully before typing:
                flags.set("new_grading", True)
                check("flag on, same object", book.grade("s001", 73), "73%")
            Note "same object" - the Gradebook was built BEFORE the flag was
            set, and we never rebuild it.
            WHY THAT PHRASE IS THE ENTIRE SESSION: it forces you to read the
            flag on every call instead of once in __init__. Both designs pass
            a naive check. Only one of them can be changed by someone who is
            not you, at 7am, without a deploy.

    STEP 2  FeatureFlags: a dict, a set(), and an is_on(). Start with True and
            False only.
            WHY AN OBJECT AND NOT A GLOBAL DICT: because in a minute is_on()
            has to do real work, and because a global that changes is session
            07 arriving early.

    STEP 3  Gradebook.strategy_for(student_id) asks the flags, then grade()
            delegates. Run it.
            WHY strategy_for IS ITS OWN METHOD: you can ask "which rule would
            this student get?" without grading anybody. Session 04's downside
            was that you could not answer that question. This is the smallest
            possible fix.

    STEP 4  Now an unknown flag. What should is_on("nonsense") do?
            WHY IT MUST BE False: a typo in a config file must switch the new
            thing OFF, never on. Default to the behaviour that was already
            working. You will meet this rule again as "fail safe", and it is
            the difference between a quiet non-event and an incident.

    STEP 5  The rollout. A flag can also be {"percent": 10} - on for a tenth
            of students. Write bucket_of() together, and START with the
            obvious version:
                return hash(subject) % 100
            Run the file twice, in two separate processes. The buckets CHANGE.
            WHY: Python randomises string hashing per process, on purpose, to
            defend against a denial-of-service attack. Which means two web
            servers put the same student in different buckets - the feature
            flickers on and off depending on which machine answered.
            Try it yourself, it takes three seconds:
                python -c "print(hash('s001') % 100)"
            Now use hashlib.sha256 instead and run it twice more. Stable.
            THE LESSON, and it is bigger than today: "it worked on my
            machine" and "it works" are different claims, and the gap between
            them is usually something you assumed was deterministic.

YOUR JOB (25 min)
    1. FeatureFlags.is_on(name, subject=None) - True/False flags first.
    2. Gradebook reads the flag on EVERY call.
    3. Unknown flag -> off.
    4. Percentage rollouts with a stable bucket_of().

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
        raise NotImplementedError    # TODO: ask the flags. On EVERY call.

    def grade(self, student_id, score):
        raise NotImplementedError    # TODO


if __name__ == "__main__":
    print("SESSION 05 - feature flags")
    flags = FeatureFlags()
    book = Gradebook(flags, current=BulgarianScale(), candidate=Percentage())

    # ---- STEP 1: the check we wrote first ---------------------------------
    # The Gradebook above was built BEFORE this line runs, and is never
    # rebuilt. If you read the flag in __init__, this cannot pass.
    flags.set("new_grading", True)
    check("flag on, same object", book.grade("s001", 73), "73%")

    # ---- NOW YOU WRITE THE REST -------------------------------------------
    #   "unknown flag is off"
    #       a fresh FeatureFlags() with nothing set. Grading s001 on 73 must
    #       give you the OLD rule. Work out that string from BulgarianScale
    #       yourself - do not copy it from session 04 without checking.
    #
    #   "flipped back with no restart"
    #       set the flag to False on the SAME objects and grade again. This
    #       is the 7am phone call, and it is the check that proves you can
    #       answer it.
    #
    #   "0 percent reaches nobody" / "100 percent reaches everybody"
    #       set {"percent": 0}, then {"percent": 100}, and check across 200
    #       students - f"s{i:03d}" for i in range(200). Use any() and all().
    #       WHY BOTH ENDS: they are the two cases a rollout must never get
    #       wrong. 1% leaking to everyone is an incident; 99% reaching nobody
    #       is a silent non-launch, which is worse because nobody notices.
    #
    #   "same student, same answer, every time"
    #       at {"percent": 50}, grade s001 fifty times and check every answer
    #       matches the first. A student must not flip rules mid-semester.
    #       Then run the whole FILE twice and check s001 got the same rule
    #       BOTH TIMES - that one is not automatable here, and it is the bug.
    #
    #   "50 percent splits the cohort"
    #       count how many of the 200 got the new rule, and check it is
    #       roughly half - say 70 < rolled < 130.
    #       WHY A RANGE AND NOT AN EXACT NUMBER: a hash is not a shuffle. It
    #       will not give you exactly 100, and a check demanding exactly 100
    #       would be asserting an accident. Check the property you actually
    #       care about, not the number you happened to observe.
    #
    # STRETCH: add a per-faculty flag - on for law, off for everyone else.
    #          Then work out what happens when a student is in the 50%
    #          rollout AND their faculty flag is off. You now have two flags
    #          and four paths. Feel how fast that got complicated.
