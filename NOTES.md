# NOTES.md — Phase 0 findings

Issues noticed while tracing the original code, before any rebuild work
started. See `CLAUDE.md` for the decisions made in response to these, and
`docs/roadmap.md` for the phase plan.

## Structural

- No `__init__.py` anywhere (`application/`, `application/models/`,
  `application/routes/` are not real packages — they work by accident of
  how the app is run).
- The Flask `app`, `db`, and `Api` singletons live in a root-level
  `setup.py`, and `application/routes/routes.py` does
  `from setup import db` — a reach back up out of the package. `setup.py`
  also collides with the setuptools convention for that filename.
  No app-factory pattern, so nothing can point the app at a different
  config (e.g. an in-memory test database) without monkeypatching.
- README says Python 3.9.1; the actual dev environment is 3.11 — real
  version drift, not just an unpinned range.
- `data.db` is committed to git and not in `.gitignore`. It also gets
  regenerated/deleted per the roadmap's own Phase 1 instructions, which
  will produce noisy diffs of a binary file.

## Data model

- `Team.motor_name` and `Driver.team_name` are foreign keys to the
  *name* column of the parent table, not the id. Natural keys as FKs:
  renames cascade painfully, and uniqueness constraints on a display name
  are a design smell.
- `Motor.team` (a one-to-many relationship) is named as if singular —
  should be `Motor.teams`.
- `Driver.wins` is a plain column that will become redundant once
  `Result` rows exist in Phase 2 (wins are derivable by aggregation).

## Routes / API behavior

- `makeData()` builds `{"<id>": {...}}` for list responses instead of a
  JSON array — every consumer has to know to iterate `dict.values()`
  instead of a plain list, and it doesn't compose with pagination.
- No `id` presence check: `Model.query.get(id)` returning `None` (e.g.
  hitting `/drivers/999`) crashes with an `AttributeError` inside
  `makeData` instead of returning 404.
- Every `PATCH` handler does
  `for column in request.json: setattr(item, column, request.json[column])`
  — mass assignment with no allow-list, so a client can PATCH `id` itself,
  or any other column, including ones that shouldn't be externally
  settable.
- `POST` handlers resolve related objects by
  `Model.query.filter_by(name=request.json['team'])` — same natural-key
  issue as the FK columns, and a typo'd name silently resolves to `None`
  rather than erroring.
- No input validation at all — a missing required key in `request.json`
  raises a raw `KeyError`/500 instead of a 400.

## Testing / ops

- No tests exist at all.
- No CI.
- No migrations — schema changes require manually deleting and
  regenerating `data.db`.
