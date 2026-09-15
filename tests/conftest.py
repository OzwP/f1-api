import datetime

import pytest

from application import create_app
from application.extensions import db
from application.models.Motor import Motor
from application.models.Team import Team
from application.models.Driver import Driver
from application.models.Race import Race
from application.models.Result import Result


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seed_data(app):
    motor = Motor(name="Mercedes PU")
    team = Team(name="Mercedes", car="W15", motor=motor)
    other_team = Team(name="Ferrari", car="SF-24")
    driver = Driver(name="Lewis Hamilton", team=team)
    other_driver = Driver(name="Max Verstappen")
    race = Race(name="Monaco Grand Prix", circuit="Circuit de Monaco",
                date=datetime.date(2024, 5, 26), season=2024)

    db.session.add_all([motor, team, other_team, driver, other_driver, race])
    db.session.commit()

    result = Result(race_id=race.id, driver_id=driver.id, position=1, points=25.0)
    db.session.add(result)
    db.session.commit()

    return {
        "motor": motor,
        "team": team,
        "other_team": other_team,
        "driver": driver,
        "other_driver": other_driver,
        "race": race,
        "result": result,
    }
