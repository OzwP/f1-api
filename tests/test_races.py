def test_list_races(client, seed_data):
    response = client.get("/races")

    assert response.status_code == 200
    assert response.get_json()["total"] == 1


def test_list_races_filtered_by_season(client, seed_data):
    response = client.get("/races?season=2023")

    assert response.status_code == 200
    assert response.get_json()["total"] == 0


def test_get_race_by_id(client, seed_data):
    race = seed_data["race"]

    response = client.get(f"/races/{race.id}")

    assert response.status_code == 200
    assert response.get_json()["data"]["name"] == "Monaco Grand Prix"


def test_get_missing_race_returns_404(client, seed_data):
    response = client.get("/races/9999")

    assert response.status_code == 404


def test_race_results_includes_driver_and_team(client, seed_data):
    race = seed_data["race"]

    response = client.get(f"/races/{race.id}/results")

    assert response.status_code == 200
    results = response.get_json()["data"]
    assert len(results) == 1
    assert results[0]["driver"]["name"] == "Lewis Hamilton"
    assert results[0]["driver"]["team"]["name"] == "Mercedes"
