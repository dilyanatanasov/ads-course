# Architecting Digital Systems

The lab exercises. One file per session, and each one is a small system that
already works - your job is what happens to it when someone asks for a change.

    git clone https://github.com/dilyanatanasov/ads-course.git
    cd ads-course
    python 04_strategy.py

## Setup

There isn't any. If `python --version` prints 3.8 or higher, you are ready.

No pip install, no test framework, no Docker, no database server, no internet.
Standard library only. If a session ever asks you to install something, that is
a bug - report it.

## How to run a session

    python 04_strategy.py

You get PASS and FAIL lines. That is the whole test framework - `check.py` is
20 lines, and you are welcome to read it. A session is finished when every
line says PASS.

A file full of FAIL lines on the first run is the normal starting state, not a
broken download.

## How a session works

Read the docstring at the top of the file first. All of them are laid out the
same way:

**THE SITUATION** - the concrete problem someone at the university actually
has. Sit with it for a minute; the annoyance is the point.

**THE IDEA** - what you are about to build, in two or three sentences.

**YOUR TASK** - a numbered list. Everything you need to finish the session,
and nothing optional.

**THE COST** - what this pattern charges you in return. Every session has one.

That last part matters more than it looks. Every pattern here is a trade, and a
developer who only ever learned the upside is how codebases end up with a
factory in front of everything. If you can't say what a pattern costs, you
don't know it yet.

Three sessions - 03, 16 and 24 - say **NOTHING TO IMPLEMENT TODAY**. Those are
complete working code that you read, measure, and deliberately break. There is
nothing to fix, and that is a different skill you will use more often than you
expect.

Eight sessions warn that **the first run looks broken**. You get a traceback
rather than PASS/FAIL, because the methods start out raising
`NotImplementedError`. Read the last line of the traceback - it names the
method to write first.

## Write the checks first

From session 02 on, the bottom of each file gives you one check already
written, then a commented list of the rest for you to write yourself.

For each one: **write the check, run it, watch it fail, then write the code
that makes it pass.** In that order.

This is not ceremony. A check you never saw fail is a check you have no reason
to trust - it might be passing by accident. And several sessions contain a
check that is *impossible to write* against the starting code. Session 02 is
the clearest: you cannot ask "what happens after the deadline?" without
changing your computer's clock. The check didn't fail, it couldn't be written,
and that is what a design problem looks like before it becomes a bug.

If you and your pair disagree about an expected value, settle that argument
before you write any implementation. The argument is the exercise. Deciding
what the code *should* do is the harder half of the job, and it is the half
that gets skipped.

## When you are stuck

1. Re-read BUILD IT TOGETHER. The reasoning for each step is there.
2. Read the check that is failing and say out loud what it is asking for.
3. Check the TODO comments - they usually name the exact expected string.
4. Ask. Being stuck for twenty minutes on a typo teaches you nothing.

## Answers

`reveal/` holds the worked answers, one session at a time, published after that
session has run. `git pull` to get the latest.

Compare it with what you wrote rather than reading it first. If yours passes
and looks different, that is often fine - and worth asking about.

## Sessions

    01  baseline monolith     three change requests; your OOP diagnostic
    02  seams                 hardcoded clock, print and fee rule -> parameters
    03  coupling              blast radius, measured with ast
    04  strategy              grading rules per faculty
    05  feature flags         strategy II - the rule chosen at runtime
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

Two exceptions to one-file-per-session, both deliberate:

- **Session 16** is four files (`16_domain`, `16_application`,
  `16_infrastructure`, `16_layers`) because separated layers *are* the lesson.
- **Sessions 23 and 24** take a mode argument, so one file can be several
  processes at once:

      python 24_services.py students

## The through-line

These are not 30 unrelated patterns.

04 Strategy becomes feature flags. 08 Observer becomes 22's event bus becomes
23's queue. 11 Facade becomes 24's API gateway. 15 Repository becomes "each
service owns its data" in 24.

So when you hear "an API gateway is a Facade with a network in it", you already
own the idea - you wrote it in week 6. Most of the distributed systems material
late in the course is something you already built, with a network dropped in
the middle of it.
