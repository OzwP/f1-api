from dataclasses import dataclass
from flask import Response, request
import flask_restful as fr
import json
from ..models import Motor as Motr, Driver as Drivr, Team as Tm
from setup import db

class Motor(fr.Resource):
    def get(self):
        items = Motr.Motor.query.all()
        data = {}
    
        for item in items:
            data[item.id] = {"name": item.name}
        
        return json.dumps(data)

    def post(self):
        
        motor = Motr.Motor(name=request.json['name'])
    
        db.session.add(motor)
        db.session.commit()

        data = json.dumps({"id" : motor.id})
        return Response(data, status = 201)

class Team(fr.Resource):

    def get(self, id=None):
        
        if not id:

            items = Tm.Team.query.all()
            data = {}
            print(request)
            for item in items:
                
                data[item.id] = {"name": item.name}

            return data
        
        else:
            team = Tm.Team.query.filter_by(id=id).first()

            return {team.id: team.name}

    def post(self):
        motor = Motr.Motor.query.filter_by(name=request.json['motor']).first()

        team = Tm.Team(name=request.json['name'], 
                    car = request.json['car'],
                    motor = motor)
    
        db.session.add(team)
        db.session.commit()

        data = json.dumps({"id" : team.id})
        return Response(data, status = 201)


class Driver(fr.Resource):
    def get(self):
        drivers = Drivr.Driver.query.all()
        
        data = {}

        for driver in drivers:
            data[driver.id] = {}
        
            for column in driver.__table__.columns.keys():
                data[driver.id][column] = getattr(driver, column)

        return data

    def post(self):
        team = Tm.Team.query.filter_by(name=request.json['team']).first()

        driver = Drivr.Driver(name = request.json['name'],
                                team = team)

        db.session.add(driver)
        db.session.commit()

        data = json.dumps({"id" : driver.id})
        return Response(data, status = 201)

    def patch(self, id):

        driver = Drivr.Driver.query.filter_by(id=id).first()
        data = {}
    
        driver.wins = request.json['wins']
        db.session.commit()

        data[driver.id] = {}
        
        for column in driver.__table__.columns.keys():
            data[driver.id][column] = getattr(driver, column)

        return data