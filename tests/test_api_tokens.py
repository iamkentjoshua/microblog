def test_token_creation(client, create_user, basic_auth_headers):
    create_user('bob', 'bob@test.com', 'dog')

    r = client.post('/api/tokens', headers=basic_auth_headers('bob', 'dog'))
    assert r.status_code == 200
    assert 'token' in r.get_json()


def test_token_rate_limit(client, create_user, basic_auth_tuple):
    # create a user that matches your existing test expectations
    create_user('rateuser', 'rateuser@test.com', 'cat')
    auth = basic_auth_tuple('rateuser', 'cat')

    for _ in range(5):
        r = client.post("/api/tokens", auth=auth)
        assert r.status_code == 200

    r = client.post("/api/tokens", auth=auth)
    assert r.status_code == 429


def test_rate_limit_isolated_per_user(client, create_user, basic_auth_tuple):
    create_user('u1', 'u1@test.com', 'cat')
    create_user('u2', 'u2@test.com', 'dog')

    auth1 = basic_auth_tuple('u1', 'cat')
    auth2 = basic_auth_tuple('u2', 'dog')

    for _ in range(5):
        assert client.post("/api/tokens", auth=auth1).status_code == 200

    assert client.post("/api/tokens", auth=auth1).status_code == 429
    assert client.post("/api/tokens", auth=auth2).status_code == 200