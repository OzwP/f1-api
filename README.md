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

The app is deploy-ready via its `Dockerfile` on either Render or Fly.io,
both of which offer a free web service + Postgres pairing. Neither step
below has been run against a live account — do it from your own login,
then update this section with the live URL.

### Render

`render.yaml` at the repo root is a Blueprint: it provisions a free
Postgres database (`f1-api-db`) and a Docker web service (`f1-api`) wired
together via `DATABASE_URL`, and sets `FLASK_CONFIG=production`.

1. On [Render](https://render.com), New → Blueprint, point it at this repo
2. Render reads `render.yaml`, provisions the database and web service, and
   builds the `Dockerfile`
3. The container's entrypoint runs `flask db upgrade` on boot, so the
   schema is created automatically on first deploy

### Fly.io

`fly.toml` is a starting config (`app` name is a placeholder — Fly
generates names during `fly launch`).

``` bash
fly launch --no-deploy          # reconciles fly.toml, reserves an app name
fly postgres create              # free-tier Postgres cluster
fly postgres attach <db-app-name>  # wires DATABASE_URL into secrets
fly deploy
```

`fly postgres attach` sets `DATABASE_URL` as a Fly secret automatically;
`FLASK_CONFIG=production` is already set via `fly.toml`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.