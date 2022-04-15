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
    
    def get(self):
        items = Tm.Team.query.all()
        data = {}

        for item in items:
            
            data[item.id] = {"name": item.name}

        return data

    def post(self):
        motor = Motr.Motor.query.filter_by(name=request.json['motor']).first()

        team = Tm.Team(name=request.json['name'], 
                    car = request.json['car'],
                    motor = motor)
    
        db.session.add(team)
        db.session.commit()

        data = json.dumps({"id" : team.id})
        return Response(data, status = 201)

