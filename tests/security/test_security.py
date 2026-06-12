import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def client():
    with patch('app.db.get_connection') as mock:
        mock.return_value = MagicMock()
        mock.return_value.cursor.return_value = MagicMock()
        app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_non_integer_user_id_rejected(client):
    # Flask rechaza rutas que no matcheen <int:user_id>
    response = client.get('/users/DROP-TABLE')
    assert response.status_code == 404


def test_health_no_secrets_exposed(client):
    response = client.get('/health')
    body = str(response.get_json())
    assert 'DATABASE_URL' not in body
    assert 'password' not in body.lower()


def test_post_without_json_returns_400(client):
    response = client.post('/users', data='datos maliciosos', content_type='text/plain')
    assert response.status_code == 400


def test_empty_name_rejected(client):
    response = client.post('/users', json={'name': '', 'email': 'test@test.com'})
    assert response.status_code == 400


def test_empty_email_rejected(client):
    response = client.post('/users', json={'name': 'Test', 'email': ''})
    assert response.status_code == 400


def test_blank_spaces_name_rejected(client):
    response = client.post('/users', json={'name': '   ', 'email': 'test@test.com'})
    assert response.status_code == 400
