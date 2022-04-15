from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from models import Team, Driver, Motor
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

@app.get("/")
def index():
    return "Hello World!"


@app.get("/teams")
def get_teams():
    
    items = Team.query.all()
    data = {}
    
    for item in items:
        data[item.id] = {"name": item.name}
        
    return json.dumps(data)

@app.get("/motors")
def get_motors():
    items = Motor.query.all()
    data = {}
    
    for item in items:
        data[item.id] = {"name": item.name}
        
    return json.dumps(data)

# @app.get('/drinks/<id>')
# def get_drink(id):
#     drink = Drink.query.get_or_404(id)
#     return json.dumps({"name" : drink.name, "description" : drink.description})
    

@app.post('/motors')
def add_motor():
    motor = Motor(name=request.json['name'])
    
    db.session.add(motor)
    db.session.commit()

    data = json.dumps({"id" : motor.id})
    return Response(data, status = 201)


@app.post('/teams')
def add_team():
    motor = Motor.query.filter_by(name=request.json['motor']).first()

    team = Team(name=request.json['name'], 
                car = request.json['car'],
                motor = motor)
    
    db.session.add(team)
    db.session.commit()

    data = json.dumps({"id" : team.id})
    return Response(data, status = 201)


# @app.delete("/drinks/<id>")
# def del_drink(id):

#     drink = Drink.query.get_or_404(id)
#     dId = drink.id
#     dName = drink.name
#     db.session.delete(drink)
#     db.session.commit()

#     return {"id" : dId, "name" : dName}