import requests


def test_dummy():
    response = requests.get('https://httpbin.org/get', timeout=5)
    assert response.status_code == 200, 'Status code is not 200'
