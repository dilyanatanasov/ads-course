"""SESSION 04 - Strategy.

    python 04_strategy.py

THE SITUATION
    Every faculty grades differently, and a new faculty arrives every few
    years. In session 01 that meant another branch in one if/elif chain that
    every faculty shares - so adding Maritime risked breaking Law.

THE IDEA
    Make the grading rule an OBJECT you hand to the Gradebook, instead of a
    branch inside it. Adding a faculty then means adding a class, not editing
    one everybody depends on.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. Gradebook.grade - return what the strategy says. Two lines, do this
       first, it is the easiest.
    2. Percentage.grade  -> "73%"
    3. PassFail.grade    -> "PASS" or "FAIL"
    4. BulgarianScale.grade - below pass_mark is "2 (Poor)". The four passing
       grades split what is left evenly: 3, 4, 5, 6.
    5. Write the four remaining checks listed at the bottom.

    Notice BulgarianScale.grade is still an if/elif chain - the same one from
    session 01. You did not delete the complexity. You put a wall around it
    so it stops growing every time a faculty joins.

THE TWIST
    Maritime wants the same 2-6 scale but a pass mark of 45 instead of 50.
    How many existing lines do you edit? Compare with session 01.

THE COST
    You now have four small classes instead of one function. Which grading
    rule runs for student s001? You cannot tell by reading - you have to run
    it. You traded "easy to find" for "easy to change". Session 06 is about
    who pays that bill.
"""
from abc import ABC, abstractmethod
from check import check


class GradingStrategy(ABC):
    @abstractmethod
    def grade(self, score: float) -> str:
        ...


class BulgarianScale(GradingStrategy):
    def __init__(self, pass_mark=50):
        self.pass_mark = pass_mark

    def grade(self, score):
        # TODO: below pass_mark -> "2 (Poor)". The four passing bands split
        # what is left evenly: 3 (Satisfactory), 4 (Good), 5 (Very good),
        # 6 (Excellent).
        raise NotImplementedError


class PassFail(GradingStrategy):
    def __init__(self, pass_mark=60):
        self.pass_mark = pass_mark

    def grade(self, score):
        raise NotImplementedError    # TODO


class Percentage(GradingStrategy):
    def grade(self, score):
        raise NotImplementedError    # TODO: "73%"


class Gradebook:
    def __init__(self, strategy):
        self.strategy = strategy     # TODO: use it below

    def grade(self, score):
        raise NotImplementedError    # TODO


if __name__ == "__main__":
    print("SESSION 04 - strategy")

    # ---- STEP 1: the check we wrote before any class existed -------------
    check("bulgarian top", Gradebook(BulgarianScale()).grade(91),
          "6 (Excellent)")

    # YOUR TURN - write one check for each, then make them pass:
    #   bulgarian fail          49 on the default scale
    #   pass / fail             60 and 59 under PassFail
    #   percentage              73 under Percentage
    #   adjustable pass mark    47 under BulgarianScale(pass_mark=45)
    #
    # Do the last one first if you like. It is the one that forces pass_mark
    # out of the code and into the constructor.
