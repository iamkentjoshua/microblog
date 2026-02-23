from tests.helpers import register_user, login_user
from app.models import Post
from app.extensions import db


def test_seed_posts(client):
    register_user(client, 'alice', 'alice@test.com', 'cat')
    login_user(client, 'alice', 'cat')

    r = client.post('/seed_posts', json={'count': 3})
    assert r.status_code == 200
    assert r.is_json
    assert r.get_json()['created'] == 3

    with client.application.app_context():
        assert Post.query.count() == 3


def test_edit_post(client):
    register_user(client, 'john', 'john@test.com', 'cat')
    login_user(client, 'john', 'cat')

    # sanity check: a protected endpoint should be accessible now
    assert client.get('/index').status_code == 200
    
    # Create a post via the same form field used by PostForm
    client.post('/', data={'post': 'Original post'}, follow_redirects=True)

    with client.application.app_context():
        post = Post.query.first()
        assert post is not None

        r = client.post(
            f'/edit_post/{post.id}',
            data={'post': 'Updated post'},
            follow_redirects=True
        )
        assert r.status_code == 200

        updated = db.session.get(Post, post.id)
        assert updated.body == 'Updated post'


def test_delete_post(client):
    register_user(client, 'carol', 'carol@test.com', 'cat')
    login_user(client, 'carol', 'cat')

    client.post('/', data={'post': 'Delete me'}, follow_redirects=True)

    with client.application.app_context():
        post = Post.query.first()
        assert post is not None

        r = client.post(
            f'/delete_post/{post.id}',
            follow_redirects=True
        )
        assert r.status_code == 200
        assert Post.query.get(post.id) is None