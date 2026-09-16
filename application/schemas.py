from marshmallow import Schema, fields, validate


class DriverSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    team_id = fields.Integer(required=False, allow_none=True)


class DriverPatchSchema(DriverSchema):
    name = fields.String(required=False, validate=validate.Length(min=1))


class ResultSchema(Schema):
    race_id = fields.Integer(required=True)
    driver_id = fields.Integer(required=True)
    position = fields.Integer(required=True, validate=validate.Range(min=1))
    points = fields.Float(required=True, validate=validate.Range(min=0))


class ResultPatchSchema(ResultSchema):
    race_id = fields.Integer(required=False)
    driver_id = fields.Integer(required=False)
    position = fields.Integer(required=False, validate=validate.Range(min=1))
    points = fields.Float(required=False, validate=validate.Range(min=0))


driver_schema = DriverSchema()
driver_patch_schema = DriverPatchSchema()
result_schema = ResultSchema()
result_patch_schema = ResultPatchSchema()


# The schemas below aren't wired into request validation (Motor/Team/Race
# POST/PATCH still accept whatever's in request.json, same as before this
# phase) — they exist to describe response shapes for the OpenAPI docs in
# application/docs.py.
class MotorSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)


class TeamSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    car = fields.String(required=False, allow_none=True)
    motor_id = fields.Integer(required=True)


class RaceSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    circuit = fields.String(required=True)
    date = fields.Date(required=True)
    season = fields.Integer(required=True)


class TeamRefSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class DriverRefSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    team = fields.Nested(TeamRefSchema, allow_none=True)


class StandingsEntrySchema(Schema):
    rank = fields.Integer()
    points = fields.Float()
    driver = fields.Nested(DriverRefSchema)
