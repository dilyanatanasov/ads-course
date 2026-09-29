"""SESSION 06 - Factory, and the question session 04 left open.

    python 06_factory.py

THE PAIN
    You have five strategies. Something must decide which one a student gets.
    Right now that decision is scattered - in a real project you would find
    `BulgarianScale(` in twelve files.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Write the LAST check first. Yes, the last one:
                GradingFactory.register("classics", Roman)
                check("a plugin this file never heard of",
                      GradingFactory.create("classics").grade(80), "V")
            WHY THE LAST ONE FIRST: it is the only check that an if/elif
            chain cannot pass. Write the easy checks first and you will
            "solve" today with an if/elif and never feel why a dict is
            different. Start with the requirement that rules out the wrong
            answer, and the right answer is the only one left.

    STEP 2  `_registry = {}` and register() puts a class in it.
            WHY STORE THE CLASS, NOT AN INSTANCE: two students must not share
            one BulgarianScale object - that is session 07's whole disaster,
            arriving a week early. The registry holds a recipe, create()
            cooks a fresh one each time.

    STEP 3  create() looks it up and calls it.
            WHY A BARE dict[key] AND NOT .get(): a missing faculty must
            EXPLODE. .get() returns None, which becomes "NoneType has no
            attribute grade" somewhere far away. Fail where the mistake is.

    STEP 4  Register the three faculties. Note engineering is BulgarianScale
            with pass_mark=45 - the same class, configured differently.
            WHY POINT THIS OUT: "one strategy per faculty" was never the
            rule. A strategy is a RULE, and two faculties can share one.

YOUR JOB (25 min)
    1. Make register() and create() work.
    2. The faculty -> strategy mapping must be DATA (a dict), not if/elif.
    3. The last check registers a faculty at runtime, from outside this file.
       If your registry is data, it just works.

THE DOWNSIDE
    Run it, then ask: where was that class instantiated? The stack trace no
    longer tells you. You traded "easy to find" for "easy to extend". Every DI
    container in industry makes this same trade, at a much bigger scale.
"""
from abc import ABC, abstractmethod
from check import check, check_raises


class GradingStrategy(ABC):
    @abstractmethod
    def grade(self, score):
        ...


class BulgarianScale(GradingStrategy):
    def __init__(self, pass_mark=50):
        self.pass_mark = pass_mark

    def grade(self, score):
        return "6" if score >= 88 else "2" if score < self.pass_mark else "4"


class PassFail(GradingStrategy):
    def grade(self, score):
        return "PASS" if score >= 60 else "FAIL"


class GradingFactory:
    _registry = {}

    @classmethod
    def register(cls, faculty, builder):
        raise NotImplementedError    # TODO

    @classmethod
    def create(cls, faculty):
        raise NotImplementedError    # TODO: KeyError with a clear message


# TODO: register informatics, law, engineering (BulgarianScale pass_mark=45)


if __name__ == "__main__":
    print("SESSION 06 - factory")

    # ---- STEP 1: the check we wrote FIRST, because it is the only one ----
    # ---- an if/elif chain cannot pass -----------------------------------
    class Roman(GradingStrategy):
        def grade(self, score):
            return "V" if score >= 50 else "I"

    GradingFactory.register("classics", Roman)
    check("a plugin this file never heard of",
          GradingFactory.create("classics").grade(80), "V")

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    # Four behaviours. Write each check, watch it fail, then make it pass.
    #
    #   "informatics"       create("informatics") must produce a
    #                       BulgarianScale. Check the TYPE NAME, not the
    #                       object - type(x).__name__ - because two
    #                       BulgarianScale instances are not equal to each
    #                       other and comparing them will mislead you.
    #   "law"               create("law") -> PassFail.
    #   "engineering has a different pass mark"
    #                       create("engineering").pass_mark is 45. Same class
    #                       as informatics, different configuration.
    #   "unknown faculty fails loudly"
    #                       create("astrology") raises KeyError. Use
    #                       check_raises for this one.
    #                       WHY THIS CHECK IS THE IMPORTANT ONE: it is the
    #                       difference between a typo you find in one second
    #                       and a None you find in an hour.
    #
    # STRETCH: add a check proving two create("informatics") calls return
    #          two DIFFERENT objects. Then make it pass. Then keep that
    #          thought warm for next week.
