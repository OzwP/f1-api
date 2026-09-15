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
