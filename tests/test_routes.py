import pytest
from app import app
from app.models import Prompt  # assuming this is your model
from flask import session
from unittest.mock import patch

def test_index_route(monkeypatch):
    # Mock the database query
    fake_prompts = [
        Prompt(category='Design', text='Create a logo'),
        Prompt(category='Art', text='Sketch a cat'),
    ]

    monkeypatch.setattr(Prompt.query, "all", lambda: fake_prompts)

    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert b'Create a logo' in response.data
        assert b'Sketch a cat' in response.data
