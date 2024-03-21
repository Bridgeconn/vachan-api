'''Set testing environment and define common tests'''
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
