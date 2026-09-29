"""SESSION 03 - Coupling and cohesion, measured.

    python 03_coupling.py

Most courses define these two words and move on. Today you get a number.

    COUPLING  how much one thing depends on another
    COHESION  how much the things inside one class belong together

BLAST RADIUS
    Pick a change. Count the methods you must edit to make it. That number is
    your coupling, and unlike the definition you can argue about it with
    evidence. blast_radius() below counts for you, using ast.

THE TWO WORDS, AND WHAT EACH ONE BUYS YOU
    COUPLING   how much one thing depends on another.
               LOW coupling buys you: when you change X, you do not have to
               open Y. The change stays where you put it.

    COHESION   how much the things inside one class belong together.
               HIGH cohesion buys you: you can read one method and know what
               it is for, because it only does one job.

    They are not the same knob. A class can be badly coupled AND badly
    cohesive - Flat below is both - or low-coupled and still incoherent.

NOTHING TO IMPLEMENT TODAY
    There are no TODOs. Run the file, read the three measurements, and argue.
    Below are two designs doing the same job: Flat is written the way session
    01 was; Split separates pricing from enrolling.

    1. Before you run it, PREDICT. To change the pricing rule - how many
       methods in Flat? How many in Split? Say a number out loud first.
       A prediction you got wrong is worth ten you never made.

    2. Run it. The first measurement says 1 and 1 - the same. So look at the
       two methods themselves. Flat.register changes pricing while also
       storing a row and sending a message; Pricing.fee_for is one line about
       money. THAT is the difference, and the count did not show it.

    3. Measurement 3 is the one that matters most: 5 against 5. Do not let
       anyone skip it.

THE RESULT YOU SHOULD EXPECT
    To change the PRICING RULE, Flat makes you open a method that also stores
    rows and sends messages. Split makes you open a method that does one thing.
    Same edit, very different chance of breaking something unrelated.

THE HONEST BIT - do not skip this
    Look at measurement 3. Renaming the `grade` field costs about the same in
    both designs. Decoupling did nothing for it.

    That is not a flaw in the exercise, it is the lesson: you decouple along
    the axis you expect to change. Split anticipated pricing changing and was
    rewarded. It never anticipated the row shape changing and got no help.
    Nobody decouples along every axis at once - that is just a program with no
    structure at all.

THE DOWNSIDE
    Split is longer, and to follow one registration you open three classes.
    Reading it is harder; changing pricing is easier. You are choosing which of
    those you do more often.

    Corollary worth saying out loud: for code that will NEVER change, Flat is
    the correct design. Most coursework is in that category, which is why all
    of this felt pointless until now.
"""
import ast
import inspect
from check import check


def blast_radius(name, *classes):
    """Methods across `classes` whose body mentions `name`."""
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


# ---------------------------------------------------------------- design A
class Flat:
    """Storage, pricing, messaging and reporting in one class."""

    def __init__(self):
        self.rows = []
        self.messages = []

    def register(self, student, course):
        fee = 120                                   # <- the pricing RULE
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


# ---------------------------------------------------------------- design B
class Pricing:
    """Knows about money. Knows nothing about grades or messages."""

    def fee_for(self, course):
        return 120                                  # <- the pricing RULE


class Enrolment:
    """Knows what one row is."""

    def __init__(self, student, course_id, fee):
        self.student = student
        self.course_id = course_id
        self.fee = fee
        self.grade = None


class Split:
    """Knows about enrolling. Delegates pricing."""

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


if __name__ == "__main__":
    print("SESSION 03 - coupling, measured")
    course = {"id": "c01", "title": "Databases", "credits": 6}

    print("\nThese three measurements RENAME NOTHING and EDIT NOTHING.")
    print("They only count how many methods a change would force you to open.")
    print("The one real edit you make today is the price, at the bottom.")
    print("\n1. IF YOU CHANGED THE PRICING RULE - which method would you open?")
    show("Flat", ["Flat.register"])
    show("Split", ["Pricing.fee_for"])
    print("      Flat.register also stores a row and sends a message.")
    print("      Pricing.fee_for does one thing. Same edit, different risk.")

    print("\n2. IF YOU RENAMED THE FEE FIELD - how many mention it?")
    print("      (same in both, and that is fine - READING a value is not")
    print("      coupling to the RULE that produces it.)")
    show("Flat", blast_radius("fee", Flat))
    show("Split", blast_radius("fee", Split, Enrolment, Pricing))

    print("\n3. IF YOU RENAMED THE GRADE FIELD - how many mention it?")
    show("Flat", blast_radius("grade", Flat))
    show("Split", blast_radius("grade", Split, Enrolment))
    print("      Barely different. Decoupling helped with pricing because")
    print("      pricing is what Split was built to isolate. It gives you")
    print("      nothing for a change nobody anticipated.")

    print("\n-- both designs still work --")
    for name, system in (("flat", Flat()), ("split", Split())):
        system.register("Ivan", course)
        system.set_grade("Ivan", "c01", "6")
        check(f"{name}: transcript", system.transcript("Ivan"),
              [("c01", "6")])
        check(f"{name}: graded rows are settled", system.outstanding(), 0)
        system.register("Maria", course)
        check(f"{name}: ungraded row is outstanding",
              system.outstanding(), 120)

    print("\n-- so what do you actually buy --")
    print("   LOW COUPLING  buys you a smaller blast radius on the changes")
    print("                 you predicted. Look at measurement 1: the count")
    print("                 was equal, but in Flat you edit pricing while")
    print("                 looking at storage and messaging.")
    print("   HIGH COHESION buys you a method you can read in one breath.")
    print("                 Pricing.fee_for is one line about money. That is")
    print("                 the real difference, and it is not a number.")
    print("   AND THE BILL  measurement 3 is 5 against 5. Split anticipated")
    print("                 pricing changing and was rewarded. It never")
    print("                 anticipated the row shape changing and got")
    print("                 nothing. You cannot decouple along every axis -")
    print("                 that is just a program with no structure.")
