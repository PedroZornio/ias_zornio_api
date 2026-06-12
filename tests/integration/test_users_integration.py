import uuid
import pytest
from app import create_app


@pytest.fixture(scope='module')
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_health_integration(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_full_user_lifecycle(client):
    email = f"integ_{uuid.uuid4().hex[:8]}@example.com"

    # Crear usuario
    response = client.post('/users', json={'name': 'Test Integration', 'email': email})
    assert response.status_code == 201
    user_id = response.get_json()['id']

    # Obtener por ID
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    assert response.get_json()['email'] == email

    # Listar — debe aparecer en la lista
    response = client.get('/users')
    assert response.status_code == 200
    ids = [u['id'] for u in response.get_json()]
    assert user_id in ids

    # Eliminar
    response = client.delete(f'/users/{user_id}')
    assert response.status_code == 200

    # Verificar que ya no existe
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 404


def test_get_nonexistent_user(client):
    response = client.get('/users/999999')
    assert response.status_code == 404


def test_delete_nonexistent_user(client):
    response = client.delete('/users/999999')
    assert response.status_code == 404
