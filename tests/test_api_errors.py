from tests.helpers import basic_auth

def test_404_error_format(client):
    r = client.get('/api/users/999')
    assert r.status_code == 401 or r.status_code == 404
