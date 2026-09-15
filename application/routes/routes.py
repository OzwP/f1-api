import datetime

from flask import request
import flask_restful as fr
from ..models import (
    Motor as motorModel,
    Driver as driverModel,
    Team as teamModel,
    Race as raceModel,
)
from ..extensions import db

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

            motors = motorModel.Motor.query.all()
            data = makeData(motors, None, False)

            return data
        
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

            teams = teamModel.Team.query.all()
            data = makeData(teams, None, False)

            return data
        
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
        
            drivers = driverModel.Driver.query.all()
            
            data = makeData(drivers, None, False)

            return data
        
        else:

            driver = driverModel.Driver.query.get_or_404(id)

            data = makeData(driver)

            return data

    def post(self):
        driver = driverModel.Driver(name = request.json['name'], team_id = request.json['team_id'])

        db.session.add(driver)
        db.session.commit()

        data = makeData(driver, "Resource succesfully created")
        return data, 201

    def patch(self, id):

        driver = driverModel.Driver.query.get_or_404(id)

        for column in request.json:
            setattr(driver, column, request.json[column])

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

            races = raceModel.Race.query.all()
            data = makeData(races, None, False)

            return data

        else:
            race = raceModel.Race.query.get_or_404(id)
            data = makeData(race)

            return data


class RaceResults(fr.Resource):

    def get(self, id):

        race = raceModel.Race.query.get_or_404(id)

        data = {"data": [serialize_result_with_driver(result) for result in race.results]}

        return data