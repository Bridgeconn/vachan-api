from . import client

def test_default_api():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "App is up and running"}