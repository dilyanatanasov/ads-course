"""SESSION 04 - Strategy. SOLUTION."""
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


class PassFail(GradingStrategy):
    def __init__(self, pass_mark=60):
        self.pass_mark = pass_mark

    def grade(self, score):
        return "PASS" if score >= self.pass_mark else "FAIL"


class Percentage(GradingStrategy):
    def grade(self, score):
        return f"{round(score)}%"


class Gradebook:
    def __init__(self, strategy):
        self.strategy = strategy

    def grade(self, score):
        return self.strategy.grade(score)


if __name__ == "__main__":
    print("SESSION 04 - strategy (solution)")
    check("bulgarian top", Gradebook(BulgarianScale()).grade(91),
          "6 (Excellent)")
    check("bulgarian fail", Gradebook(BulgarianScale()).grade(49), "2 (Poor)")
    check("pass", Gradebook(PassFail()).grade(60), "PASS")
    check("fail", Gradebook(PassFail()).grade(59), "FAIL")
    check("percentage", Gradebook(Percentage()).grade(73), "73%")
    check("adjustable pass mark",
          Gradebook(BulgarianScale(pass_mark=45)).grade(47),
          "3 (Satisfactory)")
