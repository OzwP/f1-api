from setup import app, api
from application.routes.routes import Team, Motor, Driver

@app.get("/")
def index():
    return "Hello World!"

api.add_resource(Team, "/teams", "/teams/<id>")
api.add_resource(Motor, "/motors", "/motors/<id>")  
api.add_resource(Driver, "/drivers", "/drivers/<id>")  

# @app.get("/motors")

# @app.get('/drinks/<id>')
# def get_drink(id):
#     drink = Drink.query.get_or_404(id)
#     return json.dumps({"name" : drink.name, "description" : drink.description})
    

# @app.post('/motors')
    


# @app.post('/teams')


# @app.delete("/drinks/<id>")
# def del_drink(id):

#     drink = Drink.query.get_or_404(id)
#     dId = drink.id
#     dName = drink.name
#     db.session.delete(drink)
#     db.session.commit()

#     return {"id" : dId, "name" : dName}

api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)