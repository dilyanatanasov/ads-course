"""SESSION 04 - Strategy.

    python 04_strategy.py

THE PAIN
    Every new faculty means editing the same if/elif chain. You felt it in 01.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback, not PASS/FAIL lines, because the methods below raise
    NotImplementedError until you write them. Read the LAST line of the
    traceback - it names the method to write first. As soon as one method
    works you start getting normal PASS/FAIL output again.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Write the first check, before any class exists:
                check("bulgarian top", Gradebook(BulgarianScale()).grade(91),
                      "6 (Excellent)")
            It does not even import. Good.
            WHY START WITH A LINE THAT CANNOT RUN: that line is a design
            decision in disguise. It says a Gradebook is HANDED a rule rather
            than choosing one, and it says every rule answers to .grade().
            We just designed the interface by writing the call we wished we
            could make. Notice nobody argued about class diagrams.

    STEP 2  GradingStrategy - an ABC with one abstract method.
            WHY ABC AND NOT A PLAIN CLASS: with @abstractmethod, forgetting
            to implement grade() fails LOUDLY at construction. Without it,
            you get None back three layers away and spend an afternoon on it.
            Push errors towards the mistake.

    STEP 3  BulgarianScale with the pass mark HARDCODED to 50. Run it. Green.
            WHY HARDCODE SOMETHING WE KNOW IS WRONG: because the check for
            the adjustable pass mark is not written yet. Write only what the
            current check demands, or you are guessing at requirements - and
            in a minute the twist will tell us what the real requirement is.

    STEP 4  Now the twist arrives: Maritime wants pass mark 45. Add the check
            FIRST, watch it fail, then make pass_mark a constructor argument.
            WHY THE FAILURE MATTERS: a check you never saw fail is a check
            you have no reason to trust. It might be passing by accident.

    STEP 5  Ask the room: where did the if/elif chain from session 01 go?
            It did not. It is still there, inside BulgarianScale. We did not
            delete the complexity - we put a wall around it so it stops
            leaking into every faculty we add.

YOUR JOB (25 min)
    1. Finish BulgarianScale (support an adjustable pass_mark).
    2. Add PassFail (>= 60 passes) and Percentage.
    3. Make Gradebook take a strategy instead of a faculty string.
    STRETCH: Weighted - a strategy that combines scores then delegates to
             ANOTHER strategy. A strategy holding a strategy. That is allowed.

THE TWIST (5 min)
    Maritime wants the 2-6 scale with pass mark 45 instead of 50. How many
    existing lines do you edit? Compare with session 01.

THE DOWNSIDE - say this out loud
    You now have five small classes instead of one function. Which strategy
    actually runs for student s001? You cannot tell by reading. You have to
    run it. Session 06 is about who pays that bill.
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
