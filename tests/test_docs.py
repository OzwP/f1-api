def test_openapi_spec_lists_all_resources(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    spec = response.get_json()
    for path in ("/motors", "/teams", "/drivers", "/races", "/results", "/standings/{season}"):
        assert path in spec["paths"]


def test_docs_ui_served(client):
    response = client.get("/docs/")

    assert response.status_code == 200
    assert b"swagger-ui" in response.data
