def test_list_results(client, seed_data):
    response = client.get("/results")

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 1
    assert body["data"][0]["position"] == 1


def test_get_result_by_id(client, seed_data):
    result = seed_data["result"]

    response = client.get(f"/results/{result.id}")

    assert response.status_code == 200
    assert response.get_json()["data"]["points"] == 25.0


def test_get_missing_result_returns_404(client, seed_data):
    response = client.get("/results/9999")

    assert response.status_code == 404


def test_post_result_valid(client, seed_data):
    race = seed_data["race"]
    driver = seed_data["other_driver"]

    response = client.post("/results", json={
        "race_id": race.id,
        "driver_id": driver.id,
        "position": 2,
        "points": 18.0,
    })

    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["position"] == 2
    assert body["points"] == 18.0


def test_post_result_invalid_missing_fields(client, seed_data):
    response = client.post("/results", json={"race_id": seed_data["race"].id})

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_post_result_invalid_position(client, seed_data):
    race = seed_data["race"]
    driver = seed_data["other_driver"]

    response = client.post("/results", json={
        "race_id": race.id,
        "driver_id": driver.id,
        "position": 0,
        "points": 10.0,
    })

    assert response.status_code == 400


def test_patch_result(client, seed_data):
    result = seed_data["result"]

    response = client.patch(f"/results/{result.id}", json={"points": 26.0})

    assert response.status_code == 200
    assert response.get_json()["data"]["points"] == 26.0


def test_patch_result_invalid(client, seed_data):
    result = seed_data["result"]

    response = client.patch(f"/results/{result.id}", json={"points": -5.0})

    assert response.status_code == 400


def test_delete_result(client, seed_data):
    result = seed_data["result"]

    response = client.delete(f"/results/{result.id}")
    assert response.status_code == 200

    follow_up = client.get(f"/results/{result.id}")
    assert follow_up.status_code == 404
