from setup import app, api
from application.routes.routes import Team, Motor, Driver

@app.get("/")
def index():
    return "Hello World!"

api.add_resource(Team, "/teams", "/teams/<id>")
api.add_resource(Motor, "/motors", "/motors/<id>")  
api.add_resource(Driver, "/drivers", "/drivers/<id>")  


api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)