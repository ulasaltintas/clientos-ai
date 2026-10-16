
def test_create_deal(client):
    # Arrange: Create a company
    company_response = client.post(
        "/companies",
        json={
            "name": "Deal Test Company",
            "industry": "Technology",
        },
    )

    assert company_response.status_code == 201

    company_id = company_response.json()["id"]

    # Act: Create a deal for that company
    deal_response = client.post(
        "/deals",
        json={
            "title": "Enterprise Software Subscription",
            "value": "12000.50",
            "stage": "proposal",
            "company_id": company_id,
            "contact_id": None,
            "expected_close_date": "2026-12-15",
        },
    )

    # Assert: Verify the response
    assert deal_response.status_code == 201

    data = deal_response.json()

    assert data["title"] == "Enterprise Software Subscription"
    assert data["value"] == "12000.50"
    assert data["stage"] == "proposal"
    assert data["company_id"] == company_id
    assert data["contact_id"] is None
    assert data["expected_close_date"] == "2026-12-15"

    assert isinstance(data["id"], int)
    assert "created_at" in data

    # Verify that the deal can be retrieved
    deal_id = data["id"]

    get_response = client.get(
        f"/deals/{deal_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["title"] == (
        "Enterprise Software Subscription"
    )


def test_create_deal_with_negative_value(client):
    response = client.post(
        "/deals",
        json={
            "title": "Invalid Deal",
            "value": "-500.00",
            "company_id": 1,
        },
    )

    assert response.status_code == 422



def test_create_deal_with_nonexistent_company(client):
    response = client.post(
        "/deals",
        json={
            "title": "Unknown Company Deal",
            "value": "1000.00",
            "company_id": 999999,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Company not found"
    }



def test_create_deal_with_contact_from_another_company(client):
    # Create two companies
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

    # Create a contact belonging to Company A
    contact_response = client.post(
        "/contacts",
        json={
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "company_id": company_a_id,
        },
    )

    assert contact_response.status_code == 201

    contact_id = contact_response.json()["id"]

    # Attempt to create a deal for Company B
    # using a contact from Company A
    deal_response = client.post(
        "/deals",
        json={
            "title": "Invalid Relationship Deal",
            "value": "5000.00",
            "company_id": company_b_id,
            "contact_id": contact_id,
        },
    )

    assert deal_response.status_code == 422

    assert deal_response.json() == {
        "detail": "Contact does not belong to this company"
    }
    


def test_update_deal_stage(client):
    # Create a company
    company_response = client.post(
        "/companies",
        json={"name": "Pipeline Test Company"},
    )

    assert company_response.status_code == 201
    company_id = company_response.json()["id"]

    # Create a deal with the default stage: lead
    deal_response = client.post(
        "/deals",
        json={
            "title": "New Sales Opportunity",
            "value": "5000.00",
            "company_id": company_id,
        },
    )

    assert deal_response.status_code == 201
    deal_id = deal_response.json()["id"]
    assert deal_response.json()["stage"] == "lead"

    # Update the stage
    response = client.patch(
        f"/deals/{deal_id}",
        json={"stage": "won"},
    )

    assert response.status_code == 200
    assert response.json()["stage"] == "won"

    # Verify the change was saved
    get_response = client.get(f"/deals/{deal_id}")

    assert get_response.status_code == 200
    assert get_response.json()["stage"] == "won"



def test_update_deal_value(client):
    company_response = client.post(
        "/companies",
        json={"name": "Revenue Test Company"},
    )

    assert company_response.status_code == 201
    company_id = company_response.json()["id"]

    deal_response = client.post(
        "/deals",
        json={
            "title": "Software License",
            "value": "1000.00",
            "company_id": company_id,
        },
    )

    assert deal_response.status_code == 201
    deal_id = deal_response.json()["id"]

    # Change only the monetary value
    response = client.patch(
        f"/deals/{deal_id}",
        json={"value": "2500.75"},
    )

    assert response.status_code == 200
    assert response.json()["value"] == "2500.75"

    # Other fields must remain unchanged
    assert response.json()["title"] == "Software License"
    assert response.json()["stage"] == "lead"

    get_response = client.get(f"/deals/{deal_id}")

    assert get_response.status_code == 200
    assert get_response.json()["value"] == "2500.75"



def test_update_deal_with_contact_from_another_company(client):
    # Create two companies
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

    # Create a contact belonging to Company A
    contact_response = client.post(
        "/contacts",
        json={
            "first_name": "Emma",
            "last_name": "Wilson",
            "email": "emma@example.com",
            "company_id": company_a_id,
        },
    )

    assert contact_response.status_code == 201
    contact_id = contact_response.json()["id"]

    # Create a deal belonging to Company B
    deal_response = client.post(
        "/deals",
        json={
            "title": "Company B Opportunity",
            "value": "3000.00",
            "company_id": company_b_id,
        },
    )

    assert deal_response.status_code == 201
    deal_id = deal_response.json()["id"]

    # Attempt to assign Company A's contact
    response = client.patch(
        f"/deals/{deal_id}",
        json={"contact_id": contact_id},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Contact does not belong to this company"
    }

    # Verify the rejected update did not modify the deal
    get_response = client.get(f"/deals/{deal_id}")

    assert get_response.status_code == 200
    assert get_response.json()["company_id"] == company_b_id
    assert get_response.json()["contact_id"] is None


def test_delete_deal(client):
    # Create a company
    company_response = client.post(
        "/companies",
        json={"name": "Delete Test Company"},
    )

    assert company_response.status_code == 201
    company_id = company_response.json()["id"]

    # Create a deal
    deal_response = client.post(
        "/deals",
        json={
            "title": "Temporary Deal",
            "value": "500.00",
            "company_id": company_id,
        },
    )

    assert deal_response.status_code == 201
    deal_id = deal_response.json()["id"]

    # Delete the deal
    response = client.delete(f"/deals/{deal_id}")

    assert response.status_code == 204
    assert response.content == b""

    # Verify the deal no longer exists
    get_response = client.get(f"/deals/{deal_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Deal not found"
    }



def test_delete_nonexistent_deal(client):
    response = client.delete("/deals/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deal not found"
    }



def test_update_nonexistent_deal(client):
    response = client.patch(
        "/deals/999999",
        json={"stage": "won"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deal not found"
    }



def test_update_deal_with_null_title(client):
    # Create a company
    company_response = client.post(
        "/companies",
        json={"name": "Null Validation Company"},
    )

    assert company_response.status_code == 201
    company_id = company_response.json()["id"]

    # Create a deal
    deal_response = client.post(
        "/deals",
        json={
            "title": "Important Deal",
            "value": "2500.00",
            "company_id": company_id,
        },
    )

    assert deal_response.status_code == 201
    deal_id = deal_response.json()["id"]

    # Attempt to clear a required field
    response = client.patch(
        f"/deals/{deal_id}",
        json={"title": None},
    )

    assert response.status_code == 422

    # Verify the original title remains unchanged
    get_response = client.get(f"/deals/{deal_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Important Deal"
