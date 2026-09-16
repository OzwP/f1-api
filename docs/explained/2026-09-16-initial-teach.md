# Lesson 1 — Initial Teaching Pass

**Date:** 2026-09-16
**Covers:** the project from its first commit (`0b096db`, April 2022) through `6c42e07` — *"Phase 8: Stretch goals (standings, response caching, OpenAPI docs) (#12)"*, the head of `origin/main`.
**Next run should diff from:** `6c42e07`

---

## What this run covered

This is the first pass, so [`EXPLAINED.md`](../EXPLAINED.md) was written from scratch: the whole project, from what an HTTP request is through to why CloudFront is being used as an authentication layer. Nothing had changed since a previous run, because there was no previous run.

Rather than restate that document, this lesson records the part of the run that produced **new knowledge** — things that were not derivable by reading the code, and that the next run should not have to rediscover. The project's own `NOTES.md` catalogued what was wrong with the 2022 prototype before the rebuild began; this is the equivalent inventory for the code as it stands *after* eight phases of rebuilding.

The method matters, so it's worth stating: the application was installed into a clean Python 3.11 virtualenv with the pinned requirements, the test suite was run, and then the API was driven with a test client through a series of deliberately awkward requests. Several conclusions that seemed obvious from reading the source turned out to be wrong, and one of them is documented below as a mistake.

---

## First, the baseline: what works

The suite is green and fast:

```
37 passed, 55 warnings in 0.87s
```

Installed versions, for the record, since the next run will want to know whether a dependency moved underneath it:

| Package | Version |
|---------|---------|
| Python | 3.11.15 |
| Flask | 3.1.3 |
| Flask-SQLAlchemy | 3.1.1 |
| SQLAlchemy | 2.0.52 |
| Flask-RESTful | 0.3.10 |
| Flask-Caching | 2.5.1 |
| Flask-Migrate | 4.1.0 |
| marshmallow | 4.3.1 |
| apispec | 6.10.0 |
| pytest | 9.1.1 |

Those 55 warnings are worth a glance rather than a shrug. Most are `LegacyAPIWarning` from `Query.get()` inside `get_or_404` — 18 of them — which sits oddly beside the project's stated decision to use "SQLAlchemy 2.0-style usage." The rest are Flask-Caching announcing that `NullCache` means caching is disabled, which is the testing config working as designed.

---

## Eleven findings, and how each was established

