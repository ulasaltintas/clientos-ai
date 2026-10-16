
def test_create_company(client):
    # Arrange: Prepare the request data
    company_data = {
        "name": "Test Corp",
        "industry": "Technology",
        "website": "https://testcorp.example",
    }

    # Act: Send the POST request
    response = client.post(
        "/companies",
        json=company_data,
    )

    # Assert: Verify the response
    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Corp"
    assert data["industry"] == "Technology"
    assert data["website"] == "https://testcorp.example"

    assert isinstance(data["id"], int)
    assert "created_at" in data

    # Verify the company can be retrieved
    company_id = data["id"]

    get_response = client.get(
        f"/companies/{company_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Corp"
    #assert get_response.json()["industry"] == "Technology"
    #assert get_response.json()["website"] == "https://testcorp.example"


def test_create_company_without_name(client):
    company_data = {
        "industry": "Technology",
        "website": "https://testcorp.example",
    }

    response = client.post(
        "/companies",
        json=company_data,
    )

    assert response.status_code == 422


def test_create_company_with_unknown_field(client):
    company_data = {
        "name": "Test Corp",
        "industry": "Technology",
        "random_field": "Should not be accepted",
    }

    response = client.post(
        "/companies",
        json=company_data,
    ) # Send the POST request with an unknown field and expect a 422 response

    assert response.status_code == 422


def test_get_nonexistent_company(client):
    response = client.get("/companies/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Company not found"
    }

