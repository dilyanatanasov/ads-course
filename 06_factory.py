"""SESSION 06 - Factory.

    python 06_factory.py

THE SITUATION
    Session 04 gave you a grading rule per faculty. But somebody still has to
    decide WHICH rule a given student gets, and right now that decision is
    scattered - in a real project you would find `BulgarianScale(` written out
    in a dozen different files.

THE IDEA
    Put the faculty -> rule decision in ONE place, and make it DATA rather
    than code. A dict, not an if/elif chain. Adding a faculty then means
    adding a row - and it can be added from outside this file entirely.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. GradingFactory.register(faculty, builder) - store it in _registry.
    2. GradingFactory.create(faculty) - look it up and build one.
       An unknown faculty must raise KeyError, loudly. Never return None.
    3. Register informatics, law and engineering. Engineering is
       BulgarianScale with pass_mark=45 - the same class, configured
       differently. One rule can serve two faculties.
    4. Write the four remaining checks at the bottom.

    Store the CLASS, not an instance. Two students sharing one rule object is
    session 07's disaster arriving a week early.

THE COST
    Run it, then ask: where was that class actually created? The stack trace
    no longer tells you. You traded "easy to find" for "easy to extend", and
    every dependency-injection container in industry makes the same trade at
    a much bigger scale.
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

    # ---- GIVEN: the only check an if/elif chain cannot pass --------------
    # It registers a faculty from OUTSIDE this file, at runtime. If your
    # registry is data rather than code, it just works.
    class Roman(GradingStrategy):
        def grade(self, score):
            return "V" if score >= 50 else "I"

    GradingFactory.register("classics", Roman)
    check("a plugin this file never heard of",
          GradingFactory.create("classics").grade(80), "V")

    # YOUR TURN - write one check for each, then make them pass:
    #   informatics             create("informatics") is a BulgarianScale.
    #                           Compare type(x).__name__, not the object -
    #                           two instances are never equal.
    #   law                     create("law") is a PassFail
    #   engineering pass mark   create("engineering").pass_mark is 45
    #   unknown faculty fails   create("astrology") raises KeyError.
    #                           Use check_raises.
