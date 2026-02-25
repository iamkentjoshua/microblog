import pytest
import sqlalchemy as sa
from app import create_app
from app.extensions import db
from config import Config
from app.models import User
from tests.helpers import basic_auth

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    RATELIMIT_STORAGE_URI = "memory://"

@pytest.fixture
def app():
    app = create_app(TestConfig)

    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,   
        DEBUG=True,               
        LOGIN_DISABLED=False,     
    )

    ctx = app.app_context()
    ctx.push()

    db.create_all()
    yield app

    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def basic_auth_headers():
    """Factory: build Basic Auth headers using your tests.helpers.basic_auth()."""
    def _hdr(username, password):
        return basic_auth(username, password)
    return _hdr


@pytest.fixture
def basic_auth_tuple():
    """Factory: build (username, password) tuples for Flask test client auth=... usage."""
    def _t(username, password):
        return (username, password)
    return _t

@pytest.fixture
def create_user(client):
    """
    Factory: create a user via API.
    Returns the response object (and convenience: parsed json).
    """
    def _create_user(username, email=None, password="dog", **extra_fields):
        if email is None:
            email = f"{username}@test.com"

        payload = {
            "username": username,
            "email": email,
            "password": password,
            **extra_fields,
        }
        return client.post("/api/users", json=payload)

    return _create_user

@pytest.fixture
def token_for(client):
    """
    Factory: create a bearer token for existing user credentials.
    """
    def _token_for(username, password="dog"):
        res = client.post("/api/tokens", headers=basic_auth(username, password))
        assert res.status_code == 200, res.get_json()
        data = res.get_json()
        assert "token" in data
        return data["token"]

    return _token_for

@pytest.fixture
def bearer_headers():
    """
    Helper: build Authorization header.
    """
    def _headers(token):
        return {"Authorization": f"Bearer {token}"}
    return _headers


@pytest.fixture
def make_admin(app):
    """
    Factory: promote a user to admin directly in DB.
    """
    def _make_admin(username):
        with app.app_context():
            user = db.session.scalar(sa.select(User).where(User.username == username))
            assert user is not None, f"User {username} not found"
            user.role = "admin"
            db.session.commit()
    return _make_admin


@pytest.fixture
def admin_token(create_user, make_admin, token_for):
    """
    Convenience fixture: ensures an admin user exists and returns their token.
    """
    def _admin_token(username="admin", password="dog"):
        create_user(username=username, email=f"{username}@test.com", password=password)
        make_admin(username)
        return token_for(username, password)
    return _admin_token