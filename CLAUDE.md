# CLAUDE.md

Guidance for any Claude Code session working on this repo. Read this before
starting a phase. The build plan itself lives in `docs/roadmap.md`.

## What this project is

A Flask + SQLAlchemy REST API for F1 data (teams, motors, drivers, races,
results), being rebuilt phase by phase from a rough 2022 prototype into a
tested, containerized, deployed portfolio project. See `docs/roadmap.md`
for the full phase list and `NOTES.md` for the issues found in the
original code during Phase 0.

## Branching strategy

- `main` is the only long-lived branch. (Renamed from `master` during
  rebuild planning — no other tooling referenced the old name yet, so the
  rename was free.)
- Every phase is its own branch off `main`: `phase/NN-short-slug`
  (e.g. `phase/01-fk-ids`, `phase/02-race-result`). Non-phase work (this
  bootstrap, later chores) uses `chore/short-slug`.
- One PR per phase, merged with `--no-ff` so the merge commit marks the
  phase boundary — `git log --first-parent main` should read like the
  roadmap's phase list.
- Phases are sequential (Phase 2 depends on Phase 1's FK changes, etc.) —
  don't stack phase branches on each other or run them in parallel.
  Merge, then branch again.
- Each phase is worked in its own fresh session. A new session should:
  1. Read this file and `NOTES.md`
  2. Read `docs/roadmap.md` for the specific phase's checklist
  3. Branch off current `main` (not off another phase branch)
  4. Open one PR back to `main` when the phase is done

## Commit style

- Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`,
  `docs:`.
- Atomic commits — one logical change each, and the app/test suite should
  be in a working state at every commit, not just at the tip of the
  branch. A phase is typically 2-4 commits (e.g. schema change, route
  logic, migration, tests), not one giant commit and not one commit per
  file.
- Don't rewrite the pre-rebuild history (the `*cleanup*` / `*updated*
  readme` commits) — leave it as-is; the contrast with the new history is
  part of the record.
- Merge PRs with a merge commit (`--no-ff`), not squash — the commit
  decomposition inside the PR is deliberate and worth keeping.
- This repo is public: commit messages and PR bodies may include a
  `Co-Authored-By: Claude ...` trailer, but never a `Claude-Session:`
  link — that URL is a direct link into the session and shouldn't be
  published.

## Key technical decisions (made during rebuild planning)

These were explicit decisions, not defaults — don't relitigate them
mid-phase without flagging it first:

1. **Dependencies are modernized**, not pinned to the 2022 versions in the
   original README: current Flask 3.x, Flask-SQLAlchemy 3.x,
   SQLAlchemy 2.0-style usage. This also fixes a real Python 3.9→3.11
   mismatch between the README and the actual dev environment.
2. **Alembic (via Flask-Migrate) is set up starting in Phase 1**, not
   deferred to the Postgres switch in Phase 6. Every schema change from
   Phase 1 onward should be a migration, not a `db.create_all()` /
   drop-and-recreate cycle.
3. **The app-factory restructure is its own phase (0.5)**, done before
   Phase 1's foreign-key work, so that PR's diff is only the
   `setup.py` → `create_app()` / package structure fix and Phase 1's diff
   stays focused on FKs.
4. **List endpoint response shape is fixed in Phase 1**: return a JSON
   array or `{"data": [...]}` envelope instead of the original
   id-keyed-object shape (`{"1": {...}, "2": {...}}`). There are no real
   consumers yet, so this is free now and everything after it (pagination
   in Phase 3, tests in Phase 4) is built on the right shape from the
   start.
5. **CI (originally Phase 7) is pulled forward to right after Phase 4**
   (tests), not left until after Docker/Postgres in Phase 6. It runs
   against SQLite initially; the Postgres service container is added once
   Phase 6 merges.
6. **One fresh session per phase.** Each session is scoped to a single
   phase, branches off current `main`, and opens one PR. Don't carry one
   session across multiple phases.

## Things noticed in the original code (fixed progressively per phase, not all at once)

See `NOTES.md` for the full Phase 0 list. Highlights: FKs by name instead
of id, mass-assignment in every PATCH handler (`setattr` over all of
`request.json` including `id`), no 404 handling on missing ids, `data.db`
committed to git, no `__init__.py` files anywhere, root-level `setup.py`
holding the Flask app/db singletons.
