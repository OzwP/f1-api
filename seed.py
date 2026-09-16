"""Seed the database with one F1 season pulled from the Jolpica-F1 API
(https://api.jolpi.ca/ergast/f1), the maintained successor to Ergast.

Usage:
    python seed.py --season 2023

Safe to re-run: every row is looked up by its natural key (name; season +
name for races; race + driver for results) before insert, so seeding the
same season twice updates existing rows instead of duplicating them.

The upstream API describes constructors, not engine suppliers or chassis
names, so those aren't available to pull in. Engine manufacturer is filled
in from a small static, season-specific lookup (CONSTRUCTOR_ENGINES) with
the constructor's own name as a fallback (correct for works teams); "car"
is left unset.
"""
import argparse
import datetime
import time

import requests

from application import create_app
from application.extensions import db
from application.models.Motor import Motor
from application.models.Team import Team
from application.models.Driver import Driver
from application.models.Race import Race
from application.models.Result import Result

DEFAULT_BASE_URL = "https://api.jolpi.ca/ergast/f1"
DEFAULT_SEASON = 2023
REQUEST_DELAY_SECONDS = 0.3

# Known customer-engine deals for the seasons we seed; any constructor not
# listed here is assumed to run its own engine.
CONSTRUCTOR_ENGINES = {
    2023: {
        "red_bull": "Honda RBPT",
        "alphatauri": "Honda RBPT",
        "mclaren": "Mercedes",
        "aston_martin": "Mercedes",
        "williams": "Mercedes",
        "alfa": "Ferrari",
        "haas": "Ferrari",
        "alpine": "Renault",
    },
}


def fetch_json(session, url, **params):
    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()
    time.sleep(REQUEST_DELAY_SECONDS)
    return response.json()["MRData"]


def driver_full_name(driver_payload):
    return f"{driver_payload['givenName']} {driver_payload['familyName']}"


def get_or_create_motor(name):
    motor = Motor.query.filter_by(name=name).first()
    if motor is None:
        motor = Motor(name=name)
        db.session.add(motor)
        db.session.flush()
    return motor


def get_or_create_team(constructor_payload, engine_name):
    motor = get_or_create_motor(engine_name)

    team = Team.query.filter_by(name=constructor_payload["name"]).first()
    if team is None:
        team = Team(name=constructor_payload["name"], motor=motor)
        db.session.add(team)
    else:
        team.motor = motor
    db.session.flush()
    return team


def get_or_create_driver(name, team=None):
    driver = Driver.query.filter_by(name=name).first()
    if driver is None:
        driver = Driver(name=name, team=team)
        db.session.add(driver)
    elif team is not None:
        driver.team = team
    db.session.flush()
    return driver


def get_or_create_race(season, name, circuit, date):
    race = Race.query.filter_by(season=season, name=name).first()
    if race is None:
        race = Race(name=name, circuit=circuit, date=date, season=season)
        db.session.add(race)
    else:
        race.circuit = circuit
        race.date = date
    db.session.flush()
    return race


def upsert_result(race, driver, position, points):
    result = Result.query.filter_by(race_id=race.id, driver_id=driver.id).first()
    if result is None:
        result = Result(race_id=race.id, driver_id=driver.id, position=position, points=points)
        db.session.add(result)
    else:
        result.position = position
        result.points = points


def seed_constructors_and_drivers(session, base_url, season):
    engines = CONSTRUCTOR_ENGINES.get(season, {})

    constructors_data = fetch_json(session, f"{base_url}/{season}/constructors.json", limit=100)
    constructors = constructors_data["ConstructorTable"]["Constructors"]

    teams_by_constructor_id = {}
    for constructor_payload in constructors:
        engine_name = engines.get(constructor_payload["constructorId"], constructor_payload["name"])
        teams_by_constructor_id[constructor_payload["constructorId"]] = get_or_create_team(
            constructor_payload, engine_name
        )

    drivers_data = fetch_json(session, f"{base_url}/{season}/drivers.json", limit=200)
    for driver_payload in drivers_data["DriverTable"]["Drivers"]:
        get_or_create_driver(driver_full_name(driver_payload))

    db.session.commit()
    return teams_by_constructor_id


def seed_races_and_results(session, base_url, season, teams_by_constructor_id):
    races_data = fetch_json(session, f"{base_url}/{season}.json", limit=100)

    for race_payload in races_data["RaceTable"]["Races"]:
        race = get_or_create_race(
            season,
            race_payload["raceName"],
            race_payload["Circuit"]["circuitName"],
            datetime.date.fromisoformat(race_payload["date"]),
        )

        results_data = fetch_json(
            session, f"{base_url}/{season}/{race_payload['round']}/results.json", limit=100
        )
        race_results = results_data["RaceTable"]["Races"]
        if not race_results:
            continue

        for result_payload in race_results[0]["Results"]:
            team = teams_by_constructor_id.get(result_payload["Constructor"]["constructorId"])
            driver = get_or_create_driver(driver_full_name(result_payload["Driver"]), team=team)

            upsert_result(
                race,
                driver,
                position=int(result_payload["position"]),
                points=float(result_payload["points"]),
            )

    db.session.commit()


def seed_season(session, base_url, season):
    teams_by_constructor_id = seed_constructors_and_drivers(session, base_url, season)
    seed_races_and_results(session, base_url, season, teams_by_constructor_id)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", type=int, default=DEFAULT_SEASON, help="F1 season to seed")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Jolpica-F1 API base URL")
    args = parser.parse_args(argv)

    app = create_app()
    with app.app_context():
        seed_season(requests.Session(), args.base_url, args.season)

    print(f"Seeded season {args.season}.")


if __name__ == "__main__":
    main()
