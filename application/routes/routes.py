import datetime

from flask import request
import flask_restful as fr
from marshmallow import ValidationError

from ..models import (
    Motor as motorModel,
    Driver as driverModel,
    Team as teamModel,
    Race as raceModel,
    Result as resultModel,
)
from ..extensions import db
from ..schemas import (
    driver_schema,
    driver_patch_schema,
    result_schema,
    result_patch_schema,
)

def serialize(item):
    def to_json_value(value):
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.isoformat()
        return value

    return {
        column: to_json_value(getattr(item, column))
        for column in item.__table__.columns.keys()
    }


def makeData(item, message = None, single = True):

    data = {"message": message} if message else {}

    if single:
        data["data"] = serialize(item)
    else:
        data["data"] = [serialize(element) for element in item]

    return data


def paginated_data(query):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    result = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return {
        "data": [serialize(item) for item in result.items],
        "page": result.page,
        "per_page": result.per_page,
        "total": result.total,
        "pages": result.pages,
    }


def load_or_400(schema, json_body):
    try:
        return schema.load(json_body or {})
    except ValidationError as err:
        fr.abort(400, message="Validation error", errors=err.messages)


def serialize_result_with_driver(result):
    driver = result.driver
    team = driver.team

    return {
        "id": result.id,
        "position": result.position,
        "points": result.points,
        "driver": {
            "id": driver.id,
            "name": driver.name,
            "team": {"id": team.id, "name": team.name} if team else None,
        },
    }


class Motor(fr.Resource):
    
    def get(self, id = None):
        
        if not id:
            return paginated_data(db.select(motorModel.Motor))

        else:
            motor = motorModel.Motor.query.get_or_404(id)
            data = makeData(motor)

            return data

    def post(self):
        
        motor = motorModel.Motor(name=request.json['name'])
    
        db.session.add(motor)
        db.session.commit()

        data = makeData(motor, "Resource succesfully created")
        return data, 201

    def patch(self, id):

        motor = motorModel.Motor.query.get_or_404(id)

        for column in request.json:
            setattr(motor, column, request.json[column])

        db.session.commit()

        data = makeData(motor, "Resource succesfully updated")

        return data
    
    def delete(self, id):

        motor = motorModel.Motor.query.get_or_404(id)

        db.session.delete(motor)
        db.session.commit()

        data = makeData(motor, "Resource succesfully deleted")
        return data



class Team(fr.Resource):

    def get(self, id=None):
        
        if not id:
            return paginated_data(db.select(teamModel.Team))

        else:
            team = teamModel.Team.query.get_or_404(id)
            data = makeData(team)

            return data

    def post(self):
        team = teamModel.Team(name=request.json['name'],
                    car = request.json['car'],
                    motor_id = request.json['motor_id'])

        db.session.add(team)
        db.session.commit()

        data = makeData(team, "Resource succesfully created")
        return data, 201

    def patch(self, id):

        team = teamModel.Team.query.get_or_404(id)

        for column in request.json:
            setattr(team, column, request.json[column])

        db.session.commit()

        data = makeData(team, "Resource succesfully updated")

        return data
    
    def delete(self, id):

        team = teamModel.Team.query.get_or_404(id)

        db.session.delete(team)
        db.session.commit()

        data = makeData(team, "Resource succesfully deleted")
        return data



class Driver(fr.Resource):

    def get(self, id = None):
        
        if not id:
            return paginated_data(db.select(driverModel.Driver))

        else:

            driver = driverModel.Driver.query.get_or_404(id)

            data = makeData(driver)

            return data

    def post(self):
        payload = load_or_400(driver_schema, request.json)

        driver = driverModel.Driver(name=payload["name"], team_id=payload.get("team_id"))

        db.session.add(driver)
        db.session.commit()

        data = makeData(driver, "Resource succesfully created")
        return data, 201

    def patch(self, id):

        driver = driverModel.Driver.query.get_or_404(id)

        payload = load_or_400(driver_patch_schema, request.json)

        for column, value in payload.items():
            setattr(driver, column, value)

        db.session.commit()

        data = makeData(driver, "Resource succesfully updated")

        return data

    def delete(self, id):

        driver = driverModel.Driver.query.get_or_404(id)

        db.session.delete(driver)
        db.session.commit()

        data = makeData(driver, "Resource succesfully deleted")
        return data



class Race(fr.Resource):

    def get(self, id = None):

        if not id:
            query = db.select(raceModel.Race)

            season = request.args.get("season", type=int)
            if season is not None:
                query = query.where(raceModel.Race.season == season)

            return paginated_data(query)

        else:
            race = raceModel.Race.query.get_or_404(id)
            data = makeData(race)

            return data


class RaceResults(fr.Resource):

    def get(self, id):

        race = raceModel.Race.query.get_or_404(id)

        data = {"data": [serialize_result_with_driver(result) for result in race.results]}

        return data


class Result(fr.Resource):

    def get(self, id = None):

        if not id:
            return paginated_data(db.select(resultModel.Result))

        result = resultModel.Result.query.get_or_404(id)

        data = makeData(result)

        return data

    def post(self):
        payload = load_or_400(result_schema, request.json)

        result = resultModel.Result(**payload)

        db.session.add(result)
        db.session.commit()

        data = makeData(result, "Resource succesfully created")
        return data, 201

    def patch(self, id):

        result = resultModel.Result.query.get_or_404(id)

        payload = load_or_400(result_patch_schema, request.json)

        for column, value in payload.items():
            setattr(result, column, value)

        db.session.commit()

        data = makeData(result, "Resource succesfully updated")

        return data

    def delete(self, id):

        result = resultModel.Result.query.get_or_404(id)

        db.session.delete(result)
        db.session.commit()

        data = makeData(result, "Resource succesfully deleted")
        return data