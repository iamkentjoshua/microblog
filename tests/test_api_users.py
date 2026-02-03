from tests.helpers import basic_auth
from app.extensions import db
from app.models import User
import sqlalchemy as sa

def test_create_user(client):
    response = client.post('/api/users', json={
        'username': 'susan',
        'email': 'susan@example.com',
        'password': 'cat'
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == 'susan'
    assert 'password' not in data

def test_create_user_missing_fields(client):
    r = client.post('/api/users', json={'username': 'x'})
    assert r.status_code == 400
    assert 'must include username' in r.get_json()['message']

def test_duplicate_username(client):
    client.post('/api/users', json={
        'username': 'dup',
        'email': 'a@test.com',
        'password': 'dog'
    })

    r = client.post('/api/users', json={
        'username': 'dup',
        'email': 'b@test.com',
        'password': 'dog'
    })

    assert r.status_code == 400

def test_get_user(client):
    client.post('/api/users', json={
        'username': 'joe',
        'email': 'joe@test.com',
        'password': 'dog'
    })

    token = client.post(
        '/api/tokens',
        headers=basic_auth('joe', 'dog')
    ).get_json()['token']

    r = client.get(
        '/api/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert r.status_code == 200
    assert r.get_json()['username'] == 'joe'

def test_user_cannot_update_other_user(client):
    client.post('/api/users', json={
        'username': 'u1', 'email': 'u1@test.com', 'password': 'dog'
    })
    client.post('/api/users', json={
        'username': 'u2', 'email': 'u2@test.com', 'password': 'dog'
    })

    token = client.post(
        '/api/tokens',
        headers=basic_auth('u1', 'dog')
    ).get_json()['token']

    r = client.put(
        '/api/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={'about_me': 'hack'}
    )

    assert r.status_code == 403

def test_admin_can_update_other_user(client, app):
    client.post('/api/users', json={
        'username': 'admin', 'email': 'admin@test.com', 'password': 'dog'
    })

    with app.app_context():
        admin = db.session.scalar(sa.select(User).where(User.username == 'admin'))
        admin.role = 'admin'
        db.session.commit()

    client.post('/api/users', json={
        'username': 'user', 'email': 'user@test.com', 'password': 'dog'
    })

    token = client.post(
        '/api/tokens',
        headers=basic_auth('admin', 'dog')
    ).get_json()['token']

    r = client.put(
        '/api/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={'about_me': 'updated by admin'}
    )

    assert r.status_code == 200
