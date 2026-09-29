"""SESSION 23 - A message queue made of files.

    python 23_queue.py            checks
    python 23_queue.py worker     run a worker (terminal 1)
    python 23_queue.py produce 5  enqueue 5 messages (terminal 2)
    python 23_queue.py crash      at-least-once delivery, demonstrated

WHY A FOLDER OF FILES
    Because you can open it. A real broker hides the interesting part behind a
    daemon; a folder lets you watch messages appear, get claimed and vanish.
    Everything here transfers to RabbitMQ, SQS and Kafka.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Open the queue/ folder in a file manager and leave it on screen
            all session.
            WHY: this is the only broker you will ever use that you can
            WATCH. Every idea today is true of RabbitMQ, SQS and Kafka - you
            just cannot see them do it.

    STEP 2  Write the double-claim check before claim() exists:
                q.enqueue(...); msg = q.claim()
                check("two workers cannot claim the same message",
                      q.claim(), None)
            WHY THIS ONE FIRST: it is the entire reason a queue is harder
            than a list. Two workers, one message, and the wrong answer is
            charging a student twice.

    STEP 3  enqueue(): uuid in the filename, JSON in the file.
            WHY A UUID AND NOT A COUNTER: two producers running at once both
            think they are writing message 4. A counter needs coordination;
            a uuid needs nothing. Prefer the design with no shared state
            over the one that needs a lock.

    STEP 4  claim(): os.rename into processing/. Not read-then-delete.
            WHY RENAME IS THE WHOLE TRICK: rename within one filesystem is
            ATOMIC - the OS guarantees exactly one of two racing workers
            wins and the other gets an error. Read-then-delete has a gap
            between the two, and a gap is where the second worker gets in.
            You are not being clever here, you are borrowing a guarantee
            somebody else already proved.

    STEP 5  ack() deletes; recover() moves orphans back.
            Then run `python 23_queue.py crash` together.
            WHY IT IS THE POINT OF THE SESSION: the worker dies AFTER doing
            the work, BEFORE acking. The message comes back. The work
            happens twice. That is AT-LEAST-ONCE DELIVERY, every real queue
            gives you it, and the fix is NOT in the queue - it is that your
            handler must be idempotent. Compare Ledger with
            IdempotentLedger and say out loud which one you would deploy.

YOUR JOB (25 min)
    1. enqueue() - write a JSON file with a unique name
    2. claim()   - RENAME the file into processing/. Rename is atomic on one
                   filesystem, so two workers cannot claim the same message.
    3. ack() deletes it. recover() puts orphans back.
    4. Start two workers at once and prove no message is processed twice.

THE EXERCISE THAT MATTERS
    Run `python 23_queue.py crash`. The worker dies AFTER doing the work but
    BEFORE acking. The message comes back. The work happens twice.

    That is AT-LEAST-ONCE DELIVERY and every real queue gives you it. The fix
    is not in the queue - it is your handler being IDEMPOTENT.

THE DOWNSIDE
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

        # ---- NOW YOU WRITE THE REST --------------------------------------
        #   "enqueue then claim"     msg["payload"]["student"]
        #   "claim removes from ready"
        #                            q.depth() after the claim above
        #   "ack deletes"            q.ack(msg), then list
        #                            check-queue/processing - it must be []
        #
        # ---- then the part that matters --------------------------------
        #   "crash redelivers"
        #       enqueue something, claim it, and NEVER ack - that is exactly
        #       what a crashed worker leaves behind. q.recover() must return
        #       how many it rescued.
        #   "redelivered message is claimable"
        #       and the rescued message can be claimed again.
        #
        #   "naive handler double charges"
        #       Ledger, same charge twice -> len(charges). Write down the
        #       number you EXPECT before you run it, and notice that the
        #       expected number here is the bug. This check does not
        #       describe correct behaviour; it pins down broken behaviour so
        #       the next two lines can show the fix.
        #
        #   "idempotent handler does not"
        #       IdempotentLedger, same message_id twice -> len(charges).
        #       WHY THE MESSAGE ID IS THE ARGUMENT THAT MATTERS: the queue
        #       cannot promise once-only delivery - no queue can. It can
        #       only promise the id stays the same across redeliveries. The
        #       handler turns that promise into safety. Delivery is the
        #       queue's job; idempotency is yours.
        shutil.rmtree("check-queue", ignore_errors=True)
