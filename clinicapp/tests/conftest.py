import pytest
from clinicapp import app as flask_app
from clinicapp import index

@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    return flask_app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_login(client):
    # Test GET request to login page
    response = client.get('/login')
    assert response.status_code == 200

    # TC1 - Username, password valid
    response = client.post('/login', data={'username': 'doctor', 'password': '123'})
    assert response.status_code == 302  # Expecting a redirect

    # TC2 - correct username, wrong password
    response = client.post('/login', data={'username': 'doctor', 'password': 'abcxyz'})
    assert b'You should be redirected automatically to the target URL' in response.data

    # TC3 - wrong username, correct password
    response = client.post('/login', data={'username': 'doctorxxxx', 'password': '123'})
    assert b'You should be redirected automatically to the target URL' in response.data


def test_admin_login(client):
    # TC1 - Username, password valid
    response = client.post('/admin-login', data={'username': 'admin', 'password': '123'})
    assert response.status_code == 302  # Expecting a redirect

    response = client.post('/admin-login', data={'username': 'invalidadmin', 'password': '333'})
    assert response.status_code == 302  # Expecting a redirect


def test_logout(client):
    response = client.get('/logout')
    assert response.status_code == 302


