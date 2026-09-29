"""SESSION 16 - the DOMAIN layer.

Pure rules. Imports NOTHING from application or infrastructure. That is the
whole constraint, and 16_layers.py enforces it.
"""


class NotEligible(Exception):
    pass


class CourseFull(Exception):
    pass


class Student:
    def __init__(self, sid, name, faculty, credits=0):
        self.id, self.name, self.faculty = sid, name, faculty
        self.credits = credits

    def may_enrol_in(self, course):
        return self.credits >= course.required_credits


class Course:
    def __init__(self, cid, title, seats, required_credits=0):
        self.id, self.title = cid, title
        self.seats, self.required_credits = seats, required_credits
