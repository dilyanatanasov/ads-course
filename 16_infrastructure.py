"""SESSION 16 - the INFRASTRUCTURE layer.

The outside world: storage, email, HTTP. May import inwards freely.
Swap these for SQLite or SMTP and nothing above changes.
"""


class InMemoryStudents:
    def __init__(self, students):
        self._rows = {s.id: s for s in students}

    def get(self, sid):
        return self._rows[sid]

    def add(self, student):
        self._rows[student.id] = student


class InMemoryCourses:
    def __init__(self, courses):
        self._rows = {c.id: c for c in courses}
        self._taken = {}

    def get(self, cid):
        return self._rows[cid]

    def seats_left(self, cid):
        return self._rows[cid].seats - len(self._taken.get(cid, set()))

    def take_seat(self, cid, sid):
        self._taken.setdefault(cid, set()).add(sid)


class RecordingNotifier:
    def __init__(self):
        self.messages = []

    def notify(self, student, message):
        self.messages.append((student.id, message))
