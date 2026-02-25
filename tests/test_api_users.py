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


def test_duplicate_username(create_user):
    create_user('dup', 'a@test.com', 'dog')
    r = create_user('dup', 'b@test.com', 'dog')
    assert r.status_code == 400


def test_get_user(create_user, token_for, bearer_headers, client):
    create_user('joe', 'joe@test.com', 'dog')
    token = token_for('joe', 'dog')

    r = client.get('/api/users/1', headers=bearer_headers(token))
    assert r.status_code == 200
    assert r.get_json()['username'] == 'joe'


def test_user_cannot_update_other_user(create_user, token_for, bearer_headers, client):
    create_user('u1', 'u1@test.com', 'dog')
    create_user('u2', 'u2@test.com', 'dog')

    token = token_for('u1', 'dog')
    r = client.put(
        '/api/users/2',
        headers=bearer_headers(token),
        json={'about_me': 'hack'}
    )
    assert r.status_code == 403


def test_admin_can_update_other_user(create_user, admin_token, bearer_headers, client):
    admin_tok = admin_token('admin', 'dog')
    create_user('user', 'user@test.com', 'dog')

    r = client.put(
        '/api/users/2',
        headers=bearer_headers(admin_tok),
        json={'about_me': 'updated by admin'}
    )
    assert r.status_code == 200


def test_user_can_delete_self(create_user, token_for, admin_token, bearer_headers, client):
    create_user('self', 'self@test.com', 'dog')
    self_tok = token_for('self', 'dog')

    admin_tok = admin_token('admin', 'dog')

    r = client.delete('/api/users/1', headers=bearer_headers(self_tok))
    assert r.status_code == 204

    r2 = client.get('/api/users/1', headers=bearer_headers(self_tok))
    assert r2.status_code == 401

    r3 = client.get('/api/users/1', headers=bearer_headers(admin_tok))
    assert r3.status_code == 404

def test_admin_can_get_users(
    create_user,
    admin_token,
    bearer_headers,
    client
):
    # create admin and some basic users
    admin_tok = admin_token('admin', 'dog')
    create_user('u1', 'u1@test.com', 'dog')
    create_user('u2', 'u2@test.com', 'dog')

    r = client.get('/api/users', headers=bearer_headers(admin_tok))
    assert r.status_code == 200

    data = r.get_json()
    assert isinstance(data, dict)
    assert 'items' in data 
    assert len(data['items']) >= 3

    usernames = {u['username'] for u in data['items']}
    assert {'admin', 'u1', 'u2'} <= usernames

def test_non_admin_cannot_get_users(create_user, token_for, bearer_headers, client):
    create_user('user', 'user@test.com', 'dog')
    token = token_for('user', 'dog')

    r = client.get('/api/users', headers=bearer_headers(token))
    assert r.status_code == 403