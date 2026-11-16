
import pytest
from app import app
from models import db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.drop_all()
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200


def test_create_todo(client):
    response = client.post('/todos', json={
        'title': 'Test Task',
        'description': 'Testing Flask API'
    })

    assert response.status_code == 201
    assert response.json['title'] == 'Test Task'


def test_get_todos(client):
    client.post('/todos', json={'title': 'Test Task'})

    response = client.get('/todos')

    assert response.status_code == 200
    assert len(response.json) == 1


def test_update_todo(client):
    created = client.post('/todos', json={'title': 'Old Task'})
    todo_id = created.json['id']

    response = client.put(f'/todos/{todo_id}', json={
        'title': 'Updated Task',
        'completed': True
    })

    assert response.status_code == 200
    assert response.json['title'] == 'Updated Task'
    assert response.json['completed'] is True


def test_delete_todo(client):
    created = client.post('/todos', json={'title': 'Delete Task'})
    todo_id = created.json['id']

    response = client.delete(f'/todos/{todo_id}')

    assert response.status_code == 200
    assert client.get('/todos').json == []
