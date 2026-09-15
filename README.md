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

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.