All eleven are written up in full in [Part 15 of the master doc](../EXPLAINED.md#part-15--real-bugs-and-sharp-edges-verified-not-guessed), with transcripts, root causes, and fixes. Summarised here with the *evidence* for each, because the evidence is what makes them worth trusting:

| # | Finding | How it was established |
|---|---------|------------------------|
| 1 | `PATCH`/`DELETE` on a collection URL → 500, not 405 | `PATCH /motors` → 500; log shows `TypeError: Motor.patch() missing 1 required positional argument: 'id'` |
| 2 | Mass assignment live on `Motor`/`Team` — a client can rewrite a primary key | `PATCH /motors/1 {"id": 999}` → 200; `GET /motors/999` then returns the row |
| 3 | `POST` to an unvalidated resource → 500 on a missing field | `POST /motors {}` → 500 (`KeyError: 'name'`); `POST /teams` without `car` → 500 |
| 4 | FKs unenforced on SQLite; enforced on Postgres | `PRAGMA foreign_keys` returns `0`; `POST /results` with ids 99999/88888 → **201** |
| 5 | N+1 queries | SQLAlchemy `before_cursor_execute` listener counted statements per request: 42, 21, 2 |
| 6 | `per_page` unbounded | `?per_page=100000` → honored verbatim in the response |
| 7 | No `rollback()` after a failed commit | Probed both ways — see the correction below |
| 8 | Constraint violations → 500, not 409 | Duplicate `POST /drivers` → 500 (`UNIQUE constraint failed: driver.name`) |
| 9 | Missing `Content-Type` → 415 (correct, but surprising) | `POST /drivers` with no header → 415 |
| 10 | ALB health check can't fail | Read `alb.tf`'s `health_check { path = "/" }` against the `index()` handler |
| 11 | Git history contradicts its own stated contract | `git rev-list --parents` parent counts per phase-boundary commit |

Finding 4 is the one to carry forward if you only remember one. It isn't a coding mistake — it's a **behavioral divergence between the test environment and the production environment**, which means it is structurally invisible to the test suite. The same request is a `201` on SQLite and a `500` on Postgres. And because CI still runs on SQLite (the roadmap's own Phase 4 item for adding a Postgres service container is still unticked), nothing in the pipeline can see it either.

---

## A measurement worth repeating

The N+1 numbers came from attaching a listener to the engine and counting statements per request, against one race with 20 drivers, 20 teams and 20 results:

| Endpoint | SQL statements issued |
|----------|----------------------|
| `GET /races/1/results` | **42** |
| `GET /standings/2024` | **21** |
| `GET /drivers?per_page=20` | **2** |

The third row is what makes the first two meaningful. `GET /drivers` touches no relationships, and costs exactly the two queries it should — one for the page, one for the `count(*)`. So the endpoint design isn't the problem; **attribute access on a lazily-loaded relationship inside a loop** is. `result.driver` and `driver.team` look like free attribute reads and are each a database round-trip.

This is the clearest case in the project of an abstraction hiding a cost. Reading `serialize_result_with_driver` end to end, there is nothing visibly expensive in it:

```python
driver = result.driver
team = driver.team
```

The fix is about five lines of `joinedload`. The more durable fix is a test that asserts the query count, so the next person to touch that function finds out immediately — that's [Exercise 4](../EXPLAINED.md#exercise-4--kill-the-n1-in-racesidresults-).

---

## A correction: one finding I got wrong at first

Worth recording, because the mistake is more instructive than the conclusion.

Probing the `DELETE` handlers, I saw this:

```
DELETE /results/1  →  500 {"message": "Internal Server Error"}
```

and reached for an appealing explanation. Every delete handler does this:

```python
db.session.delete(result)
db.session.commit()
invalidate_cache()

data = makeData(result, "Resource succesfully deleted")   # ← serializing a deleted object
```

It *reads* like a bug: serialize an object after committing its deletion, and SQLAlchemy's expire-on-commit should raise when you touch its attributes. A clean, plausible story.

It was wrong, and the test suite said so — `test_delete_driver` and `test_delete_result` both pass, asserting a 200. Rather than assume the tests were lucky, I isolated the case:

| Case | Result |
|------|--------|
| `DELETE` a driver with no results | **200**, correct body |
| `DELETE` a result row | **200**, correct body |
| `DELETE` a driver that has results | **200** |
| `DELETE` a team that still has a driver | **200** |

All fine. The 500 was **an artifact of my own probe script**: it held a single `app.app_context()` open across every request, so all of them shared one SQLAlchemy session. An earlier probe in the same script had triggered an `IntegrityError` (the duplicate-name case, finding 8), leaving that shared session needing a rollback that no handler performs. The `DELETE` then failed on the poisoned session.

Which turned the mistake into finding 7, and a genuinely more interesting result than the bug I thought I'd found:

```
POST /drivers {"name":"Lewis Hamilton"}  (duplicate)  →  500
GET  /drivers                      immediately after  →  200, correct data
POST /drivers {"name":"George Russell"}               →  201
```

The missing `rollback()` is real, but it is **contained** — because Flask-SQLAlchemy scopes the session to the application context, and Flask pushes a fresh one per request. The broken session is discarded before the next request starts. That's containment rather than correctness, and it holds only while no single handler does two units of work; add a second `commit()` to any handler and it becomes a live bug.

> **Transferable lesson:** when your test harness and the real runtime disagree, suspect the harness. My probe shared a session across requests in a way no real server does, and it manufactured a failure that doesn't exist — while accidentally proving something true about the code. Reproduce a suspected bug in isolation before writing it up, and when a passing test contradicts your theory, the test is usually right.

---

## What this told us about the process, not the code

Two patterns showed up repeatedly and are worth naming, because they'll predict where the *next* bugs are.

**"At least" is where the gaps live.** The roadmap's Phase 3 asked for Marshmallow schemas "for at least `Driver` and `Result`." Exactly `Driver` and `Result` were done. Findings 2 and 3 — the most severe in the list — are both `Motor` and `Team`, and `schemas.py` even says so in a comment. A scope phrased as a floor gets implemented as a ceiling.

**Untested code and broken code are the same code.** `Motor` and `Team` have no `PATCH` or `DELETE` tests. They are also the two resources with the mass-assignment hole. This is not a coincidence in either direction: writing the test would have exposed the bug, and the bug survived because no test described the behavior.

**And unverified is not the same as working.** Phases 6 and 7 are candidly documented as never having been executed — `docker compose up` was blocked by a network policy, and `terraform apply` has never run against a live AWS account. That candor is genuinely good practice, and it means everything in [Part 14](../EXPLAINED.md#part-14--docker-postgres-and-deployment) about the Postgres and AWS path describes configuration that has been *written* and *reviewed*, not configuration that has been *run*. The next session should resist treating it as proven.

---

## What was updated in the master doc

Everything — this was the first run, so [`EXPLAINED.md`](../EXPLAINED.md) was created in full (18 parts plus an appendix). Notable structural choices the next run should preserve or deliberately change:

- **[Part 8](../EXPLAINED.md#part-8--one-request-end-to-end)** traces `GET /standings/2024` through all nineteen steps and is flagged as the read-this-first section. Its step 13 is where the N+1 becomes visible in the narrative.
- **[Part 15](../EXPLAINED.md#part-15--real-bugs-and-sharp-edges-verified-not-guessed)** holds all eleven findings with transcripts. Each entry has a root cause and a fix, so it doubles as a work queue.
- **[Part 17](../EXPLAINED.md#part-17--known-weaknesses)** ranks the defects by fix priority and separates *verified defects* from *coverage gaps* from *missing-for-production* items — three different kinds of debt that shouldn't share a list.
- **[Part 18](../EXPLAINED.md#part-18--exercises)** has eleven exercises with hints. Exercises 3 and 4 are starred: closing the mass-assignment hole and killing the N+1.
- The SQL in Parts 7 and 8 was **dumped from the running application**, not transcribed by hand, so it's exactly what SQLAlchemy compiles.

If the next run finds these findings fixed, the corresponding Part 15 entries should move to a short "previously fixed" note rather than being deleted — the reasoning behind a fix is worth as much as the fix.
