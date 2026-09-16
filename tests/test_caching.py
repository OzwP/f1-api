def test_list_endpoint_is_actually_cached(app):
    # The `client`/`seed_data` fixtures run under the testing config's
    # NullCache (so tests never see stale data from one another), which
    # can't demonstrate caching is actually happening. This flips one
    # running app over to SimpleCache to prove @cache_list works: a write
    # that bypasses the API (straight to the DB) should stay invisible to
    # /motors until something calls invalidate_cache(), i.e. until a
    # write goes through the API.
    from application.extensions import cache, db
    from application.models.Motor import Motor

    app.config["CACHE_TYPE"] = "SimpleCache"
    cache.init_app(app)
    client = app.test_client()

    with app.app_context():
        db.session.add(Motor(name="Mercedes PU"))
        db.session.commit()

    first = client.get("/motors")
    assert first.get_json()["total"] == 1

    with app.app_context():
        db.session.add(Motor(name="Ferrari"))
        db.session.commit()

    cached = client.get("/motors")
    assert cached.get_json()["total"] == 1  # stale: still cached from the first call

    client.post("/motors", json={"name": "Red Bull"})  # goes through the API, invalidates

    fresh = client.get("/motors")
    assert fresh.get_json()["total"] == 3


def test_list_motors_reflects_writes(client, seed_data):
    # CACHE_TYPE is NullCache under the testing config, so this mainly
    # guards against a future config change breaking cache invalidation
    # silently: a create must always show up in the very next list call.
    first = client.get("/motors")
    assert first.get_json()["total"] == 1

    client.post("/motors", json={"name": "Ferrari"})

    second = client.get("/motors")
    assert second.get_json()["total"] == 2
    names = {motor["name"] for motor in second.get_json()["data"]}
    assert names == {"Mercedes PU", "Ferrari"}
