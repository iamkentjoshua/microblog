from tests.helpers import basic_auth

def test_token_creation(client):
    client.post('/api/users', json={
        'username': 'bob',
        'email': 'bob@test.com',
        'password': 'dog'
    })

    r = client.post('/api/tokens', headers=basic_auth('bob', 'dog'))
    assert r.status_code == 200
    assert 'token' in r.get_json()
