"""SESSION 15 - Repository.

    python 15_repository.py

THE PAIN
    Your service opens SQLite directly. So the tests need a database file, they
    are slow, they leave junk behind, and SQL strings are glued to business
    logic.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Look at run_checks(). It takes a REPO as a parameter. That is the
            only structural idea in this session and it is already written
            for you - read it before you write anything.
            WHY IT IS A FUNCTION AND NOT A SCRIPT: a check suite that takes
            the thing under test as an argument can be pointed at any
            implementation. It is session 02's seam again, applied to the
            checks themselves.

    STEP 2  Write the checks into run_checks() together, in domain words -
            get, missing, by_faculty, round trip. Notice there is not one
            SQL word in any of them.
            WHY THAT MATTERS MORE THAN IT LOOKS: the moment a check says
            SELECT, it can only ever run against a database, and you have
            lost the ability to ask this exact question of anything else.
            The vocabulary of the checks IS the interface.

    STEP 3  InMemoryStudentRepository. A dict. Four lines. Run it. Green.
            WHY BUILD THE FAKE FIRST: it is faster to get right, so any
            failure now is a failure in your CHECKS, not your storage. Debug
            one thing at a time.

    STEP 4  Now SqliteStudentRepository, and do not touch run_checks() while
            you do it. Not one character.
            WHY THAT RULE IS THE ENTIRE SESSION: if you find yourself
            needing to edit a check to make the second implementation pass,
            your interface was never honest - it was the dict's shape
            wearing a costume. The rule catches the lie immediately.

    STEP 5  Ask: get() returns None for a missing student in BOTH. Did you
            have to work for that in sqlite? fetchone() already returns None.
            Lucky. Now ask what would have happened if one raised and the
            other returned None - and how far away the bug would have
            surfaced.

YOUR JOB (25 min)
    1. InMemoryStudentRepository - a dict.
    2. SqliteStudentRepository   - stdlib sqlite3, ":memory:" for tests.
    THE SAME CHECKS RUN AGAINST BOTH. That is the point of today. If your
    abstraction is honest, both pass unchanged.

THE DOWNSIDE - be specific
    The registrar wants "students in the top 10% of their faculty who have not
    paid, sorted by enrolment date". Express that through by_faculty() and you
    will load 4000 rows into Python and filter them there.

    The repository made easy things easy and one important thing slow. Real
    projects fix it by adding a query method that leaks SQL - usually the right
    call. Just know you are making the trade.
"""
import sqlite3
from abc import ABC, abstractmethod
from check import check


class Student:
    def __init__(self, sid, name, faculty):
        self.id, self.name, self.faculty = sid, name, faculty

    def __eq__(self, other):
        return (isinstance(other, Student) and (other.id, other.name,
                other.faculty) == (self.id, self.name, self.faculty))

    def __repr__(self):
        return f"Student({self.id}, {self.name}, {self.faculty})"


class StudentRepository(ABC):
    """Domain language only. No SQL words in this interface."""

    @abstractmethod
    def add(self, student):
        ...

    @abstractmethod
    def get(self, sid):
        ...

    @abstractmethod
    def by_faculty(self, faculty):
        ...


class InMemoryStudentRepository(StudentRepository):
    def __init__(self):
        self._rows = {}

    def add(self, student):
        raise NotImplementedError    # TODO

    def get(self, sid):
        raise NotImplementedError    # TODO: None when missing

    def by_faculty(self, faculty):
        raise NotImplementedError    # TODO


class SqliteStudentRepository(StudentRepository):
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        # TODO: CREATE TABLE IF NOT EXISTS students (id TEXT PRIMARY KEY, ...)

    def add(self, student):
        raise NotImplementedError    # TODO

    def get(self, sid):
        raise NotImplementedError    # TODO

    def by_faculty(self, faculty):
        raise NotImplementedError    # TODO


def run_checks(repo, label):
    """ONE suite, pointed at any storage. Never edit this to make sqlite pass.

    If you need to, the interface is lying - fix the repository instead.
    """
    print(f"\n-- {label} --")
    repo.add(Student("s001", "Ivan", "informatics"))
    repo.add(Student("s002", "Maria", "law"))
    repo.add(Student("s003", "Georgi", "informatics"))

    # ---- STEP 2: the first check, written together -----------------------
    check("get", repo.get("s001").name, "Ivan")

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    # Three more. Domain words only - if you type SELECT in here, stop.
    #
    #   "missing returns None"   repo.get("nope"). Decide as a room: None,
    #                            or an exception? Whatever you pick, BOTH
    #                            implementations must do the same thing, and
    #                            this check is what forces that.
    #
    #   "by faculty"             the informatics students' names, sorted.
    #                            WHY sorted(): a dict and a database do not
    #                            promise the same order. Checking an
    #                            unsorted list would pass on one and fail on
    #                            the other, and you would blame the wrong
    #                            thing. When the order is not part of the
    #                            promise, do not let the check depend on it.
    #
    #   "round trip"             repo.get("s002") equals
    #                            Student("s002", "Maria", "law").
    #                            This one only works because Student defines
    #                            __eq__ - look at it. Without that you would
    #                            be comparing object identities and every
    #                            repository on earth would fail.


if __name__ == "__main__":
    print("SESSION 15 - repository (one suite, two storages)")
    run_checks(InMemoryStudentRepository(), "in memory")
    run_checks(SqliteStudentRepository(), "sqlite")
