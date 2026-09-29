# Architecting Digital Systems - labs

One file per session. Clone it, run it, read the PASS/FAIL lines, fill in the
TODOs.

    git clone <this repo>
    cd ads-course
    python 04_strategy.py

**Python 3.8+ and nothing else.** No pip install, no test framework, no Docker,
no database server, no internet. Standard library only. There is nothing to
set up - if `python --version` works, you are ready.

## How a session works

Every file has the same five parts, in this order:

    THE PAIN              why the code you are about to write exists
    BUILD IT TOGETHER     the steps we type on the projector, with the WHY
                          for each one
    YOUR JOB              what you finish in pairs
    THE TWIST             the change request that arrives once it works
    THE DOWNSIDE          what this pattern costs you

**We write the checks first.** From session 02 on, the bottom of each file
gives you the first check already written - the one we do together - and then
a commented list of the rest for you to write. Write the check, run it, watch
it fail, then write the code that makes it pass.

That order is not ceremony. Several sessions contain a check that is
*impossible to write* against the starting code - session 02 is the clearest -
and discovering that is the lesson. A design problem announces itself as a
test you cannot write, long before it announces itself as a bug.

If you and your pair disagree about an expected value, settle that argument
before writing any implementation. The argument *is* the exercise.

## Layout

    *.py          the sessions - this is what you clone
    reveal/       the worked answers, pushed after each session runs
    check.py      the PASS/FAIL printer. The only shared file.

`reveal/` is committed but fills up as the semester goes: each session's answer
appears after that session has run. `git pull` to get it.

Run any file from the folder it lives in:

    python 04_strategy.py
    cd reveal && python 04_strategy_solution.py

## Sessions with code

    01  baseline monolith     three change requests; your OOP diagnostic
    02  seams                 hardcoded clock, print and fee rule -> parameters
    03  coupling              blast radius, measured with ast
    04  strategy              grading rules per faculty
    06  factory               who chooses the strategy
    07  singleton             build it, then watch state leak between scenarios
    08  observer              registration side effects
    09  command               undo, retry, audit trail
    10  adapter               a deliberately awful legacy bank API
    12  decorator             caching and logging without editing a class
    13  middleware            auth / rate limit / logging chain
    14  state machine         enrolment lifecycle
    15  repository            one check suite, two storages
    16  layers                + a check that enforces the dependency rule
    17  MVC                   stdlib http.server, no framework
    22  event bus             observer, generalised
    23  queue + worker        a message queue made of files
    24  services              three processes on localhost, no Docker

Still to write (12): 05 strategy II, 11 facade, 18 service layer, 19 DTOs,
20 DI container, 21 ports and adapters, 25 shared database, 26 API gateway,
27 failure modes, 28 eventual consistency, 29 scenario workshop,
30 defend your architecture. Sessions 29 and 30 need no code at all - they run
on whatever you built during the semester.

Two exceptions to one-file-per-session, both deliberate:

- **Session 16** is four files (`16_domain`, `16_application`,
  `16_infrastructure`, `16_layers`) because separated layers *are* the lesson.
- **Sessions 23 and 24** take a mode argument so one file can be several
  processes: `python 24_services.py students`.

Sessions 16 and 24 have no TODOs. They are complete working code that you read
and then deliberately break, so there is nothing to solve.

## Session shape (50-60 min)

| Min | What |
|---|---|
| 0-8 | Run it. Take a change request. Feel the pain. Do not name the pattern. |
| 8-23 | BUILD IT TOGETHER. Checks first, then code, one step at a time. |
| 23-45 | Pairs write the remaining checks and make them pass. |
| 45-55 | The twist, then **the downside**. |
| 55-60 | Buffer. |

**Do not skip the downside.** Every docstring names a real cost. Students who
only learn the upside become the developers who put a factory in front of
everything.

## The through-line

04 Strategy becomes feature flags. 08 Observer becomes 22's event bus becomes
23's queue. 11 Facade becomes 24's API gateway. 15 Repository becomes "each
service owns its data" in 24. When you hear "an API gateway is a Facade with a
network in it", you already own the idea.

---

## For whoever is teaching this

`solutions/` is gitignored and never reaches GitHub. It is the source of truth;
`reveal/` is **generated** from it:

    python build_reveal.py            rebuild everything
    python build_reveal.py 04         one session
    python build_reveal.py --check    fail if reveal/ is stale, write nothing

Teacher-only content lives in marked blocks and is stripped on the way out:

    <<<TEACHER
    Blast radius: CR-1 touches 1 place, CR-2 touches 3.
    Do not say "Strategy" out loud today.
    TEACHER>>>

    x = 1     # TEACHER: they always get this wrong, wait for it

Never edit `reveal/` by hand - it is overwritten. Run `build_reveal.py` after
touching a solution and commit the result, or students pull an answer that
does not match the code.

`reveal/` is **gitignored by default**, so a stray `git add .` cannot leak the
whole semester in one commit. Publishing session NN, after you have taught it:

    python build_reveal.py NN
    git add -f reveal/NN_*.py
    git commit -m "reveal: session NN" && git push

The `-f` is only needed the first time each file is published; after that git
tracks it normally.

Keep `solutions/` backed up somewhere yourself. Because it is gitignored, this
repo is not backing it up for you.

### Verify everything still runs

    cd solutions && for f in *_solution.py; do python "$f"; done
    python build_reveal.py --check
