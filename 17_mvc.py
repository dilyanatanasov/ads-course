"""SESSION 17 - MVC, with no framework.

    python 17_mvc.py          the checks
    python 17_mvc.py serve    a real web server on http://localhost:8000/courses

THE SITUATION
    You need a web page listing courses, filterable by faculty, showing which
    are full. A framework would do the interesting part for you. Python's
    standard library has an HTTP server, so 80 lines and you own every piece.

THE THREE PARTS
    Model       data and rules. Does not know the web exists.
    View        data in, HTML out. Makes no decisions.
    Controller  reads the request, asks the model, picks a view.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. Course.is_full and Course.seats_left - in the MODEL, not the view.
    2. Catalog.by_faculty.
    3. course_list() - a table. Status is "FULL" or "N left". ESCAPE every
       value that came from outside.
    4. CourseController.index (with ?faculty=) and .show (404 when missing).
    5. Write the five remaining checks at the bottom.

    The escaping check is the one to write FIRST. It is the only one here that
    is a security hole if it fails, and writing it first means the view is
    born escaping instead of having html.escape() retrofitted into a template
    you have grown attached to.

    The controller takes a dict and returns a dict, so you can check it with
    no server running. That is deliberate - it is session 02's seam at the
    edge of the web.

THE COST
    MVC says nothing about where business logic goes. Put "is this course
    full" in the controller and it works - until a CLI needs the same rule
    and cannot reach it. Every fat-controller codebase you will inherit was
    written by someone following MVC correctly.
"""
import html
import sys
from check import check


# ---- MODEL ---------------------------------------------------------------
class Course:
    def __init__(self, cid, title, faculty, seats, taken=0):
        self.id, self.title, self.faculty = cid, title, faculty
        self.seats, self.taken = seats, taken

    @property
    def is_full(self):
        raise NotImplementedError    # TODO

    @property
    def seats_left(self):
        raise NotImplementedError    # TODO


class Catalog:
    def __init__(self, courses=None):
        self.courses = courses or [
            Course("c01", "Databases", "informatics", 30, 30),
            Course("c02", "Computer Networks", "informatics", 25, 11),
            Course("c03", "Roman Law", "law", 40, 4),
        ]

    def all(self):
        return list(self.courses)

    def by_faculty(self, faculty):
        raise NotImplementedError    # TODO

    def get(self, cid):
        for course in self.courses:
            if course.id == cid:
                return course
        return None


# ---- VIEW ----------------------------------------------------------------
def course_list(courses, heading="Courses"):
    # TODO: a table. Status is "FULL" or "N left". ESCAPE every value.
    raise NotImplementedError


def not_found(what):
    return f"<h1>Not found</h1><p>No such thing: {html.escape(what)}</p>"


# ---- CONTROLLER ----------------------------------------------------------
class CourseController:
    def __init__(self, catalog):
        self.catalog = catalog

    def index(self, request):
        raise NotImplementedError    # TODO: ?faculty= filters

    def show(self, request):
        raise NotImplementedError    # TODO: 404 when missing


def serve():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs
    controller = CourseController(Catalog())
    routes = {"/courses": controller.index, "/course": controller.show}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            action = routes.get(parsed.path)
            response = (action({"path": parsed.path, "query": query})
                        if action else {"status": 404, "body": "<h1>404</h1>"})
            body = response["body"].encode("utf-8")
            self.send_response(response["status"])
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    print("http://localhost:8000/courses  (ctrl-c to stop)")
    HTTPServer(("localhost", 8000), Handler).serve_forever()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
    else:
        print("SESSION 17 - mvc")

        # ---- STEP 1: the check we wrote first, because it is the only ----
        # ---- one here that is a security bug when it fails ---------------
        nasty = Catalog([Course("x", "<script>", "informatics", 5)])
        page = CourseController(nasty).index({"query": {}})
        check("view escapes html", "<script>" in page["body"], False)

        # YOUR TURN - build a CourseController(Catalog()) and write one
        # check for each, then make them pass:
        #   index status              page["status"] for an empty query
        #   index lists everything    "Roman Law" is in page["body"]
        #   filters by faculty        with {"faculty": "law"}, Roman Law is
        #                             present AND Databases is absent. Check
        #                             BOTH in one check, as a tuple - a
        #                             filter is only proven by what it
        #                             leaves out.
        #   missing course is 404     controller.show with id "nope". On the
        #                             web, "not found" is a normal answer,
        #                             not a crash.
        #   full course marked        "FULL" appears in the index body -
        #                             Databases is 30 of 30.
