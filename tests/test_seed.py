from application.models.Driver import Driver
from application.models.Motor import Motor
from application.models.Race import Race
from application.models.Result import Result
from application.models.Team import Team

import seed

SEASON = 2023

CONSTRUCTORS = {
    "MRData": {
        "ConstructorTable": {
            "Constructors": [
                {"constructorId": "red_bull", "name": "Red Bull"},
                {"constructorId": "ferrari", "name": "Ferrari"},
            ]
        }
    }
}

DRIVERS = {
    "MRData": {
        "DriverTable": {
            "Drivers": [
                {"givenName": "Max", "familyName": "Verstappen"},
                {"givenName": "Charles", "familyName": "Leclerc"},
            ]
        }
    }
}

RACES = {
    "MRData": {
        "RaceTable": {
            "Races": [
                {
                    "round": "1",
                    "raceName": "Bahrain Grand Prix",
                    "date": "2023-03-05",
                    "Circuit": {"circuitName": "Bahrain International Circuit"},
                }
            ]
        }
    }
}

RESULTS_ROUND_1 = {
    "MRData": {
        "RaceTable": {
            "Races": [
                {
                    "Results": [
                        {
                            "position": "1",
                            "points": "25",
                            "Driver": {"givenName": "Max", "familyName": "Verstappen"},
                            "Constructor": {"constructorId": "red_bull", "name": "Red Bull"},
                        },
                        {
                            "position": "2",
                            "points": "18",
                            "Driver": {"givenName": "Charles", "familyName": "Leclerc"},
                            "Constructor": {"constructorId": "ferrari", "name": "Ferrari"},
                        },
                    ]
                }
            ]
        }
    }
}


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.routes = {
            f"https://api.jolpi.ca/ergast/f1/{SEASON}/constructors.json": CONSTRUCTORS,
            f"https://api.jolpi.ca/ergast/f1/{SEASON}/drivers.json": DRIVERS,
            f"https://api.jolpi.ca/ergast/f1/{SEASON}.json": RACES,
            f"https://api.jolpi.ca/ergast/f1/{SEASON}/1/results.json": RESULTS_ROUND_1,
        }

    def get(self, url, params=None, timeout=None):
        return FakeResponse(self.routes[url])


def test_seed_season_populates_expected_rows(app, monkeypatch):
    monkeypatch.setattr(seed.time, "sleep", lambda _: None)

    with app.app_context():
        seed.seed_season(FakeSession(), seed.DEFAULT_BASE_URL, SEASON)

        assert Motor.query.count() == 2
        assert {m.name for m in Motor.query.all()} == {"Honda RBPT", "Ferrari"}

        assert Team.query.count() == 2
        red_bull = Team.query.filter_by(name="Red Bull").first()
        assert red_bull.motor.name == "Honda RBPT"

        assert Driver.query.count() == 2
        verstappen = Driver.query.filter_by(name="Max Verstappen").first()
        assert verstappen.team.name == "Red Bull"

        assert Race.query.count() == 1
        race = Race.query.first()
        assert race.name == "Bahrain Grand Prix"
        assert race.season == SEASON

        assert Result.query.count() == 2
        result = Result.query.filter_by(driver_id=verstappen.id).first()
        assert result.position == 1
        assert result.points == 25.0


def test_seed_season_is_idempotent(app, monkeypatch):
    monkeypatch.setattr(seed.time, "sleep", lambda _: None)

    with app.app_context():
        seed.seed_season(FakeSession(), seed.DEFAULT_BASE_URL, SEASON)
        seed.seed_season(FakeSession(), seed.DEFAULT_BASE_URL, SEASON)

        assert Motor.query.count() == 2
        assert Team.query.count() == 2
        assert Driver.query.count() == 2
        assert Race.query.count() == 1
        assert Result.query.count() == 2
