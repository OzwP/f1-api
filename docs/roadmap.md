# F1 API — Build Roadmap

Goal: extend the existing Flask app into a deployed, tested, containerized
portfolio project. Work top to bottom — each phase should be a separate
git branch + PR to yourself, even solo. That habit alone is worth practicing.

---

## Phase 0 — Get oriented (30–60 min)
- [ ] Get the existing app running locally, hit each endpoint with `curl` or Postman
- [ ] Open `data.db` in a SQLite browser (e.g. DB Browser for SQLite) and look at
      the actual rows — get a feel for what's there
- [ ] Read `routes.py` end to end and narrate to yourself what each method does
- [ ] Write down (in the README or a NOTES.md) the issues you notice — compare
      against what I flagged above. Do you spot others?

**Why this phase matters:** you can't safely extend code you haven't traced.

---

## Phase 0.5 — App factory restructure

*(Added during rebuild planning, not in the original roadmap — see
`CLAUDE.md` decisions log. Needed as a prerequisite for Phase 4's test
config and Phase 6's env-var config; kept as its own PR so Phase 1's diff
stays focused on foreign keys.)*

- [ ] Replace root `setup.py` + module-level `app`/`db` with an app-factory
      pattern: `create_app(config_name)`, extensions instantiated in their
      own module and initialized via `init_app()` inside the factory
- [ ] Add the missing `__init__.py` files so `application` and its
      subpackages are proper packages
- [ ] Modernize dependencies (Flask 3.x, Flask-SQLAlchemy 3.x,
      SQLAlchemy 2.0-style) — fixes the Python 3.9→3.11 mismatch already
      present between the README and this environment
- [ ] Confirm the app still runs and all existing endpoints still respond
      identically before moving on

---

## Phase 1 — Fix the foreign keys (id-based, not name-based)
- [ ] Change `Team.motor_name` → `Team.motor_id` (FK to `motor.id`)
- [ ] Change `Driver.team_name` → `Driver.team_id` (FK to `team.id`)
- [ ] Update `routes.py` create/patch logic accordingly (you're currently doing
      `filter_by(name=...)` — decide: keep accepting names in the JSON body but
      resolve to ids internally, or switch the API to accept ids directly)
- [ ] Delete `data.db` and regenerate it — decide now if you're staying on
      SQLite for local dev or jumping to Postgres immediately (see Phase 6)
- [ ] Set up Flask-Migrate/Alembic now and generate the migration for this
      change, instead of drop-and-recreate (see `CLAUDE.md` decisions log)
- [ ] Fix list endpoints to return a JSON array / `{"data": [...]}` envelope
      instead of an id-keyed object, since there are no real consumers yet

**Concept to look up:** why surrogate keys (auto-increment id) are preferred
over natural keys (name) as foreign keys in relational design.

---

## Phase 2 — Add Race and Result models
- [ ] `Race`: id, name, circuit, date, season
- [ ] `Result`: id, race_id (FK), driver_id (FK), position, points
- [ ] Add the `db.relationship()` calls so you can do `race.results` and
      `driver.results` from Python, not just raw joins
- [ ] Add routes: `GET /races`, `GET /races/<id>`, `GET /races/<id>/results`
- [ ] `GET /races/<id>/results` should return each result with the driver's
      name and team nested in — this is your first real multi-table join
- [ ] Generate an Alembic migration for the new tables
- [ ] Decide whether `Driver.wins` stays as a denormalized cache or is
      dropped now that it's derivable from `Result` (see Phase 8 note about
      not storing standings redundantly — same argument applies here)

**Concept to look up:** SQLAlchemy relationship `backref` vs `back_populates`,
and lazy loading strategies.

---

## Phase 3 — Error handling + validation
- [ ] Every `.query.get(id)` that returns `None` should 404, not crash —
      add a helper or use `.get_or_404()`
- [ ] Add Marshmallow (or Pydantic) schemas for at least `Driver` and `Result`
      — validate POST bodies before touching the DB, return 400 on bad input
- [ ] Add pagination to list endpoints (`?page=1&per_page=20`) and a
      `?season=` filter on `/races`

