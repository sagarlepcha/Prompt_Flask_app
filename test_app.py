import pytest
import os
import tempfile
from app import app, db
from models import Prompt

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['TESTING'] = True
    app.secret_key = 'testkey'

    with app.app_context():
        db.create_all()
        prompt = Prompt(text='Sample prompt', category='Test')
        db.session.add(prompt)
        db.session.commit()

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Sample prompt" in response.data

def test_login_logout(client):
    # Signup a test user directly in the DB
    import sqlite3
    with sqlite3.connect("users.db") as conn:
        conn.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                     ("testuser", "testpass", 1))
    # Login
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    assert b"Logout" in response.data or b"Admin" in response.data

    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert b"Login" in response.data

def test_admin_dashboard_access_control(client):
    response = client.get('/admin')
    assert response.status_code == 302  # redirect to login
