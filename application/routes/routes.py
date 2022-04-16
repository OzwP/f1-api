from flask import request
import flask_restful as fr
from ..models import Motor as motorModel, Driver as driverModel, Team as teamModel
from setup import db

def makeData(item, message = None, single = True):
    
    data = {"message": message} if message else {}

    if single:
        
        data[item.id] = {}
        
        for column in item.__table__.columns.keys():
            data[item.id][column] = getattr(item, column)

        return data
        
    
    else:

        for element in item:
            data[element.id] = {}
            
            for column in element.__table__.columns.keys():
                data[element.id][column] = getattr(element, column)


        return data
    
        


class Motor(fr.Resource):
    
    def get(self, id = None):
        
        if not id:

            motors = motorModel.Motor.query.all()
            data = makeData(motors, None, False)

            return data
        
        else:
            motor = motorModel.Motor.query.filter_by(id=id).first()
            data = makeData(motor)

            return data

    def post(self):
        
        motor = motorModel.Motor(name=request.json['name'])
    
        db.session.add(motor)
        db.session.commit()

        data = makeData(motor, "Resource succesfully created")
        return data, 201

    def patch(self, id):

        motor = motorModel.Motor.query.filter_by(id=id).first()

        for column in request.json:
            setattr(motor, column, request.json[column])

        db.session.commit()

        data = makeData(motor, "Resource succesfully updated")

        return data
    
    def delete(self, id):

        motor = motorModel.Motor.query.get(id)

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
            team = teamModel.Team.query.filter_by(id=id).first()
            data = makeData(team)

            return data

    def post(self):
        motor = motorModel.Motor.query.filter_by(name=request.json['motor']).first()

        team = teamModel.Team(name=request.json['name'], 
                    car = request.json['car'],
                    motor = motor)
    
        db.session.add(team)
        db.session.commit()

        data = makeData(team, "Resource succesfully created")
        return data, 201

    def patch(self, id):

        team = teamModel.Team.query.filter_by(id=id).first()

        for column in request.json:
            setattr(team, column, request.json[column])

        db.session.commit()

        data = makeData(team, "Resource succesfully updated")

        return data
    
    def delete(self, id):

        team = teamModel.Team.query.get(id)

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

            driver = driverModel.Driver.query.filter_by(id=id).first()

            data = makeData(driver)

            return data

    def post(self):
        team = teamModel.Team.query.filter_by(name=request.json['team']).first()

        driver = driverModel.Driver(name = request.json['name'],
                                team = team)

        db.session.add(driver)
        db.session.commit()

        data = makeData(driver, "Resource succesfully created")
        return data, 201

    def patch(self, id):

        driver = driverModel.Driver.query.filter_by(id=id).first()

        for column in request.json:
            setattr(driver, column, request.json[column])

        db.session.commit()

        data = makeData(driver, "Resource succesfully updated")

        return data

    def delete(self, id):

        driver = driverModel.Driver.query.get(id)

        db.session.delete(driver)
        db.session.commit()

        data = makeData(driver, "Resource succesfully deleted")
        return data