**Concept to look up:** why you generally shouldn't trust `request.json`
directly in production code.

---

## Phase 4 — Tests (pytest) + CI (GitHub Actions)

*(CI folded into this phase — previously its own Phase 7 further down the
list; see `CLAUDE.md` decisions log. Wiring CI up alongside the test
suite means every phase from 5 onward is checked automatically from the
start, instead of leaving a gap where tests exist but nothing runs them
on push. CI runs on SQLite initially; add the Postgres service container
once Phase 6 lands.)*

- [ ] Set up a test config pointing at an in-memory SQLite db, separate from dev
- [ ] Write fixtures that seed a handful of teams/drivers/races before each test
- [ ] Cover: GET list, GET by id, GET missing id (404), POST valid, POST
      invalid (400), PATCH, DELETE — for at least Driver and Result
- [ ] Aim for meaningful coverage, not 100% — test behavior, not lines
- [ ] Add `.github/workflows/test.yml` running pytest on every push/PR
- [ ] Spin up a Postgres service container in the workflow (once Phase 6 is
      merged) so tests run against the real DB engine, not just SQLite
- [ ] Add the passing/failing badge to your README

**Concept to look up:** pytest fixtures and `conftest.py`; Flask's test client.

---

## Phase 5 — Seed real data
- [ ] Write a standalone `seed.py` that pulls one season from the Jolpica-F1
      API (Ergast's successor) and populates Team, Motor, Driver, Race, Result
- [ ] Handle the mapping carefully — the external API's field names won't
      match yours 1:1
- [ ] Make it idempotent (safe to run twice without duplicating rows)

---

## Phase 6 — Postgres + Docker

*(`docker-compose up` and the Postgres migration run could not be executed
live in the sandboxed session that wrote this — its network policy blocks
the Docker Hub CDN. Everything below was reviewed and unit-tested short of
that: `docker compose config` validates the compose file, the app's SQLite
test suite still passes against the same code paths, and `psycopg2-binary`
installs and imports cleanly. Run `docker compose up --build` locally to
do the live confirmation and check these off for real.)*

- [x] Swap SQLAlchemy's connection string from SQLite to Postgres
      (env-var driven, don't hardcode credentials)
- [x] Write a `Dockerfile` for the Flask app
- [x] Write a `docker-compose.yml` running the app + a Postgres service together
- [ ] Confirm `docker-compose up` gets you a working API from a clean checkout
- [ ] Run Alembic migrations against Postgres and confirm they apply cleanly

**Concept to look up:** why SQLite is fine for tests/dev but not typically
for a "real" deployed service; Docker networking between containers.

---

## Phase 7 — Deploy

*(Target changed mid-build from Render/Fly.io to AWS: ECS Fargate + RDS
Postgres behind a CloudFront distribution that requires a signed
URL/cookie on every request — see the README's "Deploying" section and
`terraform/aws/`. Infra-as-code is prepped, not applied: this session
doesn't have AWS credentials, and `terraform init` also couldn't reach
the provider registry to fully validate it — see `terraform/aws/README.md`
and the PR that added it for exactly what was and wasn't verified. The
remaining items are yours to do from your own AWS account.)*

- [x] Pick a deploy target and prep its infrastructure — AWS (ECS Fargate +
      RDS + CloudFront), see `terraform/aws/`
- [ ] `terraform apply`, build + push the image, deploy, confirm the
      CloudFront URL responds (with a signed URL/cookie —
      `scripts/sign_cloudfront_url.py`)
- [ ] Update the README with the live CloudFront domain and example
      signed requests

---

## Phase 8 — Stretch goals (pick if you have energy left)
- [ ] `GET /standings/<season>` — compute the championship table by aggregating
      `Result` rows, don't store it redundantly
- [ ] Response caching on list endpoints
- [ ] API docs via Swagger/OpenAPI (flask-smorest or similar)

---

## How to use this with me
Bring me a phase at a time. Paste the diff or describe what you built and
what broke — I'll review, explain the "why" behind anything that looks off,
and answer conceptual questions. I won't write the implementation for you
unless you're stuck and ask directly for a snippet to compare against.
