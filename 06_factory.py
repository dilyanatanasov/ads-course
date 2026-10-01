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

    Every step has a HINT next to the code it belongs to.

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
    """One table: faculty name -> the thing that builds its grading rule.

    You never write GradingFactory(). Both methods are classmethods, so you
    call them on the class itself: GradingFactory.create("law").
    """
    _registry = {}

    @classmethod
    def register(cls, faculty, builder):
        """Add one row to the table."""
        # HINT: one line. Store builder in cls._registry under the key faculty.
        #
        # A "builder" is anything you can put brackets after to get a rule.
        # A class is one: PassFail is a builder, PassFail() is the rule.
        raise NotImplementedError    # TODO

    @classmethod
    def create(cls, faculty):
        """Build a fresh grading rule for this faculty."""
        # HINT: three steps.
        #   1. look the builder up in cls._registry
        #   2. not there -> raise KeyError("no grading rule registered for: "
        #                                  + faculty)
        #   3. CALL the builder and return the result - builder(), with the
        #      brackets. Without them you hand back the class, not a rule.
        raise NotImplementedError    # TODO


# TODO: three lines, one per faculty. The first one is done for you -
# uncomment it once register() works.
#
#   GradingFactory.register("informatics", BulgarianScale)
#
#   law          -> PassFail
#   engineering  -> BulgarianScale with pass_mark=45
#
# HINT for engineering: BulgarianScale(pass_mark=45) is already a finished
# rule - there is nothing left to call. Put `lambda:` in front of it, and it
# becomes something that builds one each time it is called.


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
    #
    #   informatics             create("informatics") is a BulgarianScale.
    #                           Compare the class NAME, not the object - two
    #                           instances are never equal:
    #
    #       check("informatics",
    #             type(GradingFactory.create("informatics")).__name__,
    #             "BulgarianScale")
    #
    #   law                     the same shape: create("law") is a PassFail
    #
    #   engineering pass mark   create("engineering").pass_mark is 45.
    #                           Check the NUMBER, not the class name - the
    #                           name would pass even if you forgot the 45.
    #
    #   unknown faculty fails   create("astrology") raises KeyError.
    #                           check_raises takes the name, the error, then
    #                           the function WITHOUT brackets and its argument:
    #
    #       check_raises("unknown faculty fails", KeyError,
    #                    GradingFactory.create, "astrology")
    #
    #                           Write create("astrology") yourself and it
    #                           blows up before check_raises can catch it.
