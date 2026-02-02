import base64

def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {
        'Authorization': f'Basic {token}'
    }
