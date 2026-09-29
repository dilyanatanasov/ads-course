"""SESSION 01 - The baseline. THE REVEAL.

    python 01_baseline_solution.py

This is one way to implement the three change requests: the obvious,
procedural way. It is not "good code" and it is not meant to be. It is the
honest answer to "what happens when you add three features to a monolith
the fastest way".

Every edit is marked with  # CR-1  # CR-2  # CR-3  so you can see exactly
what each change request touched.

    CR-1  Maritime Studies: 0-100 percentage grading
    CR-2  notifications go to email as well as console
    CR-3  scholarship students do not pay

COMPARE THIS TO YOUR OWN SOLUTION
    How many places did YOU touch for each CR? Same count as here, or
    different? Neither answer is wrong - that's the point of today.

    Once you've compared, look at register(). Count how many different
    things it now does: validate, check seats, decide who pays, take
    payment, store the row, notify. That's six reasons for one method
    to change.

    Ask yourself: what would a FOURTH faculty cost to add here? A fifth?
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
        self.sent_emails = []                                        # CR-2

    def add_student(self, sid, name, faculty, scholarship=False):    # CR-3
        self.students[sid] = {"id": sid, "name": name, "faculty": faculty}
        if scholarship:                                              # CR-3
            SCHOLARSHIP_STUDENTS.add(sid)                            # CR-3

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

        # CR-3: the fee decision is now welded into the middle of register()
        pays = sid not in SCHOLARSHIP_STUDENTS                       # CR-3
        if course["fee"] > 0 and pays:                               # CR-3
            self.payments.append({"student": sid, "amount": course["fee"]})

        self.registrations.append({"student": sid, "course": cid,
                                   "grade": None})

        message = f"Dear {self.students[sid]['name']}, you are registered for {course['title']}."
        self.console.append(message)
        self.sent_emails.append(message)                             # CR-2
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
        elif faculty == "maritime":                                  # CR-1
            g = f"{round(score)}%"                                   # CR-1
        else:
            raise ValueError("unknown faculty: " + faculty)

        for r in self.registrations:
            if r["student"] == sid and r["course"] == cid:
                r["grade"] = g

        message = f"Your grade is {g}."
        self.console.append(message)
        self.sent_emails.append(message)                             # CR-2
        return g


if __name__ == "__main__":
    print("SESSION 01 - baseline + the three change requests")

    s = RegistrationSystem()
    s.add_student("s001", "Ivan", "informatics")
    s.add_student("s002", "Maria", "law")
    s.add_student("s004", "Nikolay", "maritime")
    s.add_student("s005", "Elena", "informatics", scholarship=True)
    s.add_course("c01", "Databases", seats=4, fee=120)

    print("\n-- the original six still pass --")
    check("registers a student", s.register("s001", "c01"), True)
    check("charges the fee", s.payments[0]["amount"], 120)
    check_raises("rejects double registration", ValueError,
                 s.register, "s001", "c01")
    check("bulgarian scale", s.grade("s001", "c01", 91), "6 (Excellent)")
    s.register("s002", "c01")
    check("law is pass/fail", s.grade("s002", "c01", 91), "PASS")

    print("\n-- CR-1: maritime grades as a percentage --")
    s.register("s004", "c01")
    check("maritime percentage", s.grade("s004", "c01", 73), "73%")

    print("\n-- CR-2: notifications also go to email --")
    check("email sent on registration",
          s.sent_emails[0], "Dear Ivan, you are registered for Databases.")
    check("console still works too", len(s.console), len(s.sent_emails))

    print("\n-- CR-3: scholarship students do not pay --")
    payments_before = len(s.payments)
    s.register("s005", "c01")
    check("scholarship student registered", len(s.registrations), 4)
    check("but was not charged", len(s.payments), payments_before)

    print("\n-- what each CR cost --")
    print("   CR-1 touched 1 place   (a third branch in the grading chain)")
    print("   CR-2 touched 3 places  (constructor + both notify sites)")
    print("   CR-3 touched 2 places  (add_student + inside register)")
    print("   register() now does 6 things: validate, seats, who-pays,")
    print("   payment, store, notify. Six reasons for it to change.")
    print("\n   What does a FOURTH faculty cost? A fifth?")
