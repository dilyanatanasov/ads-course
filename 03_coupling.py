"""SESSION 03 - Coupling and cohesion, measured.

    python 03_coupling.py

Most courses define these two words and move on. Today you get a number.

    COUPLING  how much one thing depends on another
    COHESION  how much the things inside one class belong together

BLAST RADIUS
    Pick a change. Count the methods you must edit to make it. That number is
    your coupling, and unlike the definition you can argue about it with
    evidence. blast_radius() below counts for you, using ast.

BUILD IT TOGETHER (12 min - we read blast_radius() line by line)
    Today is the one session where we do not write the tool, we read it. It
    is 15 lines and it is the only honest thing in this course.

    STEP 1  Read blast_radius(). It parses each class with ast and asks, per
            method: does this method mention that name?
            WHY AST AND NOT A TEXT SEARCH: ctrl-F finds the word "fee" in a
            comment, in a docstring, in the string "coffee". The parser knows
            the difference between a NAME and some letters. When you measure
            something, the measurement has to be harder to fool than the
            thing it measures.

    STEP 2  Before running anything, PREDICT out loud. Write the numbers on
            the board. To change the pricing rule: how many methods in Flat?
            How many in Split?
            WHY PREDICT FIRST: if you look at the number before committing to
            a guess, you will find it obvious and learn nothing. A prediction
            you got wrong is worth ten you never made.

    STEP 3  Run it. Compare with the board.

    STEP 4  Now look at measurement 3 - renaming `grade` - and predict again.
            WHY THIS ONE MATTERS MOST: it is the measurement where the
            "better" design wins nothing. Do not let anyone skip past it.

YOUR JOB (25 min)
    Two designs do the same job. Flat is written the way session 01 was.
    Split separates pricing from enrolling.

    1. Run the file and read the three measurements.
    2. Change the fee to 25 lv per credit. Do it in BOTH designs, timing
       yourself. The last two checks go green when you are done.
    3. Before running it - PREDICT the blast radius of adding VAT. Then
       measure.

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

    print("\n1. TO CHANGE THE PRICING RULE, WHICH METHOD DO YOU OPEN?")
    show("Flat", ["Flat.register"])
    show("Split", ["Pricing.fee_for"])
    print("      Flat.register also stores a row and sends a message.")
    print("      Pricing.fee_for does one thing. Same edit, different risk.")

    print("\n2. HOW MANY METHODS READ THE FEE? (same in both - and\n      that is fine. READING a value is not coupling to the RULE.)")
    show("Flat", blast_radius("fee", Flat))
    show("Split", blast_radius("fee", Split, Enrolment, Pricing))

    print("\n3. THE HONEST ONE - rename the grade field")
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

    print("\n-- TODO: make the fee 25 lv per credit in BOTH designs --")
    check("split: pricing rule is per credit", Pricing().fee_for(course), 150)
    flat = Flat()
    flat.register("Georgi", course)
    check("flat: charges per credit", flat.rows[0]["fee"], 150)
