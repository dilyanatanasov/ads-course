"""Run before you teach, and before you push. Stdlib only, like everything else.

    python verify.py              everything
    python verify.py --fast       skip session 24 (it starts three processes)

WHY THIS EXISTS
    Session 24 was broken for an unknown number of weeks. Every solution still
    passed, every task file still parsed, and nobody noticed, because the only
    thing that would have caught it was somebody running that one file. This
    is that somebody.

WHY NOT pytest
    Because the first line of the README promises students no pip install, and
    a course that breaks its own promise in its own repo has no standing to
    lecture anyone about design. The checks students read are 20 lines of
    print statements; so is this.

WHAT IT CHECKS
    1. every solution runs green
    2. the no-TODO sessions (01, 16, 24) run green as STUDENTS get them
    3. every task file parses
    4. reveal/ is not stale
    5. solutions/ is not tracked by git   <- the one that saves the course
"""
import ast
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOLUTIONS = os.path.join(HERE, "solutions")

# Sessions with no TODOs: students get working code and break it deliberately,
# so the file they receive must be green on arrival.
COMPLETE = ["01_baseline.py", "16_layers.py", "24_services.py"]

failures = []


def report(ok, label, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        failures.append(label)
        for line in (detail or "").strip().splitlines()[-12:]:
            print("        " + line)


def run(path, cwd, timeout=90):
    """Returns (ok, output). A session is green when it says PASS and never FAIL."""
    try:
        done = subprocess.run([sys.executable, os.path.basename(path)],
                              cwd=cwd, capture_output=True, text=True,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    output = done.stdout + done.stderr
    if done.returncode != 0:
        return False, output
    if "FAIL" in output:
        return False, output
    if "PASS" not in output:
        return False, "ran, but printed no PASS line at all\n" + output
    return True, output


def main(fast=False):
    print("1. solutions run green")
    for name in sorted(os.listdir(SOLUTIONS)):
        if name.endswith("_solution.py"):
            ok, out = run(os.path.join(SOLUTIONS, name), SOLUTIONS)
            report(ok, name, out)

    print("\n2. the no-TODO sessions are green as students receive them")
    for name in COMPLETE:
        if fast and name == "24_services.py":
            print(f"  SKIP  {name} (--fast)")
            continue
        ok, out = run(os.path.join(HERE, name), HERE)
        report(ok, name, out)

    print("\n3. every task file parses")
    broken = []
    for name in sorted(os.listdir(HERE)):
        if not (name.endswith(".py") and name[0].isdigit()):
            continue
        with open(os.path.join(HERE, name), encoding="utf-8") as handle:
            try:
                ast.parse(handle.read(), filename=name)
            except SyntaxError as exc:
                broken.append(f"{name}: {exc}")
    report(not broken, "all task files parse", "\n".join(broken))

    print("\n4. reveal/ is in sync with solutions/")
    done = subprocess.run([sys.executable, "build_reveal.py", "--check"],
                          cwd=HERE, capture_output=True, text=True)
    report(done.returncode == 0, "reveal/ is up to date", done.stdout)

    print("\n5. solutions/ has not leaked into git")
    done = subprocess.run(["git", "ls-files"], cwd=HERE,
                          capture_output=True, text=True)
    if done.returncode != 0:
        print("  SKIP  not a git repository")
    else:
        leaked = [f for f in done.stdout.splitlines()
                  if f.startswith("solutions/")]
        report(not leaked, "solutions/ is not tracked",
               "TRACKED BY GIT - students can read these:\n"
               + "\n".join(leaked))

    print()
    if failures:
        print(f"{len(failures)} PROBLEM(S). Do not teach or push this:")
        for name in failures:
            print("  - " + name)
        return 1
    print("All good.")
    return 0


if __name__ == "__main__":
    sys.exit(main(fast="--fast" in sys.argv))
