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


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_get_users_returns_list(client):
    with patch('app.routes.users.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, 'Juan Perez', 'juan@test.com'),
            (2, 'Maria Lopez', 'maria@test.com'),
        ]
        mock_conn.return_value.cursor.return_value = mock_cursor
        response = client.get('/users')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['name'] == 'Juan Perez'
    assert data[1]['email'] == 'maria@test.com'


def test_get_user_found(client):
    with patch('app.routes.users.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, 'Juan Perez', 'juan@test.com')
        mock_conn.return_value.cursor.return_value = mock_cursor
        response = client.get('/users/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 1
    assert data['name'] == 'Juan Perez'


def test_get_user_not_found(client):
    with patch('app.routes.users.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = mock_cursor
        response = client.get('/users/999')
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_create_user_success(client):
    with patch('app.routes.users.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (42,)
        mock_conn.return_value.cursor.return_value = mock_cursor
        response = client.post('/users', json={'name': 'Juan', 'email': 'juan@test.com'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['id'] == 42
    assert data['name'] == 'Juan'
    assert data['email'] == 'juan@test.com'


def test_create_user_missing_email(client):
    response = client.post('/users', json={'name': 'Juan'})
    assert response.status_code == 400


def test_create_user_missing_name(client):
    response = client.post('/users', json={'email': 'juan@test.com'})
    assert response.status_code == 400


def test_create_user_no_body(client):
    response = client.post('/users')
    assert response.status_code == 400


def test_delete_user_success(client):
    with patch('app.routes.users.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.return_value.cursor.return_value = mock_cursor
        response = client.delete('/users/1')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User deleted'


def test_delete_user_not_found(client):
    with patch('app.routes.users.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = mock_cursor
        response = client.delete('/users/999')
    assert response.status_code == 404
