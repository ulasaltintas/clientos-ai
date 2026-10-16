
def test_create_contact(client):
    # Arrange: Create a company first
    company_response = client.post(
        "/companies",
        json={
            "name": "Test Company",
            "industry": "Technology",
        },
    )

    assert company_response.status_code == 201

    company_id = company_response.json()["id"]

    # Act: Create a contact associated with the company
    contact_response = client.post(
        "/contacts",
        json={
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "phone": "+49123456789",
            "job_title": "Developer",
            "company_id": company_id,
        },
    )

    # Assert
    assert contact_response.status_code == 201

    data = contact_response.json()

    assert data["first_name"] == "John"
    assert data["last_name"] == "Smith"
    assert data["email"] == "john@example.com"
    assert data["company_id"] == company_id
    assert isinstance(data["id"], int)

    # Verify the contact can be retrieved
    contact_id = data["id"]

    get_response = client.get(
        f"/contacts/{contact_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["email"] == "john@example.com"
    

def test_create_contact_with_nonexistent_company(client):
    contact_data = {
        "first_name": "Emma",
        "last_name": "Wilson",
        "email": "emma@example.com",
        "company_id": 999999,
    }

    response = client.post(
        "/contacts",
        json=contact_data,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Company not found"
    }



def test_create_contact_with_duplicate_email(client):
    # Create a company
    company_response = client.post(
        "/companies",
        json={"name": "Duplicate Test Company"},
    )

    assert company_response.status_code == 201
    company_id = company_response.json()["id"]

    # Create the first contact
    contact_data = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com",
        "company_id": company_id,
    }

    first_response = client.post(
        "/contacts",
        json=contact_data,
    )

    assert first_response.status_code == 201

    # Attempt to create another contact with the same email
    duplicate_data = {
        "first_name": "Another",
        "last_name": "Person",
        "email": "john@example.com",
        "company_id": company_id,
    }

    duplicate_response = client.post(
        "/contacts",
        json=duplicate_data,
    )

    assert duplicate_response.status_code == 409



def test_same_email_allowed_in_different_companies(client):
    # Arrange: Create two different companies
    company_a = client.post(
        "/companies",
        json={"name": "Company A"},
    )

    company_b = client.post(
        "/companies",
        json={"name": "Company B"},
    )

    assert company_a.status_code == 201
    assert company_b.status_code == 201

    company_a_id = company_a.json()["id"]
    company_b_id = company_b.json()["id"]

    # Create a contact in Company A
    contact_a = client.post(
        "/contacts",
        json={
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "company_id": company_a_id,
        },
    )

    # Create a contact in Company B with the SAME email
    contact_b = client.post(
        "/contacts",
        json={
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "company_id": company_b_id,
        },
    )

    # Assert: Both should succeed
    assert contact_a.status_code == 201
    assert contact_b.status_code == 201

    # Each contact has a different ID
    assert contact_a.json()["id"] != contact_b.json()["id"]

    # But both share the same email
    assert contact_a.json()["email"] == contact_b.json()["email"]

    # And belong to different companies
    assert contact_a.json()["company_id"] != contact_b.json()["company_id"]
