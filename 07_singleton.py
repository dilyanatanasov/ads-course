"""SESSION 07 - Singleton, and why your tests will hate you.

    python 07_singleton.py

The only session where the goal is to build something and then regret it.

PART 1 (10 min) - run it
    The textbook singleton is below. Lots of real code looks exactly like this.
    Run the file. Watch the second check FAIL - not because the code is wrong,
    but because state outlived the thing that owned it.

BUILD IT TOGETHER (12 min)
    STEP 1  Run it before changing anything. Read the FAIL line carefully:
            scenario B expected an empty database and found Ivan in it.
            WHY READ THE FAILURE OUT LOUD: nobody wrote a bug. Every line is
            correct on its own. The defect is that two things that should
            know nothing about each other are quietly sharing a variable.
            That is the only kind of bug that survives a code review.

    STEP 2  Ask before fixing: WHO decided StudentService uses that database?
            StudentService did, in its own constructor, where no caller can
            see it or change it. A dependency you cannot see is a dependency
            you cannot replace - and a test is just another caller that wants
            to replace something.

    STEP 3  Delete `Database()` from the constructor. Take `db` as a
            parameter instead. Four characters of typing.
            WHY THIS IS THE WHOLE OF DEPENDENCY INJECTION: that is it. That
            is the pattern. Every DI container you will ever meet is
            machinery for doing this at a scale where doing it by hand hurts.
            You are not learning a framework today, you are learning the
            thing frameworks automate.

    STEP 4  Build the Database once, in main(), and hand it down.
            WHY THE EDGE OF THE PROGRAM: somebody has to choose the real
            thing. Push that decision to the outermost layer and everything
            inside stays swappable. Session 16 gives this a name.

PART 2 (25 min) - fix it
    Rewrite StudentService so the database is passed IN (look for TODO).
    Construct it once at the edge of the program and hand it down.
    That habit has a fancy name - dependency injection - and you are about to
    write it by hand in four lines.

THE HONEST CAVEAT
    Singletons are not evil. A logger or a config object is usually fine.
    The rule that matters: if it holds STATE THAT CHANGES, do not make it
    global.
"""
from check import check


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.rows = []
        return cls._instance

    def insert(self, row):
        self.rows.append(row)

    def all(self):
        return list(self.rows)


class StudentService:
    def __init__(self):
        self.db = Database()          # TODO: take the db as a parameter

    def enrol(self, name):
        self.db.insert(name)


if __name__ == "__main__":
    print("SESSION 07 - singleton")
    print("\n-- two independent scenarios, each expecting a clean world --")
    first = StudentService()
    check("scenario A starts empty", first.db.all(), [])
    first.enrol("Ivan")

    second = StudentService()
    check("scenario B starts empty", second.db.all(), [])

    print("\nNothing is wrong with either scenario. Ivan leaked between them.")
    print("Fix: pass the Database in, build it once in main().")
