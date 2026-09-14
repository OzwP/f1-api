# F1-API

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

### All endpoints (/motors, /drivers, /teams) accept the following methods:

#### GET

    # returns {"data": [...]} with all the objects in the db and their properties

#### GET <id>

    # returns {"data": {...}} with the object of the specified id and its properties

#### POST

    #returns status code 201 when creating an appropriate resource

    -motors 
    Expected: string:name

    -teams
    Expected: int:motor_id, string:name, string:car

    -drivers
    Expected: int:team_id, string:name, (optional) int:wins

PATCH <id>

    # returns status code 200 when updating resource successfully 

    For example when making a PATCH call to localhost/drivers/2 
    {wins: 4} can be provided in the body to update said column

#### DELETE

    # returns status code 200 when successfully deleting a resource

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.