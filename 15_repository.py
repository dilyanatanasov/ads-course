"""SESSION 15 - Repository.

    python 15_repository.py

THE SITUATION
    Your service opens SQLite directly. So the tests need a real database
    file, they are slow, they leave junk behind, and SQL strings are glued to
    business logic.

THE IDEA
    Put storage behind an interface written in DOMAIN words - add, get,
    by_faculty - with no SQL in it. Then write two implementations: a dict
    and a real database. THE SAME CHECKS RUN AGAINST BOTH.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. InMemoryStudentRepository - a dict. Do this one first; it is faster to
       get right, so any failure is in your CHECKS, not your storage.
    2. SqliteStudentRepository - stdlib sqlite3, ":memory:" for tests.
    3. Write the three remaining checks inside run_checks().

    THE RULE: once run_checks() passes for the dict, do not touch it again.
    Not one character. If you need to edit a check to make sqlite pass, your
    interface was never honest - it was the dict's shape wearing a costume,
    and the rule catches that immediately.

THE COST - be specific
    The registrar wants "students in the top 10% of their faculty who have
    not paid, sorted by enrolment date". Express that through by_faculty()
    and you will load 4000 rows into Python and filter them there.

    The repository made easy things easy and one important thing slow. Real
    projects fix it by adding a query method that leaks SQL - usually the
    right call. Just know you are making the trade.
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

    # YOUR TURN - three more, in domain words only. If you type SELECT, stop.
    #   missing returns None   repo.get("nope"). Decide as a room: None or an
    #                          exception? Whichever you pick, BOTH storages
    #                          must agree, and this check forces that.
    #   by faculty             the informatics students' names, sorted().
    #                          A dict and a database do not promise the same
    #                          order, so an unsorted check would pass on one
    #                          and fail on the other.
    #   round trip             repo.get("s002") equals
    #                          Student("s002", "Maria", "law"). This works
    #                          only because Student defines __eq__ - look at
    #                          it.


if __name__ == "__main__":
    print("SESSION 15 - repository (one suite, two storages)")
    run_checks(InMemoryStudentRepository(), "in memory")
    run_checks(SqliteStudentRepository(), "sqlite")
