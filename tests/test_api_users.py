from tests.helpers import basic_auth

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
