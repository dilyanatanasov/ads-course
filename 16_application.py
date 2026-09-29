"""SESSION 16 - the APPLICATION layer.

One use case. May import domain. May NOT import infrastructure - it declares
what it needs and something else supplies it.
"""
import importlib

domain = importlib.import_module("16_domain")


class EnrolStudent:
    def __init__(self, students, courses, notifier):
        self.students, self.courses, self.notifier = students, courses, notifier

    def __call__(self, student_id, course_id):
        student = self.students.get(student_id)
        course = self.courses.get(course_id)

        if not student.may_enrol_in(course):
            raise domain.NotEligible(
                f"{student.name} needs {course.required_credits} credits"
            )
        if self.courses.seats_left(course_id) <= 0:
            raise domain.CourseFull(course.title)

        self.courses.take_seat(course_id, student_id)
        self.notifier.notify(student, "Enrolled in " + course.title)
        return True
