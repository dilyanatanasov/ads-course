"""SESSION 02 - Seams. SOLUTION."""
from datetime import datetime
from check import check, check_raises

DEADLINE = datetime(2030, 3, 1)


class Registration:
    def __init__(self, clock=None, notify=None, fee_rule=None):
        # Each default keeps the original behaviour. Nothing is forced on the
        # caller - the seam is opt-in.
        self.clock = clock or datetime.now
        self.notify = notify or print
        self.fee_rule = fee_rule or (lambda course: 120)
        self.registrations = []
        self.charged = []

    def register(self, student, course):
        if self.clock() > DEADLINE:
            raise ValueError("registration closed on 1 March 2030")

        fee = self.fee_rule(course)
        self.charged.append((student, fee))
        self.registrations.append((student, course))

        self.notify(f"Dear {student}, you are registered for {course['title']}.")
        return True


if __name__ == "__main__":
    print("SESSION 02 - seams (solution)")
    course = {"id": "c01", "title": "Databases", "credits": 6}

    before = Registration(clock=lambda: datetime(2030, 2, 20))
    check("open before the deadline", before.register("Ivan", course), True)

    after = Registration(clock=lambda: datetime(2030, 3, 2))
    check_raises("closed after the deadline", ValueError,
                 after.register, "Ivan", course)

    sent = []
    watched = Registration(clock=lambda: datetime(2030, 2, 20),
                           notify=sent.append)
    watched.register("Maria", course)
    check("notification captured, not printed", sent,
          ["Dear Maria, you are registered for Databases."])

    per_credit = Registration(clock=lambda: datetime(2030, 2, 20),
                              notify=sent.append,
                              fee_rule=lambda c: c["credits"] * 25)
    per_credit.register("Georgi", course)
    check("fee rule swapped without editing register()",
          per_credit.charged, [("Georgi", 150)])

    plain = Registration()
    check("defaults are still sensible", callable(getattr(plain, "fee_rule", None)), True)
