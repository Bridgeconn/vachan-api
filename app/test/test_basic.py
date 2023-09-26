'''Basic test to check App'''

from . import client

def test_default_api():
    '''test the default API endpoint and check if App is up'''
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>Vachan API</title>" in response.text
