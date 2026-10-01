"""SESSION 03 - Coupling, measured. SOLUTION.

The per-credit change is applied to both designs. Note WHERE each edit landed:

    Flat   -> inside register(), which also stores a row and sends a message
    Split  -> inside Pricing.fee_for(), which does nothing else

Same one-line change. Only one of them put the enrolment logic at risk.
"""
import ast
import inspect
from check import check

RATE_PER_CREDIT = 25


def blast_radius(name, *classes):
    hits = []
    for cls in classes:
        tree = ast.parse(inspect.getsource(cls))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for inner in ast.walk(node):
                if ((isinstance(inner, ast.Name) and inner.id == name)
                        or (isinstance(inner, ast.Attribute)
                            and inner.attr == name)
                        or (isinstance(inner, ast.Constant)
                            and inner.value == name)):
                    hits.append(f"{cls.__name__}.{node.name}")
                    break
    return sorted(set(hits))


def show(label, methods):
    print(f"   {label:<8} {len(methods)}  {', '.join(methods)}")


class Flat:
    def __init__(self):
        self.rows = []
        self.messages = []

    def register(self, student, course):
        fee = course["credits"] * RATE_PER_CREDIT      # <- the edit landed here
        self.rows.append({"student": student, "course": course["id"],
                          "fee": fee, "grade": None})
        self.messages.append(f"registered {student}")

    def set_grade(self, student, course_id, grade):
        for row in self.rows:
            if row["student"] == student and row["course"] == course_id:
                row["grade"] = grade

    def transcript(self, student):
        return [(r["course"], r["grade"]) for r in self.rows
                if r["student"] == student]

    def outstanding(self):
        return sum(r["fee"] for r in self.rows if r["grade"] is None)

    def invoice_lines(self):
        return [f"{r['student']} owes {r['fee']} lv"
                for r in self.rows if r["grade"] is None]


class Pricing:
    def fee_for(self, course):
        return course["credits"] * RATE_PER_CREDIT     # <- and here


class Enrolment:
    def __init__(self, student, course_id, fee):
        self.student = student
        self.course_id = course_id
        self.fee = fee
        self.grade = None


class Split:
    def __init__(self, pricing=None):
        self.pricing = pricing or Pricing()
        self.rows = []
        self.messages = []

    def register(self, student, course):
        self.rows.append(Enrolment(student, course["id"],
                                   self.pricing.fee_for(course)))
        self.messages.append(f"registered {student}")

    def set_grade(self, student, course_id, grade):
        for row in self.rows:
            if row.student == student and row.course_id == course_id:
                row.grade = grade

    def transcript(self, student):
        return [(r.course_id, r.grade) for r in self.rows
                if r.student == student]

    def outstanding(self):
        return sum(r.fee for r in self.rows if r.grade is None)

    def invoice_lines(self):
        return [f"{r.student} owes {r.fee} lv"
                for r in self.rows if r.grade is None]


class VatPricing(Pricing):
    """Bonus: with Split, VAT is a NEW class. Nothing existing is edited.

    Try the same trick on Flat and you cannot - the rule is welded into
    register(). That is the payoff, and it only exists on the axis the design
    anticipated.
    """

    def fee_for(self, course):
        return round(super().fee_for(course) * 1.20)


if __name__ == "__main__":
    print("SESSION 03 - coupling, measured (solution)")
    course = {"id": "c01", "title": "Databases", "credits": 6}

    print("\n1. TO CHANGE THE PRICING RULE, WHICH METHOD DO YOU OPEN?")
    show("Flat", ["Flat.register"])
    show("Split", ["Pricing.fee_for"])

    print("\n3. THE HONEST ONE - rename the grade field")
    show("Flat", blast_radius("grade", Flat))
    show("Split", blast_radius("grade", Split, Enrolment))

    print("\n-- both designs still work --")
    for name, system in (("flat", Flat()), ("split", Split())):
        system.register("Ivan", course)
        system.set_grade("Ivan", "c01", "6")
        check(f"{name}: transcript", system.transcript("Ivan"),
              [("c01", "6")])
        check(f"{name}: graded rows are settled", system.outstanding(), 0)
        system.register("Maria", course)
        check(f"{name}: ungraded row is outstanding",
              system.outstanding(), 150)

    print("\n-- per-credit pricing --")
    check("split: pricing rule is per credit", Pricing().fee_for(course), 150)
    flat = Flat()
    flat.register("Georgi", course)
    check("flat: charges per credit", flat.rows[0]["fee"], 150)

    print("\n-- bonus: VAT as a new class, nothing existing edited --")
    vat = Split(pricing=VatPricing())
    vat.register("Petar", course)
    check("VAT added by substitution", vat.rows[0].fee, 180)
