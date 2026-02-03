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

def test_token_rate_limit(client, user):
    auth = (user, "cat")  # user is now username string

    for _ in range(5):
        r = client.post("/api/tokens", auth=auth)
        assert r.status_code == 200

    r = client.post("/api/tokens", auth=auth)
    assert r.status_code == 429

def test_rate_limit_isolated_per_user(client, user, user2):
    auth1 = (user, "cat")
    auth2 = (user2, "dog")

    for _ in range(5):
        client.post("/api/tokens", auth=auth1)

    assert client.post("/api/tokens", auth=auth1).status_code == 429
    assert client.post("/api/tokens", auth=auth2).status_code == 200
