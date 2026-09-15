def test_list_motors(client, seed_data):
    response = client.get("/motors")

    assert response.status_code == 200
    assert response.get_json()["total"] == 1


def test_get_missing_motor_returns_404(client, seed_data):
    response = client.get("/motors/9999")

    assert response.status_code == 404


def test_post_motor(client, seed_data):
    response = client.post("/motors", json={"name": "Ferrari PU"})

    assert response.status_code == 201
    assert response.get_json()["data"]["name"] == "Ferrari PU"


def test_list_teams(client, seed_data):
    response = client.get("/teams")

    assert response.status_code == 200
    assert response.get_json()["total"] == 2


def test_get_team_by_id(client, seed_data):
    team = seed_data["team"]

    response = client.get(f"/teams/{team.id}")

    assert response.status_code == 200
    assert response.get_json()["data"]["motor_id"] == seed_data["motor"].id


def test_get_missing_team_returns_404(client, seed_data):
    response = client.get("/teams/9999")

    assert response.status_code == 404
