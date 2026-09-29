"""SESSION 16 - Layers, and a check that ENFORCES them.

    python 16_layers.py

NOTHING TO IMPLEMENT TODAY
    No TODOs. You read three files, then break one on purpose.

THE SITUATION
    Four files instead of one:

        16_domain.py          the rules. Knows about nothing else.
        16_application.py     the use cases. Knows domain.
        16_infrastructure.py  database, email, HTTP. Knows both.
        16_layers.py          this file: the checks, and the rule-enforcer.

    ONE rule, the DEPENDENCY RULE: arrows point inwards only. domain may
    NEVER import infrastructure.

WHY THIS SESSION IS DIFFERENT
    Everybody draws this diagram. Almost nobody enforces it, so six months
    later domain imports a database driver and the diagram on the wiki is
    quietly fiction. Here the rule is a CHECK that fails and names the
    offender, in about twenty lines of ast.

YOUR TASK (25 min)
    1. Open 16_domain.py and look at its imports. There are none. That is the
       most important line in the project - it means you can reason about the
       rules without knowing whether a database exists.

    2. Open 16_application.py. EnrolStudent is HANDED students, courses and a
       notifier; it never constructs one. That is session 07's fix promoted to
       an architectural rule.

    3. Run this file. Green. Now answer: where is the database? There isn't
       one. The checks enrol a real student under real rules with no storage
       at all, because the rules were never tangled up with the storage.

    4. Read dependency_violations(). Then BREAK the rule on purpose: add
       `import importlib` and `importlib.import_module("16_infrastructure")`
       to 16_domain.py. Run again and watch the check name the offender.
       Then undo it.

    Step 4 is the exercise. A check you have never seen go red is decoration -
    you know it is green, which is not the same as knowing it works.

THE COST
    Four files for a 200-line program is absurd, and you will meet codebases
    where the ceremony costs more than it saves. Adopt layers when more than
    one person changes the code, or when there is more than one way in -
    web plus CLI plus a scheduled job.
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
