from flask import request
import flask_restful as fr
from ..models import Motor as motorModel, Driver as driverModel, Team as teamModel
from setup import db

def makeData(items, message = None, single = False):
    
    data = {"message": message} if message else {}

    if not single:
        
        for item in items:
            data[item.id] = {}
            
            for column in item.__table__.columns.keys():
                data[item.id][column] = getattr(item, column)


        return data
    
    else:
    
        data[items.id] = {}
        
        for column in items.__table__.columns.keys():
            data[items.id][column] = getattr(items, column)

        return data


class Motor(fr.Resource):
    
    def get(self):
        
        motors = motorModel.Motor.query.all()
        
        data = makeData(motors)
        
        return data

    def post(self):
        
        motor = motorModel.Motor(name=request.json['name'])
    
        db.session.add(motor)
        db.session.commit()

        data = makeData(motor, "Resource succesfully created", True)
        return data, 201

    def delete(self, id):

        motor = motorModel.Motor.query.get(id)

        db.session.delete(motor)
        db.session.commit()

        data = makeData(motor, "Resource succesfully deleted", True)
        return data



class Team(fr.Resource):

    def get(self, id=None):
        
        if not id:

            teams = teamModel.Team.query.all()
            data = makeData(teams)

            return data
        
        else:
            team = teamModel.Team.query.filter_by(id=id).first()
            data = makeData(team, True)

            return data

    def post(self):
        motor = motorModel.Motor.query.filter_by(name=request.json['motor']).first()

        team = teamModel.Team(name=request.json['name'], 
                    car = request.json['car'],
                    motor = motor)
    
        db.session.add(team)
        db.session.commit()

        data = makeData(team)
        return data, 201

    def delete(self, id):

        team = teamModel.Team.query.get(id)

        db.session.delete(team)
        db.session.commit()

        data = makeData(team, "Resource succesfully deleted", True)
        return data



class Driver(fr.Resource):

    def get(self, id = None):
        
        if not id:
        
            drivers = driverModel.Driver.query.all()
            
            data = makeData(drivers)

            return data
        
        else:

            driver = driverModel.Driver.query.filter_by(id=id).first()

            data = makeData(driver, True)

            return data

    def post(self):
        team = teamModel.Team.query.filter_by(name=request.json['team']).first()

        driver = driverModel.Driver(name = request.json['name'],
                                team = team)

        db.session.add(driver)
        db.session.commit()

        data = makeData(driver)
        return data, 201

    def patch(self, id):

        driver = driverModel.Driver.query.filter_by(id=id).first()

        for column in request.json:
            setattr(driver, column, request.json[column])

        db.session.commit()

        data = makeData(driver, "Resource succesfully updated" ,True)

        return data

    def delete(self, id):

        driver = driverModel.Driver.query.get(id)

        db.session.delete(driver)
        db.session.commit()

        data = makeData(driver, "Resource succesfully deleted", True)
        return data