"""SESSION 23 - A message queue made of files.

    python 23_queue.py            the checks
    python 23_queue.py worker     run a worker      (terminal 1)
    python 23_queue.py produce 5  enqueue 5 jobs    (terminal 2)
    python 23_queue.py crash      at-least-once delivery, demonstrated

THE SITUATION
    Charging 4000 students at the end of term cannot happen inside a web
    request. You need to hand the work to something else and let it get on
    with it.

    So: a folder of files. Open it in a file manager and leave it on screen -
    this is the only broker you will ever use that you can WATCH. Everything
    here is true of RabbitMQ, SQS and Kafka; they just hide it behind a daemon.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. enqueue(payload) - a uuid in the filename, JSON in the file.
       A uuid, not a counter: two producers both think they are writing
       message 4. A counter needs coordination; a uuid needs nothing.
    2. claim() - os.rename the file into processing/.
       RENAME, not read-then-delete. Rename within one filesystem is ATOMIC:
       the OS guarantees exactly one of two racing workers wins.
       Read-then-delete has a gap between the two steps, and the gap is where
       the second worker gets in.
    3. ack(message) - delete it from processing/.
    4. recover() - move orphans back to ready/, return how many.
    5. IdempotentLedger.charge - no-op if that message id was already applied.
    6. Write the six remaining checks at the bottom.

THE PART THAT MATTERS
    Run `python 23_queue.py crash`. The worker dies AFTER doing the work but
    BEFORE acking. The message comes back. The work happens twice.

    That is AT-LEAST-ONCE DELIVERY, every real queue gives you it, and the fix
    is NOT in the queue - it is your handler being idempotent. Compare Ledger
    with IdempotentLedger and say out loud which one you would deploy.

THE COST
    You now have a system where "it succeeded" and "we know it succeeded" are
    different facts. Every distributed system lives with this permanently.
"""
import json
import os
import shutil
import sys
import time
import uuid
from check import check


class FileQueue:
    def __init__(self, root="queue"):
        self.root = root
        self.ready = os.path.join(root, "ready")
        self.processing = os.path.join(root, "processing")
        for folder in (self.ready, self.processing):
            os.makedirs(folder, exist_ok=True)

    def enqueue(self, payload):
        raise NotImplementedError    # TODO: unique id, write JSON to ready/

    def claim(self):
        raise NotImplementedError    # TODO: os.rename into processing/

    def ack(self, message):
        raise NotImplementedError    # TODO: delete from processing/

    def recover(self):
        raise NotImplementedError    # TODO: orphans back to ready/, return n

    def depth(self):
        return len(os.listdir(self.ready))


class Ledger:
    """Naive: running the same message twice charges twice."""

    def __init__(self):
        self.charges = []

    def charge(self, student, amount):
        self.charges.append((student, amount))


class IdempotentLedger:
    """Safe: remembers which message ids it has already applied."""

    def __init__(self):
        self.charges = []
        self.applied = set()

    def charge(self, student, amount, message_id):
        raise NotImplementedError    # TODO: no-op if already applied


def worker():
    queue = FileQueue()
    ledger = IdempotentLedger()
    recovered = queue.recover()
    if recovered:
        print(f"recovered {recovered} messages from a previous crash")
    print("worker running - ctrl-c to stop")
    while True:
        message = queue.claim()
        if message is None:
            time.sleep(0.3)
            continue
        payload = message["payload"]
        ledger.charge(payload["student"], payload["amount"], message["id"])
        print(f"charged {payload['student']} {payload['amount']:.2f} lv")
        queue.ack(message)


def crash_demo():
    for handler_name in ("naive", "idempotent"):
        shutil.rmtree("crash-queue", ignore_errors=True)
        queue = FileQueue("crash-queue")
        queue.enqueue({"student": "s001", "amount": 120.0})
        print(f"\n--- {handler_name} handler ---")
        ledger = Ledger() if handler_name == "naive" else IdempotentLedger()

        message = queue.claim()
        if handler_name == "naive":
            ledger.charge(message["payload"]["student"],
                          message["payload"]["amount"])
        else:
            ledger.charge(message["payload"]["student"],
                          message["payload"]["amount"], message["id"])
        print("work done. worker crashes before ack...")
        queue.recover()
        message = queue.claim()
        if handler_name == "naive":
            ledger.charge(message["payload"]["student"],
                          message["payload"]["amount"])
        else:
            ledger.charge(message["payload"]["student"],
                          message["payload"]["amount"], message["id"])
        queue.ack(message)
        print("charges:", ledger.charges)
    shutil.rmtree("crash-queue", ignore_errors=True)
    print("\nThe queue did not change. The handler did.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "worker":
        worker()
    elif mode == "produce":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        q = FileQueue()
        for i in range(n):
            q.enqueue({"student": f"s{i + 1:03d}", "amount": 120.0})
        print(f"enqueued {n}, queue depth {q.depth()}")
    elif mode == "crash":
        crash_demo()
    else:
        print("SESSION 23 - file queue")
        shutil.rmtree("check-queue", ignore_errors=True)
        q = FileQueue("check-queue")

        # ---- STEP 2: the check that is the whole reason a queue is hard --
        q.enqueue({"student": "s001", "amount": 10.0})
        msg = q.claim()
        check("two workers cannot claim the same message", q.claim(), None)

        # YOUR TURN - write one check for each, then make them pass:
        #   enqueue then claim         msg["payload"]["student"]
        #   claim removes from ready   q.depth() after the claim above
        #   ack deletes                q.ack(msg), then list
        #                              check-queue/processing - must be []
        #
        # Then the part that matters:
        #   crash redelivers           enqueue, claim, and NEVER ack - that
        #                              is exactly what a crashed worker
        #                              leaves behind. q.recover() returns
        #                              how many it rescued.
        #   redelivered is claimable   and it can be claimed again
        #   naive handler double charges
        #                              Ledger, same charge twice. Note the
        #                              expected number here IS the bug -
        #                              this check pins down broken
        #                              behaviour so the next line can show
        #                              the fix.
        #   idempotent handler does not
        #                              IdempotentLedger, same message_id
        #                              twice. The queue cannot promise
        #                              once-only delivery - no queue can.
        #                              It can only promise the id stays the
        #                              same. Your handler turns that into
        #                              safety.
