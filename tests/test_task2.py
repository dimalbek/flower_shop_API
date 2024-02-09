import requests


def test_get_login():
    response = requests.get("http://localhost:8000/login")
    assert "email" in response.text
    assert "password" in response.text


def test_post_login_invalid():
    data = {"email": ""}
    response = requests.post("http://localhost:8000/login", data=data)
    assert response.status_code == 422


def test_post_login_valid():
    data = {"email": "test@test.com", "password": "123"}
    response = requests.post(
        "http://localhost:8000/login", data=data, allow_redirects=False
    )
    assert response.status_code == 303
    assert "/profile" in response.headers.get("location")
