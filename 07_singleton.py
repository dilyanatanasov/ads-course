"""SESSION 07 - Singleton, and why it breaks your tests.

    python 07_singleton.py

THE SITUATION
    The textbook singleton is below: one Database, shared by everyone who
    asks for it. Plenty of real code looks exactly like this.

    Run it. The second check FAILS - and not because the code is wrong. Both
    scenarios are correct on their own. Ivan leaked from the first into the
    second, because the database outlived the thing that owned it.

    Before you fix anything, answer out loud: WHO decided that StudentService
    uses that database? StudentService did, in its own constructor, where no
    caller can see it or change it. A dependency you cannot see is one you
    cannot replace - and a test is just another caller wanting to replace
    something.

THE IDEA
    Stop letting the class choose. Pass the database IN. Build it once at the
    edge of the program and hand it down.

    That habit has a fancy name - dependency injection - and you are about to
    write it by hand in four lines. Every DI framework you will meet is
    machinery for doing this at a scale where doing it by hand hurts.

YOUR TASK (25 min)
    1. StudentService takes `db` as a constructor parameter (see the TODO).
    2. Build the Database once in __main__ and pass it in.
    3. The two scenarios must stop affecting each other.

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
