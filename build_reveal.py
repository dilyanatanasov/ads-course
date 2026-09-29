"""Generate reveal/ from solutions/. Run this instead of copying by hand.

    python build_reveal.py            rebuild every session
    python build_reveal.py 04         rebuild session 04 only
    python build_reveal.py --check    fail if reveal/ is stale (no writes)

WHY THIS EXISTS
    solutions/ and reveal/ used to be two hand-maintained copies of the same
    code. Edit one, forget the other, and the folder students read is wrong.
    Now there is one source of truth - solutions/ - and reveal/ is output.

THE CONVENTION
    Anything between these markers is teacher-only and is stripped:

        <<<TEACHER
        Blast radius: CR-1 touches 1 place, CR-2 touches 3.
        Do not say "Strategy" out loud today.
        TEACHER>>>

    Markers work in docstrings and in comments. A stripped block leaves no
    trace - no blank gap, no "removed" note.

    Line-level version, for a single line:

        x = 1     # TEACHER: they always get this wrong, wait for it

RULE
    Never edit reveal/ by hand. It is overwritten.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "solutions")
TARGET = os.path.join(HERE, "reveal")

# Also swallows one blank line before the block, so stripping leaves the
# spacing a human would have written rather than a visible gap.
BLOCK = re.compile(
    r"(?:^[ \t]*\n)?^[ \t]*<<<TEACHER\b.*?^[ \t]*TEACHER>>>[ \t]*\n?",
    re.DOTALL | re.MULTILINE)
LINE = re.compile(r"[ \t]*#[ \t]*TEACHER:.*$", re.MULTILINE)


def strip_teacher(text):
    """Remove teacher-only blocks and trailing TEACHER: comments."""
    text = BLOCK.sub("", text)
    text = LINE.sub("", text)
    # A line that was nothing but a TEACHER: comment is now blank - drop it,
    # but keep deliberate blank lines that were already there.
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    return text


def sessions():
    for name in sorted(os.listdir(SOURCE)):
        if name.endswith(".py"):
            yield name


def build(only=None, check_only=False):
    os.makedirs(TARGET, exist_ok=True)
    written, stale = [], []

    for name in sessions():
        if only and not name.startswith(only):
            continue
        with open(os.path.join(SOURCE, name), encoding="utf-8") as handle:
            wanted = strip_teacher(handle.read())

        destination = os.path.join(TARGET, name)
        current = None
        if os.path.exists(destination):
            with open(destination, encoding="utf-8") as handle:
                current = handle.read()

        if current == wanted:
            continue
        if check_only:
            stale.append(name)
            continue
        with open(destination, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(wanted)
        written.append(name)

    # Anything in reveal/ with no source is left over from the old hand-copied
    # days. Name it rather than deleting someone's file silently.
    orphans = [n for n in sorted(os.listdir(TARGET))
               if n.endswith(".py") and not os.path.exists(
                   os.path.join(SOURCE, n))]

    if check_only:
        if stale:
            print("STALE - run python build_reveal.py")
            for name in stale:
                print("  " + name)
            return 1
        print("reveal/ is up to date")
        return 0

    for name in written:
        print("  wrote  reveal/" + name)
    if not written:
        print("  reveal/ was already up to date")
    for name in orphans:
        print(f"  ORPHAN reveal/{name} has no solutions/ source - delete it?")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    sys.exit(build(only=next((a for a in args if not a.startswith("-")), None),
                   check_only="--check" in args))
