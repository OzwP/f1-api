from flask import Flask
from flask_restful import Api

from .config import config
from .extensions import db


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    from .routes.routes import Driver, Motor, Team

    api = Api(app)
    api.add_resource(Motor, "/motors", "/motors/<int:id>")
    api.add_resource(Team, "/teams", "/teams/<int:id>")
    api.add_resource(Driver, "/drivers", "/drivers/<int:id>")

    @app.get("/")
    def index():
        return "Hello World!"

    return app
