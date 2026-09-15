def test_list_drivers(client, seed_data):
    response = client.get("/drivers")

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 2
    names = {driver["name"] for driver in body["data"]}
    assert names == {"Lewis Hamilton", "Max Verstappen"}


def test_get_driver_by_id(client, seed_data):
    driver = seed_data["driver"]

    response = client.get(f"/drivers/{driver.id}")

    assert response.status_code == 200
    assert response.get_json()["data"]["name"] == "Lewis Hamilton"


def test_get_missing_driver_returns_404(client, seed_data):
    response = client.get("/drivers/9999")

    assert response.status_code == 404


def test_post_driver_valid(client, seed_data):
    team = seed_data["other_team"]

    response = client.post("/drivers", json={"name": "Charles Leclerc", "team_id": team.id})

    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["name"] == "Charles Leclerc"
    assert body["team_id"] == team.id


def test_post_driver_invalid_missing_name(client, seed_data):
    response = client.post("/drivers", json={"team_id": seed_data["team"].id})

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_patch_driver(client, seed_data):
    driver = seed_data["other_driver"]
    team = seed_data["team"]

    response = client.patch(f"/drivers/{driver.id}", json={"team_id": team.id})

    assert response.status_code == 200
    assert response.get_json()["data"]["team_id"] == team.id


def test_patch_driver_invalid(client, seed_data):
    driver = seed_data["driver"]

    response = client.patch(f"/drivers/{driver.id}", json={"name": ""})

    assert response.status_code == 400


def test_delete_driver(client, seed_data):
    driver = seed_data["other_driver"]

    response = client.delete(f"/drivers/{driver.id}")
    assert response.status_code == 200

    follow_up = client.get(f"/drivers/{driver.id}")
    assert follow_up.status_code == 404
