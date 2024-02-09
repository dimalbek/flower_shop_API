import requests


def test_cart():
    session = requests.session()

    data = {"flower_id": 1}
    response = session.post("http://localhost:8000/cart/items", data=data)
    response = session.get("http://localhost:8000/cart/items", data=data)

    assert "1" in response.text
