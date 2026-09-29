"""SESSION 24 - Microservices in three terminal windows. No Docker.

    python 24_services.py students   # terminal 1, port 8001
    python 24_services.py courses    # terminal 2, port 8002
    python 24_services.py gateway    # terminal 3, port 8000
    curl http://127.0.0.1:8000/enrolment?student=s001

    python 24_services.py            # checks: starts all three itself

WHY THIS COUNTS AS DISTRIBUTED
    Three processes, own SQLite file each, talking over HTTP. Network calls,
    independent deployment, partial failure, separate data. Every property
    that matters.

READ IT TOGETHER (20 min - no TODOs today, and that is deliberate)
    STEP 1  Three terminals, three commands, before any explanation. Then
            curl the gateway.
            WHY START BY RUNNING IT: "microservices" sounds like a thing you
            need a platform team for. It is three processes and a port
            number. Deflate it first, respect it afterwards.

    STEP 2  Look at db() and count the databases. Two, in two folders.
            Now try to make the students service answer a question about
            course titles. You cannot - it has no table for them and no
            connection to the other one.
            WHY THE ENFORCEMENT IS PHYSICAL: in session 16 the dependency
            rule needed a check to enforce it. Here a separate PROCESS
            enforces it. Nobody can take a shortcut, because the shortcut
            does not exist. That is the real thing you are buying.

    STEP 3  Read the HOST and CLIENT_TIMEOUT comments at the top of this
            file. Both were real bugs in this exact file, and both are
            failure modes that do not exist in a single program.

    STEP 4  Read enrolment() and find the two fetches. One failure is fatal,
            the other is not.
            WHY THAT ASYMMETRY IS A DESIGN DECISION, NOT A DETAIL: somebody
            decided a student's page is still worth showing without course
            TITLES, but worthless without the student. Ask the room whether
            they agree. There is no technical answer - it is a product
            judgement that you are now required to make, in code, because
            you split the system up.

    STEP 5  Kill terminal 2 while the page is loading. Watch it degrade.
            Then read the "warning" field in the JSON.
            WHY THE WARNING MATTERS: the response is incomplete AND SAYS SO.
            A degraded answer that pretends to be a full one is worse than
            an error.

YOUR JOB (25 min)
    1. Read it. Note each service owns its own database and cannot read the
       other's.
    2. Add a course to the courses service. The students service neither knows
       nor cares.
    3. NOW BREAK IT: kill terminal 2 and call the gateway again.
       - What does the user see? How long did they wait?
       - Should the whole page fail because course NAMES are missing?

    The gateway already degrades gracefully - read `enrolment()` and see how.
    Compare with session 01, where this failure mode could not exist.

THE DOWNSIDE, IN ONE SENTENCE
    You turned a function call that could not fail into a network call that can
    fail in eight ways, on purpose - so know what you bought.
"""
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 1.0

# 127.0.0.1, never "localhost", and this is not pedantry.
# On many machines "localhost" resolves to ::1 (IPv6) first. If nothing is
# listening on ::1, some systems REFUSE instantly - fine - but others silently
# DROP the packet, so the client sits there for the full timeout before
# retrying on IPv4. On this course's Windows boxes that is ~2 seconds PER CALL.
# The gateway makes two calls to answer one request, so a 1-second client
# timeout could never succeed and the whole session looked broken.
# Your first distributed-systems bug, and it was a name resolution detail.
HOST = "127.0.0.1"
BASE = f"http://{HOST}"

# TIMEOUT BUDGETS NEST, and getting this wrong is a classic outage.
# The gateway spends up to TIMEOUT waiting on students, then up to TIMEOUT
# waiting on courses. So answering ONE gateway request can take 2 x TIMEOUT.
# A caller that also waits only TIMEOUT gives up before the gateway has even
# finished degrading - and reports "gateway down" when the gateway is fine.
# Rule: the caller's patience must exceed the sum of everything it waits on.
CLIENT_TIMEOUT = TIMEOUT * 4


def serve(port, routes, name):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            action = routes.get(parsed.path)
            if action is None:
                payload, status = {"error": "not found"}, 404
            else:
                try:
                    payload, status = action(query), 200
                except Exception as exc:              # noqa: BLE001
                    payload, status = {"error": str(exc)}, 500
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    print(f"{name} on http://127.0.0.1:{port}")
    HTTPServer((HOST, port), Handler).serve_forever()


def db(folder, schema):
    path = os.path.join(HERE, folder)
    os.makedirs(path, exist_ok=True)
    conn = sqlite3.connect(os.path.join(path, "data.db"))
    for statement in schema:
        conn.execute(statement)
    conn.commit()
    return conn


