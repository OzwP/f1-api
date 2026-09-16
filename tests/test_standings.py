import datetime

from application.extensions import db
from application.models.Race import Race
from application.models.Result import Result


def test_standings_ranks_drivers_by_total_points(client, seed_data):
    other_race = Race(name="Spanish Grand Prix", circuit="Circuit de Barcelona-Catalunya",
                       date=datetime.date(2024, 6, 23), season=2024)
    db.session.add(other_race)
    db.session.commit()

    # Hamilton already has 25 points from seed_data's race. Give
    # Verstappen 30 total across two races so he outranks Hamilton.
    db.session.add_all([
        Result(race_id=other_race.id, driver_id=seed_data["other_driver"].id, position=1, points=25.0),
        Result(race_id=seed_data["race"].id, driver_id=seed_data["other_driver"].id, position=2, points=5.0),
    ])
    db.session.commit()

    response = client.get("/standings/2024")

    assert response.status_code == 200
    body = response.get_json()
    assert body["season"] == 2024

    standings = body["data"]
    assert [entry["driver"]["name"] for entry in standings] == ["Max Verstappen", "Lewis Hamilton"]
    assert [entry["points"] for entry in standings] == [30.0, 25.0]
    assert [entry["rank"] for entry in standings] == [1, 2]
    assert standings[1]["driver"]["team"]["name"] == "Mercedes"
    assert standings[0]["driver"]["team"] is None


def test_standings_ties_share_a_rank(client, seed_data):
    db.session.add(
        Result(race_id=seed_data["race"].id, driver_id=seed_data["other_driver"].id, position=2, points=25.0)
    )
    db.session.commit()

    response = client.get("/standings/2024")

    standings = response.get_json()["data"]
    assert [entry["rank"] for entry in standings] == [1, 1]


def test_standings_empty_season_returns_empty_list(client, seed_data):
    response = client.get("/standings/1950")

    assert response.status_code == 200
    assert response.get_json()["data"] == []
