"""SESSION 17 - MVC, with no framework.

    python 17_mvc.py          run the checks
    python 17_mvc.py serve    real web server on http://localhost:8000/courses

WHY NO FRAMEWORK
    A framework would do the interesting part for you. Python's standard
    library has an HTTP server. 80 lines and you own every piece.

THE THREE PARTS
    Model      data and rules. Does not know the web exists.
    View       data -> HTML. No decisions.
    Controller reads the request, calls the model, picks a view.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Write the escaping check FIRST, before any HTML exists:
                nasty = Catalog([Course("x", "<script>", "informatics", 5)])
                page = CourseController(nasty).index({"query": {}})
                check("view escapes html", "<script>" in page["body"], False)
            WHY THIS ONE BEFORE THE PRETTY ONES: it is the only check here
            that is a security bug if it fails. Write it first and the view
            is born escaping. Write it last and you are retrofitting
            html.escape() into a template you have already got attached to -
            which is exactly how this bug reaches production everywhere.

    STEP 2  is_full and seats_left on Course - in the MODEL, not the view.
            WHY THERE: the view asks "is this full" and does not get to have
            an opinion. Put that comparison in the template and a CLI
            written next month cannot reuse it. This is the twist below,
            and we are dodging it on purpose so everyone can feel the
            difference later.

    STEP 3  course_list(). Data in, HTML string out, and NO decisions.
            WHY "no decisions" is a rule and not a style: the moment a view
            decides something, that decision is only true for people
            arriving over HTTP.

    STEP 4  CourseController.index. Takes a dict, returns a dict.
            WHY A DICT AND NOT A REAL REQUEST OBJECT: because then you can
            check the controller with no server running, which is what every
            check below does. Session 02's seam, at the edge of the web.

    STEP 5  Run `python 17_mvc.py serve` and open it in a browser. Same
            controller, same code, real HTTP.
            WHY BOTHER: it proves the dict was not a toy. The checks were
            exercising the real thing all along.

YOUR JOB (25 min)
    1. Finish Course.is_full / seats_left and Catalog.by_faculty.
    2. Finish course_list() - it must ESCAPE user text.
    3. Finish CourseController.index (with ?faculty=) and .show (404 path).
    Note the controller takes a dict and returns a dict, so you can check it
    with no server running. That is deliberate.

THE TWIST (next session's whole topic)
    Put "is this course full" logic in the controller. It works. Now add a CLI
    that needs the same rule. You cannot reuse it - it is trapped in the web
    layer. That is the fat controller problem.

THE DOWNSIDE
    MVC says nothing about where business logic goes. Every fat-controller
    codebase you will inherit was written by someone following MVC correctly.
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

        # ---- NOW YOU WRITE THE REST --------------------------------------
        # Build a CourseController(Catalog()) and check:
        #
        #   "index status"            page["status"] for an empty query
        #   "index lists everything"  "Roman Law" appears in page["body"]
        #
        #   "filters by faculty"      with {"query": {"faculty": "law"}},
        #                             Roman Law is present AND Databases is
        #                             absent. Check BOTH IN ONE check, as a
        #                             tuple.
        #                             WHY BOTH: "the filter shows law" also
        #                             passes for a filter that shows
        #                             everything. A filter is only proven by
        #                             what it LEAVES OUT.
        #
        #   "missing course is 404"   controller.show with id "nope".
        #                             WHY A STATUS AND NOT AN EXCEPTION: on
        #                             the web, "not found" is a normal
        #                             answer, not a crash. The controller's
        #                             job is turning an absence into a
        #                             response.
        #
        #   "full course marked"      "FULL" appears in the index body.
        #                             Databases is 30 of 30.
        #
        # STRETCH: add ?faculty=nosuchfaculty. What SHOULD happen - empty
        #          table, or 404? Decide, write the check, then implement.
