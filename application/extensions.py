"""Flask extension instances.

``db`` is instantiated here (unbound) and wired to each app via
``init_app()`` inside ``create_app()``, instead of being created against a
module-level ``app`` singleton.

Flask-RESTful's ``Api`` doesn't support being re-bound to a second app once
its resources are registered (each ``add_resource()`` call attaches routes
directly to whichever app it's bound to), so it isn't a shared singleton
here — ``create_app()`` builds a fresh ``Api(app)`` each time, which is what
lets it be called more than once (e.g. once per test).
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
