from tests.helpers import basic_auth

def test_protected_endpoint_requires_auth(client):
    response = client.get('/api/users/1')
    assert response.status_code == 401

def test_basic_auth_invalid_password(client):
    client.post('/api/users', json={
        'username': 'alice',
        'email': 'alice@test.com',
        'password': 'cat'
    })

    response = client.post(
        '/api/tokens',
        headers={
            'Authorization': 'Basic YWxpY2U6d3Jvbmc='  # alice:wrong
        }
    )

    assert response.status_code == 401
    assert response.get_json()['error'] == 'Unauthorized'

def test_token_auth_missing_token(client):
    response = client.get('/api/users')
    assert response.status_code == 401

def test_token_auth_invalid_token(client):
    response = client.get(
        '/api/users',
        headers={'Authorization': 'Bearer invalidtoken'}
    )

    assert response.status_code == 401
