---
title: Lesson 2 — Depth Pass and Obsidian Conversion
tags:
  - type/teaching-addendum
  - project/f1-api
date: 2026-10-07
covers-commit: 6c42e07
previous: 2026-09-16-initial-teach
---

# Lesson 2 — Depth Pass and Obsidian Conversion

**Date:** 2026-10-07
**Covers:** no new commits. The code is unchanged at `6c42e07` — *"Phase 8: Stretch goals (standings, response caching, OpenAPI docs) (#12)"*, the same commit [[2026-09-16-initial-teach]] covered.
**Next run should diff from:** `6c42e07`

---

## What this run was

Not an incremental update, because nothing in the application changed. This was a **second pass over the same code**, asked for on two axes: go deeper and more practical, and make the document native to Obsidian.

That makes it an unusual addendum. There is no delta in the codebase to teach. What there is instead is a delta in *what we know about the codebase* — because going deeper meant going back to the running application and asking it questions the first pass never asked. Two of those questions produced new defects.

> [!tip] Transferable lesson
> A second read of code you have already documented is not wasted effort. The first pass establishes what the code *is*; the second asks what it *does under conditions you did not try*. The two findings below were both sitting in plain sight in code the previous pass had already quoted and explained.

---

## Two new findings

Both were produced by running the application, not by reading it. Full write-ups are in [[EXPLAINED#Part 15 — Verified Findings]]; here is what was asked and what came back.

### Finding 12 — no index on any foreign key

**The question:** the first pass established that `/races/<id>/results` issues 42 SQL statements. It never asked what each of those statements *costs*.

Dumping every index the schema creates:

```
sqlite_autoindex_motor_1    -- from UNIQUE (name)
sqlite_autoindex_team_1     -- from UNIQUE (name)
sqlite_autoindex_driver_1   -- from UNIQUE (name)
```

Three, all incidental to a `UNIQUE` constraint on a name, plus the implicit primary keys. Nothing on `result.race_id`, `result.driver_id`, `driver.team_id`, `team.motor_id` or `race.season` — every column the application joins or filters on.

Asking the planner what that means:

```
EXPLAIN QUERY PLAN  (the /standings/<season> query)
    SCAN result
    SEARCH driver USING INTEGER PRIMARY KEY (rowid=?)
    SEARCH race USING INTEGER PRIMARY KEY (rowid=?)
    USE TEMP B-TREE FOR GROUP BY
    USE TEMP B-TREE FOR ORDER BY
```

`SCAN result` is a full table scan. **The cost of a standings request grows with the total number of results in the database, not with the season requested.** Seed ten seasons and the 2024 standings get roughly ten times slower while returning the same twenty rows.

The root cause is a fact most people learn the hard way: **a foreign key does not create an index.** It constrains which values are legal and says nothing about search speed. Neither Postgres nor SQLite nor SQLAlchemy adds one; you must ask with `index=True`.

What makes this finding the most *durable* of the thirteen is that nothing in the project's tooling can surface it:

- It is invisible in the response — the data is correct, just slowly obtained.
- The tests pass, and they run on datasets of two rows where a scan is free.
- **`flask db migrate` will never flag it.** Autogenerate compares the database to the models; the models do not declare these indexes, so the schema matches perfectly. It reports no drift because there is no drift — the models are simply wrong together.

### Finding 13 — integer fields silently truncate floats

**The question:** the first pass said Marshmallow "coerces types" and moved on. What does coercion actually do at the edges?

Loading the schema directly, with no database involved:

| Input | Field | Result |
|---|---|---|
| `"3"` | Integer | `3` — string of digits parses |
| `3.7` | Integer | **`3`** — truncated, accepted, no warning |
| `"4.9"` | Integer | rejected: "Not a valid integer." |
| `true` | Float | rejected: "Not a valid number." |
| `12345` | String | rejected: "Not a valid string." |

So `POST /results` with `"position": 3.7` returns `201 Created` and stores position 3. Nothing in the response says a value was changed.

Two things make it worth a finding rather than a footnote. It is silent data corruption, and since every JSON number is a float, a client computing a position arithmetically can easily produce `3.0000000000000004`. And the rule is **internally inconsistent**: `3.7` the number is accepted while `"4.9"` the string is rejected, so the same logical value passes or fails depending on quoting. A client switching from form encoding to JSON changes its validation behavior without changing its values.

The fix is one argument — `fields.Integer(strict=True)` — which is the kind of thing you only apply if you have read your validation library's coercion rules rather than assumed them.

---

## What else got deeper

Nine areas gained material that is measured rather than described. Briefly, with where it landed:

| Area | What was added |
|---|---|
| HTTP methods | Safe and idempotent as formal properties; why this API has no `PUT`; `HEAD` and `OPTIONS` work without being written |
| Method dispatch | *Why* a collection `PATCH` is a 500 while `PUT` is a clean 405 with an `Allow` header — two different layers decide |
| Indexes | A new vocabulary section, because the concept was missing entirely from the first pass |
| The SQLAlchemy session | Unit of work, identity map, and context scoping, as one concept the rest of the document refers back to |
| Autoflush | Measured: a query emits the pending `INSERT` before its `SELECT`. This is *why* the seeder's get-or-create works |
| expire_on_commit | Measured: reading an attribute after commit costs an extra `SELECT` |
| Query plans | `EXPLAIN QUERY PLAN` output for all five hot queries |
| Cache keys | The actual key format, and confirmation that argument order does not fragment the cache |
| Concurrency | One sync worker, one task: effective concurrency of **1**, and the coupling to the latent cache bug |
| Marshmallow coercion | A nine-row table of measured inputs and outputs |
| Alembic autogenerate | What it detects versus what it misses, including why it cannot see finding 12 |
| Schema omissions | No `ON DELETE` policy, no `CHECK` constraints, no uniqueness on `(race_id, driver_id)` |
| GROUP BY portability | The standings query is legal on Postgres by functional dependency and on SQLite by permissiveness — the same dev/prod divergence shape as finding 4 |

One thing was *resolved* rather than added. The previous addendum recorded a correction: a `DELETE` returning 500 turned out to be an artifact of the probe sharing one session across requests, and the handlers — which serialize an object after committing its deletion — work fine. It explained the symptom but not the mechanism. This pass found it:

```
after delete+commit -> persistent: False | deleted: False | detached: True
expired attribute names: none (values retained)
serialize() of the deleted object -> {'id': 1, 'name': 'Merc PU'}
SQL emitted while serializing: 0
```

A deleted-and-committed object is **detached with its attribute values intact**, rather than expired like every other committed object. So `serialize()` reads from memory and never asks the database about a row that no longer exists. It looks like it should fail, it does not, and now there is a reason rather than an absence of one.

---

## The Obsidian conversion

The document is now written in Obsidian's own dialect rather than GitHub-flavoured Markdown. Four changes, and one deliberate non-change.

**Wikilinks replace anchor links.** `[Part 8](#part-8--one-request-end-to-end)` became `[[#Part 8 — One Request, End to End]]`. GitHub's slug anchors do not resolve in Obsidian; wikilinks do, and they also surface in the graph view and in backlinks. 88 heading links and 2 note links, all validated against the actual headings by a checker that fails on a mismatch.

A constraint fell out of this: **headings can no longer contain backticks**, because a backtick inside a wikilink target is fragile. So `### 6. per_page is unbounded` rather than ``### 6. `per_page` is unbounded``. Marginally less pretty, reliably linkable.

**Callouts replace blockquotes and HTML.** The 29 "Transferable lesson" pull quotes are now `> [!tip]` callouts, warnings are `> [!warning]`, and the recorded decisions are `> [!info]`. Most usefully, the eleven exercise hints — previously `<details><summary>` HTML, which renders as raw markdown inside Obsidian — are now `> [!hint]- Hint`, a natively foldable callout, collapsed by default.

**Frontmatter properties.** Title, aliases, tags, dates and the commit covered, so the note is filterable and the `covers-commit` value is queryable rather than buried in prose.

**File references are inline code, not links.** `application/routes/routes.py:129` rather than a relative markdown link. This is the deliberate tradeoff: a relative link to a `.py` file resolves differently depending on whether the vault root is the repository root, the `docs/` folder, or somewhere else entirely, and in most of those cases it is simply broken. Inline code is correct in every reader, at the cost of not being clickable in any of them. If the vault is the repository root and clickable source links matter more, that decision is a find-and-replace away.

The PDF pipeline was taught to understand all of this — wikilinks, callouts, frontmatter — so `EXPLAINED.pdf` still renders, with callouts coloured by type.

---

## What was updated in the master doc

All of it, structurally: [[EXPLAINED]] went from 18 parts to the same 18 parts with roughly 300 lines of new measured material, and every piece of syntax changed. Specifically:

- New sections: [[EXPLAINED#Indexes, the part nobody declares]], [[EXPLAINED#Why this API has no PUT]], [[EXPLAINED#WSGI and the concurrency model]], [[EXPLAINED#What a rename actually costs]], [[EXPLAINED#What the schema does not declare]], [[EXPLAINED#How method dispatch really works]], [[EXPLAINED#The session, the unit of work, and the identity map]], [[EXPLAINED#Autoflush, measured]], [[EXPLAINED#expire_on_commit, measured]], [[EXPLAINED#What coercion actually does, measured]], [[EXPLAINED#What the database actually does with it]], [[EXPLAINED#A portability trap in GROUP BY]], [[EXPLAINED#What the cache key actually is]], [[EXPLAINED#What autogenerate will not do for you]], [[EXPLAINED#How many requests can this serve at once]], [[EXPLAINED#What it cost]].
- Findings 12 and 13 added to Part 15, and the Part 17 severity table re-ranked — finding 12 enters at **High**, above the N+1 it compounds.
- Exercise 4 now covers the N+1 *and* the indexes together, because fixing either alone leaves most of the cost in place.
- Exercise 9 gained a warning that finding 4 will start failing tests once CI runs on Postgres, and that this is success rather than a regression.

The previous addendum, [[2026-09-16-initial-teach]], was converted to the same syntax but its content was left as written — it is a record of what that run found, and rewriting history in a course log defeats the point of keeping one.
