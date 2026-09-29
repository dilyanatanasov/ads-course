"""SESSION 16 - Layers, and a check that ENFORCES them.

    python 16_layers.py

THE IDEA
    16_domain.py          the rules. Knows about nothing else.
    16_application.py     the use cases. Knows domain.
    16_infrastructure.py  database, email, HTTP. Knows both.

    One rule - the DEPENDENCY RULE: arrows point inwards only.
    domain may NEVER import infrastructure.

WHY THIS SESSION IS DIFFERENT
    Everybody draws this diagram. Almost nobody enforces it, so six months
    later domain imports a database driver and the diagram is a lie.
    Today you write a check that FAILS when someone breaks the rule. It parses
    the import statements with ast, in about 20 lines.

READ IT TOGETHER (20 min - no TODOs today, and that is deliberate)
    STEP 1  Open 16_domain.py and read the imports. There are none.
            WHY AN EMPTY IMPORT LIST IS THE MOST IMPORTANT LINE IN THE
            PROJECT: it is the only layer whose correctness does not depend
            on anything else existing. You can reason about may_enrol_in()
            without knowing whether there is a database, a web server, or a
            company.

    STEP 2  Open 16_application.py. EnrolStudent takes students, courses and
            notifier as parameters and never constructs one.
            WHY: it is session 07's fix, promoted to an architectural rule.
            The use case declares what it needs; somebody further out
            decides what those actually are.

    STEP 3  Ask the room the question that makes it land: where is the
            database? There isn't one. The checks below enrol a real student
            in a real course with real rules and no storage at all.
            WHY THAT IS POSSIBLE: the rules were never entangled with the
            storage in the first place. That is the payoff, and it is worth
            sitting with for a moment.

    STEP 4  Read dependency_violations() together. It parses each layer's
            imports with ast and compares them against ALLOWED.
            WHY THIS EXISTS AT ALL: everybody draws this diagram. Almost
            nobody enforces it, so in six months domain imports a database
            driver, and the diagram on the wiki quietly becomes fiction.
            Twenty lines turn the diagram into something that can FAIL.

    STEP 5  Now break it on purpose - step 3 of YOUR JOB below. Watch the
            check name the offender.
            WHY BREAKING IT IS THE EXERCISE: a check you have never seen go
            red is decoration. You do not know it works, you only know it is
            green, and those are different facts.

YOUR JOB (25 min)
    1. Read the three layer files. Understand why enrol works with no database.
    2. Run this file. Green.
    3. Now BREAK it deliberately: add `import importlib` +
       `importlib.import_module("16_infrastructure")` to 16_domain.py.
       Run again. Watch it name the offender. Then undo.

THE DOWNSIDE
    Four files for a 200-line program is absurd, and you will meet codebases
    where the ceremony costs more than it saves. Adopt layers when more than
    one person changes the code, or when there is more than one way in
    (web + CLI + scheduled job).
"""
import ast
import importlib
import os
from check import check, check_raises

domain = importlib.import_module("16_domain")
application = importlib.import_module("16_application")
infrastructure = importlib.import_module("16_infrastructure")

ALLOWED = {
    "16_domain": set(),
    "16_application": {"16_domain"},
    "16_infrastructure": {"16_domain", "16_application"},
}


def dependency_violations():
    """Architecture as a check. The cheapest governance that exists."""
    here = os.path.dirname(os.path.abspath(__file__))
    violations = []
    for layer, allowed in ALLOWED.items():
        path = os.path.join(here, layer + ".py")
        if not os.path.exists(path):
            continue
        with open(path) as handle:
            tree = ast.parse(handle.read(), filename=path)
        referenced = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                referenced |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                referenced.add(node.module.split(".")[0])
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in ALLOWED:        # importlib.import_module("x")
                    referenced.add(node.value)
        for other in referenced & set(ALLOWED):
            if other != layer and other not in allowed:
                violations.append(f"{layer}.py imports {other}")
    return violations


if __name__ == "__main__":
    print("SESSION 16 - layers")

    students = infrastructure.InMemoryStudents([
        domain.Student("s001", "Ivan", "informatics", credits=60),
        domain.Student("s002", "Maria", "informatics", credits=10),
    ])
    courses = infrastructure.InMemoryCourses([
        domain.Course("c01", "Software Architecture", seats=1,
                      required_credits=30)])
    notifier = infrastructure.RecordingNotifier()
    enrol = application.EnrolStudent(students, courses, notifier)

    check("eligible student enrols", enrol("s001", "c01"), True)
    check("notified once", len(notifier.messages), 1)
    check_raises("ineligible student rejected", domain.NotEligible,
                 enrol, "s002", "c01")

    students.add(domain.Student("s003", "Georgi", "informatics", credits=90))
    check_raises("full course rejected", domain.CourseFull,
                 enrol, "s003", "c01")

    print("\n-- the dependency rule --")
    violations = dependency_violations()
    check("arrows point inwards only", violations, [])
    if violations:
        for line in violations:
            print("        " + line)
