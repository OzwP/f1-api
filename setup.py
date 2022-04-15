from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__)
api = Api()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)