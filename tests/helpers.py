import base64

def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {
        'Authorization': f'Basic {token}'
    }

def register_user(client, username, email, password):
    r = client.post('/auth/register', data={
        'username': username,
        'email': email,
        'password': password,
        'password2': password
    }, follow_redirects=True)

    if r.status_code == 404:
        r = client.post('/register', data={
            'username': username,
            'email': email,
            'password': password,
            'password2': password
        }, follow_redirects=True)

    return r


def login_user(client, username, password):
    r = client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

    if r.status_code == 404:
        r = client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    return r

def logout_user(client):
    r = client.get('/auth/logout', follow_redirects=True)
    if r.status_code == 404:
        r = client.get('/logout', follow_redirects=True)
    return r