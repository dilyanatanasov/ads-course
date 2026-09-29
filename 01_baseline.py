"""SESSION 01 - The baseline.

    python 01_baseline.py

THE SITUATION
    You inherit a working exam registration system. One file. It runs.

RUN IT TOGETHER (8 min - no new code today)
    STEP 1  Run it. Everything passes. Say that out loud: this code WORKS.
            WHY THAT IS THE STARTING POINT: nothing you will do this semester
            is about making broken code work. It is about what happens to
            working code when someone asks for one more thing. If you only
            ever judge code by "does it run", every design in this course
            looks like a waste of time.

    STEP 2  Read the checks at the bottom before the class. They are the only
            description of what this system promises.
            WHY THEY GO FIRST FROM NOW ON: from session 02, YOU write these
            before you write the code. Today you just read them, so that
            next week you know what you are aiming at.

    STEP 3  Now take the change requests. Time yourself on each one.

YOUR JOB (25 min, pairs)
    Three change requests. Do them any way you like - no correct answer today.

    CR-1  Faculty of Maritime Studies joins. They grade 0-100 percentage.
    CR-2  Notifications go to email as well as console (append to sent_emails).
    CR-3  Students with a scholarship do not pay.

THEN ANSWER OUT LOUD
    1. How many places did you touch for CR-1?
    2. What changes when a fourth faculty joins?
    3. Which CR was hardest, and why?

THE POINT
    Nobody wrote this badly on purpose. This is what code looks like when every
    feature was added the fastest way at the time.
"""
from check import check, check_raises

SCHOLARSHIP_STUDENTS = {"s003"}


class RegistrationSystem:
    def __init__(self):
        self.students = {}
        self.courses = {}
        self.registrations = []
        self.payments = []
        self.console = []

    def add_student(self, sid, name, faculty):
        self.students[sid] = {"id": sid, "name": name, "faculty": faculty}

    def add_course(self, cid, title, seats, fee):
        self.courses[cid] = {"id": cid, "title": title, "seats": seats,
                             "fee": fee}

    def register(self, sid, cid):
        if sid not in self.students:
            raise ValueError("no such student: " + sid)
        if cid not in self.courses:
            raise ValueError("no such course: " + cid)
        for r in self.registrations:
            if r["student"] == sid and r["course"] == cid:
                raise ValueError("already registered")

        course = self.courses[cid]
        taken = len([r for r in self.registrations if r["course"] == cid])
        if taken >= course["seats"]:
            raise ValueError("course is full")

        if course["fee"] > 0:
            self.payments.append({"student": sid, "amount": course["fee"]})

        self.registrations.append({"student": sid, "course": cid,
                                   "grade": None})
        self.console.append(
            f"Dear {self.students[sid]['name']}, you are registered for {course['title']}."
        )
        return True

    def grade(self, sid, cid, score):
        faculty = self.students[sid]["faculty"]
        if faculty == "informatics":
            if score < 50:
                g = "2 (Poor)"
            elif score < 63:
                g = "3 (Satisfactory)"
            elif score < 75:
                g = "4 (Good)"
            elif score < 88:
                g = "5 (Very good)"
            else:
                g = "6 (Excellent)"
        elif faculty == "law":
            g = "PASS" if score >= 60 else "FAIL"
        else:
            raise ValueError("unknown faculty: " + faculty)
        for r in self.registrations:
            if r["student"] == sid and r["course"] == cid:
                r["grade"] = g
        return g


if __name__ == "__main__":
    print("SESSION 01 - baseline (everything should pass before you start)")
    s = RegistrationSystem()
    s.add_student("s001", "Ivan", "informatics")
    s.add_student("s002", "Maria", "law")
    s.add_course("c01", "Databases", seats=2, fee=120)

    check("registers a student", s.register("s001", "c01"), True)
    check("charges the fee", s.payments[0]["amount"], 120)
    check_raises("rejects double registration", ValueError,
                 s.register, "s001", "c01")
    check("bulgarian scale", s.grade("s001", "c01", 91), "6 (Excellent)")
    s.register("s002", "c01")
    check("law is pass/fail", s.grade("s002", "c01", 91), "PASS")
    s.add_student("s003", "Georgi", "informatics")
    check_raises("respects seat limit", ValueError, s.register, "s003", "c01")
