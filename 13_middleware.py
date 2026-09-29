"""SESSION 13 - Middleware chain.

    python 13_middleware.py

WHY THIS ONE MATTERS
    This is not academic. This IS Express, Django and ASP.NET Core. After today
    you will recognise the shape in their documentation.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Check the bare application first, with no middleware at all:
                check("plain app", application(request())["status"], 200)
            WHY BOTHER CHECKING THE OBVIOUS: in ten minutes something will
            return 401 and you will need to know whether the app underneath
            still works. This line is the one that answers that instantly.
            The cheapest debugging tool is a check on the thing you were
            sure about.

    STEP 2  AuthMiddleware alone. No token -> 401 and DO NOT call self.next.
            WHY THE EARLY RETURN IS THE INTERESTING LINE: a middleware that
            can refuse to pass the request on is a middleware that can
            protect everything behind it. If it always called next, it would
            be a logger, not a guard.

    STEP 3  Now read call() at the top, and notice it accepts either an
            object with .handle or a plain function.
            WHY THAT SMALL UGLINESS EXISTS: it lets the chain end in the
            plain application function without the application knowing it is
            in a chain. The last thing in a pipeline should never need to
            know it is last.

    STEP 4  LoggingMiddleware. Record AFTER the call, not before.
            WHY AFTER: before the call you know the path. Only after it do
            you know the status. A middleware sees the request on the way in
            AND the response on the way out - that two-sided shape is the
            whole reason this is a chain and not a list of validators.

    STEP 5  build(). Now argue about order before writing it: auth first, or
            rate limit first? Take a vote, then write the check that settles
            it - flood the chain with UNAUTHENTICATED requests, then send a
            good one and see whether it still gets through.
            WHY THIS IS NOT A STYLE QUESTION: one order lets anyone on the
            internet exhaust a real user's budget without ever logging in.
            The other does not. Same components, same code, one is a
            vulnerability. Order is not cosmetic.

YOUR JOB (25 min)
    Each middleware may inspect the request, reject it, pass it on, and inspect
    the response on the way back.
    1. LoggingMiddleware  - records path and final status
    2. AuthMiddleware     - no token -> 401
    3. RateLimitMiddleware- over the limit -> 429
    4. build()            - assemble the chain

    STRETCH: which order? Auth before rate limiting, or after? One of those
    lets an unauthenticated flood eat a real user's budget. The last check
    tests for it.

THE DOWNSIDE
    A request now passes through five functions before anything useful happens.
    When one mysteriously returns 401, the cause is in a file you did not open,
    registered in a list you did not write.
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

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    # One middleware at a time. Do not write build() until the three pieces
    # pass on their own - a broken chain has three suspects.
    #
    #   "auth rejects no token"   AuthMiddleware(application) with
    #                             request(token=None) -> status 401
    #   "auth allows a token"     ...with a token -> 200
    #
    #   "rate limit"              RateLimitMiddleware(application, limit=3),
    #                             four requests in a row. Check the WHOLE
    #                             list of statuses, not just the last one.
    #                             WHY THE LIST: [200, 200, 200, 429] proves
    #                             it blocks the fourth AND allows the first
    #                             three. Checking only the last would pass
    #                             for a middleware that blocks everything.
    #
    #   "log sees the response too"
    #                             LoggingMiddleware(application), one
    #                             request, then check log.entries holds the
    #                             path AND the status: [("/courses", 200)].
    #
    #   "full chain allows" / "full chain rejects"
    #                             build(application), then a good request
    #                             and a token-less one.
    #
    # ---- AND THE ONE THAT DECIDES THE ORDER ------------------------------
    #   "unauth flood did not eat the budget"
    #       build(application, limit=2). Send FIVE requests with no token.
    #       Then send one good request and check it still gets 200.
    #       Write this check BEFORE you decide the order in build(). Get the
    #       order wrong and an anonymous flood locks out a paying student -
    #       and you will see it here, in a classroom, rather than in an
    #       incident report.
