def test_create_dog(client):
    # előbb egy owner kell
    client.post("/owners", json={"email": "gazdi@example.com", "password": "pw"})
    response = client.post("/dogs", json={
        "name": "Odin",
        "breed": "Tacskó",
        "color": "barna",
        "gender": "kan",
        "owner_id": 1
    })
    assert response.status_code == 201
    assert response.get_json()["name"] == "Rex"
