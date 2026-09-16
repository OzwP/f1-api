"""Builds the OpenAPI 3 spec served at /openapi.json (and rendered by
Swagger UI at /docs).

The routes are Flask-RESTful resources rather than plain view functions,
so there's no decorator on each handler generating this automatically —
the paths below are declared by hand, once per resource, using apispec's
MarshmallowPlugin to turn the existing marshmallow schemas into component
schemas and $refs.
"""
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from .schemas import (
    DriverSchema,
    MotorSchema,
    RaceSchema,
    ResultSchema,
    StandingsEntrySchema,
    TeamSchema,
)

# name -> (schema class, base path, extra query params for the list op)
RESOURCES = {
    "Motor": (MotorSchema, "/motors", []),
    "Team": (TeamSchema, "/teams", []),
    "Driver": (DriverSchema, "/drivers", []),
    "Race": (RaceSchema, "/races", [{"name": "season", "in": "query", "schema": {"type": "integer"}}]),
    "Result": (ResultSchema, "/results", []),
}

PAGE_PARAMS = [
    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 20}},
]

ID_PARAM = {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}


def _envelope(schema_name):
    return {
        "type": "object",
        "properties": {"data": {"$ref": f"#/components/schemas/{schema_name}"}},
    }


def _list_envelope(schema_name):
    return {
        "type": "object",
        "properties": {
            "data": {"type": "array", "items": {"$ref": f"#/components/schemas/{schema_name}"}},
            "page": {"type": "integer"},
            "per_page": {"type": "integer"},
            "total": {"type": "integer"},
            "pages": {"type": "integer"},
        },
    }


def build_spec():
    spec = APISpec(
        title="F1 API",
        version="1.0.0",
        openapi_version="3.0.3",
        info={
            "description": (
                "Teams, motors, drivers, races, and results. List endpoints "
                "are paginated and briefly cached; /standings is computed "
                "from Result rows on every request."
            )
        },
        plugins=[MarshmallowPlugin()],
    )

    for name, (schema_cls, base_path, extra_list_params) in RESOURCES.items():
        spec.components.schema(name, schema=schema_cls)

        spec.path(
            path=base_path,
            operations={
                "get": {
                    "summary": f"List {name.lower()}s",
                    "parameters": PAGE_PARAMS + extra_list_params,
                    "responses": {
                        "200": {
                            "description": "Paginated list",
                            "content": {"application/json": {"schema": _list_envelope(name)}},
                        }
                    },
                },
                "post": {
                    "summary": f"Create a {name.lower()}",
                    "requestBody": {"content": {"application/json": {"schema": schema_cls}}},
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {"application/json": {"schema": _envelope(name)}},
                        },
                        "400": {"description": "Validation error"},
                    },
                },
            },
        )

        spec.path(
            path=f"{base_path}/{{id}}",
            operations={
                "get": {
                    "summary": f"Get a {name.lower()} by id",
                    "parameters": [ID_PARAM],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {"application/json": {"schema": _envelope(name)}},
                        },
                        "404": {"description": "Not found"},
                    },
                },
                "patch": {
                    "summary": f"Update a {name.lower()}",
                    "parameters": [ID_PARAM],
                    "responses": {
                        "200": {
                            "description": "Updated",
                            "content": {"application/json": {"schema": _envelope(name)}},
                        },
                        "400": {"description": "Validation error"},
                        "404": {"description": "Not found"},
                    },
                },
                "delete": {
                    "summary": f"Delete a {name.lower()}",
                    "parameters": [ID_PARAM],
                    "responses": {
                        "200": {"description": "Deleted"},
                        "404": {"description": "Not found"},
                    },
                },
            },
        )

    spec.path(
        path="/races/{id}/results",
        operations={
            "get": {
                "summary": "Results for a race, with each driver and their team nested in",
                "parameters": [ID_PARAM],
                "responses": {
                    "200": {"description": "OK"},
                    "404": {"description": "Not found"},
                },
            }
        },
    )

    spec.components.schema("StandingsEntry", schema=StandingsEntrySchema)
    spec.path(
        path="/standings/{season}",
        operations={
            "get": {
                "summary": "Championship standings for a season",
                "description": "Aggregated from Result rows on every request; nothing is stored redundantly.",
                "parameters": [
                    {"name": "season", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "season": {"type": "integer"},
                                        "data": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/StandingsEntry"},
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
    )

    return spec
