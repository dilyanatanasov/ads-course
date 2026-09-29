"""SESSION 13 - Middleware chain.

    python 13_middleware.py

THE SITUATION
    Every request to the course list needs three things that have nothing to
    do with course lists: check the token, refuse callers who ask too often,
    and log what happened. Putting all three inside the handler means writing
    them again in the next handler, and the one after that.

THE IDEA
    A chain. Each link may inspect the request, refuse it, pass it on, and
    inspect the response on the way back. The handler at the end never learns
    it was in a chain.

    This is not academic. This IS Express, Django and ASP.NET Core - after
    today you will recognise the shape in their documentation.

YOUR TASK (25 min)
    1. AuthMiddleware      - no token -> 401, and do NOT call self.next.
    2. RateLimitMiddleware - over the limit -> 429.
    3. LoggingMiddleware   - record (path, status) AFTER the call. Before it
                             you know the path; only after do you know the
                             status.
    4. build(app, limit)   - assemble the chain. The ORDER MATTERS, and
                             deciding it is the real task. Auth before rate
                             limiting, or after? One of those two lets an
                             anonymous flood use up a paying student's budget.
                             Vote on it, then write the last check and find out.
    5. Write the seven remaining checks at the bottom.

    Build one middleware at a time and check it alone. A broken chain has
    three suspects.

THE COST
    A request now passes through four functions before anything useful
    happens. When one mysteriously returns 401, the cause is in a file you
    did not open, registered in a list you did not write.
"""
from check import check


def application(request):
    return {"status": 200, "body": "course list for " + request["path"]}


def call(handler, request):
    """The next thing may be a middleware object or a plain function."""
    return (handler.handle(request) if hasattr(handler, "handle")
            else handler(request))


class Middleware:
    def __init__(self, next_handler):
        self.next = next_handler

    def handle(self, request):
        raise NotImplementedError


class LoggingMiddleware(Middleware):
    def __init__(self, next_handler):
        super().__init__(next_handler)
        self.entries = []

    def handle(self, request):
        raise NotImplementedError    # TODO: record (path, status) AFTER

class AuthMiddleware(Middleware):
    def handle(self, request):
        raise NotImplementedError    # TODO


class RateLimitMiddleware(Middleware):
    def __init__(self, next_handler, limit=3):
        super().__init__(next_handler)
        self.limit = limit
        self.seen = 0

    def handle(self, request):
        raise NotImplementedError    # TODO


def build(app, limit=100):
    raise NotImplementedError        # TODO: in which order?


def request(path="/courses", token="abc"):
    return {"path": path, "token": token}


if __name__ == "__main__":
    print("SESSION 13 - middleware")

    # ---- STEP 1: the boring check that earns its place in ten minutes ----
    check("plain app", application(request())["status"], 200)

    # YOUR TURN - write one check for each, then make them pass. One
    # middleware at a time; do not write build() until the three pass alone.
    #
    #   auth rejects no token   AuthMiddleware(application) with
    #                           request(token=None) -> 401
    #   auth allows a token     ...with a token -> 200
    #   rate limit              RateLimitMiddleware(application, limit=3),
    #                           four requests. Check the WHOLE list of
    #                           statuses, not just the last - checking only
    #                           the last would pass for a middleware that
    #                           blocks everything.
    #   log sees the response   LoggingMiddleware, one request, then check
    #                           log.entries holds the path AND the status
    #   full chain allows       build(application), good request -> 200
    #   full chain rejects      ...token-less -> 401
    #
    # AND THE ONE THAT DECIDES THE ORDER:
    #   unauth flood did not eat the budget
    #       build(application, limit=2). Send FIVE token-less requests, then
    #       one good one, and check it still gets 200. Get the order wrong
    #       and an anonymous flood locks out a paying student - here, in a
    #       classroom, rather than in an incident report.
