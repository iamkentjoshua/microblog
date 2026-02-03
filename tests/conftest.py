import pytest
from app import create_app
from app.extensions import db
from config import Config
from app.models import User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    RATELIMIT_STORAGE_URI = "memory://"

@pytest.fixture
def app():
    app = create_app(TestConfig)

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
def user(app):
    u = User(username="john", email="john@example.com")
    u.set_password("cat")
    db.session.add(u)
    db.session.commit()
    return u.username

@pytest.fixture
def user2(app):
    u = User(username="susan", email="susan@example.com")
    u.set_password("dog")
    db.session.add(u)
    db.session.commit()
    return u.username
