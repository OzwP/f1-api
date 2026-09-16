# F1-API

[![Tests](https://github.com/OzwP/f1-api/actions/workflows/test.yml/badge.svg)](https://github.com/OzwP/f1-api/actions/workflows/test.yml)

## Installation

Using a python virtual environment is recommended prior to installing
requirements.

**Python 3.9.1**

``` bash
python3 -m venv .venv
```

Then activate it using

``` bash
source .venv/bin/activate
```

Now the requirements can be installed

``` bash
pip install -r requirements.txt
```

Then create the database by applying the migrations

``` bash
export FLASK_APP=app.py
flask db upgrade
```

## Usage

To run server 

```
python app.py
```

### Index

    GET request to index
    # returns 'Hello World!'

### All endpoints (/motors, /drivers, /teams, /races, /results) accept the following methods:

#### GET

    # returns {"data": [...], "page": 1, "per_page": 20, "total": N, "pages": M}
    # supports ?page= and ?per_page= query params
    # /races also supports ?season= to filter by season

#### GET <id>

    # returns {"data": {...}} with the object of the specified id and its properties
    # returns 404 if no object exists with that id

#### POST

    #returns status code 201 when creating an appropriate resource
    #returns status code 400 with {"message": "Validation error", "errors": {...}} on bad input

    -motors 
    Expected: string:name

    -teams
    Expected: int:motor_id, string:name, string:car

    -drivers
    Expected: string:name, (optional) int:team_id

    -results
    Expected: int:race_id, int:driver_id, int:position, float:points

PATCH <id>

    # returns status code 200 when updating resource successfully 
    # returns status code 400 on bad input (drivers and results only)
    # returns status code 404 if no object exists with that id

    For example when making a PATCH call to localhost/drivers/2 
    {"team_id": 4} can be provided in the body to update said column

#### DELETE

    # returns status code 200 when successfully deleting a resource
    # returns status code 404 if no object exists with that id

### GET /standings/&lt;season&gt;

    # returns {"season": 2024, "data": [{"rank": 1, "points": 25.0, "driver": {"id": 1, "name": "...", "team": {"id": 1, "name": "..."}}}, ...]}
    # computed from Result rows on every request, not stored
    # ties share a rank (two drivers on 25 points are both rank 1, the next is rank 3)
    # an unknown/empty season returns 200 with an empty "data" array, not a 404

### API docs

Interactive Swagger UI is served at `/docs`, backed by the OpenAPI 3 spec
at `/openapi.json` (built in `application/docs.py`).

### Caching

List endpoints (`/motors`, `/teams`, `/drivers`, `/races`, `/results`,
`/standings/<season>`) are cached for `CACHE_DEFAULT_TIMEOUT` seconds
(30s by default), keyed on the full query string so different
`?page=`/`?per_page=`/`?season=` combinations don't collide. Any create,
update, or delete through the API clears the whole cache, so writes are
never masked by a stale read. Single-resource lookups by id aren't
cached. The default `CACHE_TYPE` is Flask-Caching's `SimpleCache`
(in-process, not shared across workers/instances) — fine for a single
container, but swap in a shared backend like Redis before running more
than one.

## Testing

Install dev dependencies (includes pytest on top of the app's requirements)
and run the suite:

``` bash
pip install -r requirements-dev.txt
pytest
```

Tests run against an in-memory SQLite database (the `testing` config) and
seed their own data per test, so they don't touch `data.db`. The same
command runs in CI on every push and pull request.

## Seeding real data

`seed.py` pulls one season of teams, drivers, races, and results from the
[Jolpica-F1 API](https://api.jolpi.ca/ergast/f1) (Ergast's maintained
successor) and writes it into the configured database:

``` bash
export FLASK_APP=app.py
flask db upgrade
python seed.py --season 2023
```

It's safe to run more than once — every row is looked up by its natural
key before insert, so re-running the same season updates existing rows
instead of duplicating them. The upstream API doesn't expose engine
manufacturer or chassis name, so engine is filled in from a small
season-specific lookup in `seed.py` and `car` is left unset.

## Running with Docker Compose

The app and a Postgres database can be brought up together, no local
Python install required:

``` bash
docker compose up --build
```

This builds the `web` image, starts Postgres, waits for it to be healthy,
runs `flask db upgrade` (via the container's entrypoint), and starts the
app with gunicorn on `http://localhost:5000`. Postgres data persists in
the `pgdata` volume across restarts.

To seed it with real data once it's up:

``` bash
docker compose exec web python seed.py --season 2023
```

## Configuration

`DATABASE_URL` selects the database for the `production` config (used by
Docker Compose above); without it, `ProductionConfig` falls back to the
same local SQLite file as development. `FLASK_CONFIG` selects which
config class `app.py` loads (`development` by default, `production` in
Docker Compose, `testing` under pytest).

## Deploying

The deployment target is AWS: ECS Fargate running the `Dockerfile` image,
an RDS Postgres instance, and a CloudFront distribution in front of it
that requires a **signed URL or signed cookie** on every request —
CloudFront rejects unsigned requests before they ever reach the app. This
is access control, not just a CDN: there's no public, unauthenticated way
to reach the API.

```
viewer --(signed URL/cookie required)--> CloudFront --(shared-secret header,
    IP-range-restricted)--> ALB --> ECS Fargate (this app) --> RDS Postgres
```

All of the infrastructure lives in `terraform/aws/` (see that directory's
README for the full walkthrough) and hasn't been applied against a live
AWS account from this repo — do that from your own credentials, then come
back and fill in the live CloudFront domain here.

Quick summary:

1. `cd terraform/aws && terraform init && terraform apply` — provisions
   the VPC, ECR repo, RDS instance, ECS service, ALB, and CloudFront
   distribution (see that directory's README for the one-time RSA keypair
   setup CloudFront signing needs first)
2. Build and push the app image to the ECR repo Terraform created, then
   force a new ECS deployment — either manually (commands in
   `terraform/aws/README.md`) or via `.github/workflows/deploy-aws.yml`
   (`workflow_dispatch`, once its AWS_ROLE_ARN/ECR_REPOSITORY/etc. repo
   variables are set)
3. Generate a signed URL or signed cookies with
   `scripts/sign_cloudfront_url.py` before hitting the CloudFront domain
   — an unsigned request gets a 403 from CloudFront directly

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.