# ---- students service (port 8001) ---------------------------------------
def students_service():
    schema = ["CREATE TABLE IF NOT EXISTS students ("
              " id TEXT PRIMARY KEY, name TEXT, faculty TEXT)",
              "CREATE TABLE IF NOT EXISTS enrolments (student TEXT,"
              " course TEXT)"]
    conn = db("students_db", schema)
    conn.executemany("INSERT OR REPLACE INTO students VALUES (?, ?, ?)",
                     [("s001", "Ivan", "informatics"),
                      ("s002", "Maria", "law")])
    conn.execute("DELETE FROM enrolments")
    conn.executemany("INSERT INTO enrolments VALUES (?, ?)",
                     [("s001", "c01"), ("s001", "c02"), ("s002", "c03")])
    conn.commit()

    def student(query):
        row = conn.execute("SELECT id, name, faculty FROM students"
                           " WHERE id = ?", (query.get("id"),)).fetchone()
        if row is None:
            return {"error": "no such student"}
        courses = [r[0] for r in conn.execute(
            "SELECT course FROM enrolments WHERE student = ?",
            (query.get("id"),)).fetchall()]
        return {"id": row[0], "name": row[1], "faculty": row[2],
                "course_ids": courses}

    serve(8001, {"/student": student,
                 "/health": lambda q: {"status": "up"}}, "students")


# ---- courses service (port 8002) ----------------------------------------
def courses_service():
    conn = db("courses_db", ["CREATE TABLE IF NOT EXISTS courses ("
                             " id TEXT PRIMARY KEY, title TEXT, seats INT)"])
    conn.executemany("INSERT OR REPLACE INTO courses VALUES (?, ?, ?)",
                     [("c01", "Databases", 30),
                      ("c02", "Software Architecture", 25),
                      ("c03", "Roman Law", 40)])
    conn.commit()

    def courses(query):
        wanted = [c for c in query.get("ids", "").split(",") if c]
        if wanted:
            marks = ",".join("?" * len(wanted))
            rows = conn.execute(
                f"SELECT id, title FROM courses WHERE id IN ({marks})", wanted
            ).fetchall()
        else:
            rows = conn.execute("SELECT id, title FROM courses").fetchall()
        return {"courses": [{"id": r[0], "title": r[1]} for r in rows]}

    serve(8002, {"/courses": courses,
                 "/health": lambda q: {"status": "up"}}, "courses")


# ---- gateway (port 8000) -------------------------------------------------
def fetch(url, timeout=TIMEOUT):
    """Returns (payload, error). Never raises - that is the point."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), None
    except urllib.error.URLError as exc:
        return None, f"unreachable: {exc.reason}"
    except Exception as exc:                          # noqa: BLE001
        return None, str(exc)


def gateway_service():
    def enrolment(query):
        student, error = fetch(
            f"http://127.0.0.1:8001/student?id={query.get('student', '')}"
        )
        if student is None:
            # students is ESSENTIAL - no answer is possible without it
            return {"error": "student service unavailable", "detail": error}

        ids = student.get("course_ids", [])
        courses, error = fetch(
            f"http://127.0.0.1:8002/courses?ids={','.join(ids)}"
        )
        if courses is None:
            # courses is NOT essential - degrade instead of failing
            return {"student": student["name"], "faculty": student["faculty"],
                    "courses": [{"id": c, "title": None} for c in ids],
                    "complete": False, "warning": error}

        titles = {c["id"]: c["title"] for c in courses["courses"]}
        return {"student": student["name"], "faculty": student["faculty"],
                "courses": [{"id": c, "title": titles.get(c)} for c in ids],
                "complete": True}

    def health(query):
        students, se = fetch("http://127.0.0.1:8001/health")
        courses, ce = fetch("http://127.0.0.1:8002/health")
        return {"students": "up" if students else f"DOWN ({se})",
                "courses": "up" if courses else f"DOWN ({ce})"}

    serve(8000, {"/enrolment": enrolment, "/health": health}, "gateway")


# ---- checks: start all three, then kill one ------------------------------
def run_checks():
    from check import check
    print("SESSION 24 - services (starting three processes...)")
    procs = [subprocess.Popen([sys.executable, __file__, mode], cwd=HERE,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
             for mode in ("students", "courses", "gateway")]

    def wait_for(url, seconds=8):
        deadline = time.time() + seconds
        while time.time() < deadline:
            payload, _ = fetch(url, timeout=CLIENT_TIMEOUT)
            if payload:
                return True
            time.sleep(0.15)
        return False

    try:
        for port in (8001, 8002, 8000):
            if not wait_for(f"{BASE}:{port}/health"):
                print(f"  could not start port {port}")
                return
        data, _ = fetch("http://127.0.0.1:8000/enrolment?student=s001",
                        timeout=CLIENT_TIMEOUT)
        check("gateway stitches both services", data["student"], "Ivan")
        check("answer is complete", data["complete"], True)
        check("course titles resolved",
              sorted(c["title"] for c in data["courses"]),
              ["Databases", "Software Architecture"])

        student, _ = fetch("http://127.0.0.1:8001/student?id=s001",
                           timeout=CLIENT_TIMEOUT)
        check("students service knows nothing of course titles",
              "Databases" in json.dumps(student), False)

        print("\n-- killing the courses service --")
        procs[1].terminate()
        procs[1].wait(timeout=5)
        data, _ = fetch("http://127.0.0.1:8000/enrolment?student=s001",
                        timeout=CLIENT_TIMEOUT)
        check("degrades instead of dying", data["complete"], False)
        check("still returns something useful", data["student"], "Ivan")
        check("titles are missing, not fatal", data["courses"][0]["title"],
              None)
    finally:
        for proc in procs:
            proc.terminate()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"students": students_service, "courses": courses_service,
     "gateway": gateway_service}.get(mode, run_checks)()
