def test_create_challenge_success(client, test_user):
    payload = {
        "title": "Severe Arsenic Contamination in Wells",
        "description": "High arsenic levels detected in groundwater across rural drinking wells.",
        "submitted_by": test_user.id,
        "category": "Water & Sanitation",
        "subcategory": "Groundwater Contamination",
        "people_affected": 3200,
        "state": "Jharkhand",
        "district": "Sahebganj",
        "block": "Rajmahal",
        "panchayat": "Kalyanpur",
        "village": "Ganga Nagar",
        "latitude": 25.048,
        "longitude": 87.839,
    }
    response = client.post("/api/challenges", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["submitted_by"] == test_user.id
    assert data["status"] == "submitted"
    assert data["category"] == "Water & Sanitation"
    assert data["subcategory"] == "Groundwater Contamination"
    assert data["people_affected"] == 3200
    assert data["location"] is not None
    assert data["location"]["state"] == "Jharkhand"
    assert data["location"]["district"] == "Sahebganj"
    assert data["location"]["block"] == "Rajmahal"
    assert data["location"]["panchayat"] == "Kalyanpur"
    assert data["location"]["village"] == "Ganga Nagar"
    assert data["location"]["latitude"] == 25.048
    assert data["location"]["longitude"] == 87.839


def test_create_challenge_non_jharkhand_rejected(client, test_user):
    payload = {
        "title": "Flooding in Patna",
        "description": "Urban flooding in monsoon season.",
        "submitted_by": test_user.id,
        "state": "Bihar",
        "district": "Patna",
    }
    response = client.post("/api/challenges", json=payload)
    assert response.status_code in [400, 422]


def test_create_challenge_state_normalization(client, test_user):
    for raw_state in ["jharkhand", "JHARKHAND", "  Jharkhand  "]:
        payload = {
            "title": f"Soil Erosion Issue ({raw_state.strip()})",
            "description": "Topsoil loss affecting agricultural yield in tribal farmland.",
            "submitted_by": test_user.id,
            "state": raw_state,
            "district": "Dumka",
        }
        response = client.post("/api/challenges", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["location"]["state"] == "Jharkhand"


def test_create_challenge_missing_required_fields(client):
    # Missing title, description, district, etc.
    response = client.post("/api/challenges", json={})
    assert response.status_code == 422


def test_create_challenge_invalid_user(client):
    payload = {
        "title": "Deforestation in Saranda",
        "description": "Illegal logging destroying Sal tree cover.",
        "submitted_by": 99999,  # Non-existent user
        "state": "Jharkhand",
        "district": "West Singhbhum",
    }
    response = client.post("/api/challenges", json=payload)
    assert response.status_code == 400
    assert "User with ID 99999 does not exist" in response.json()["detail"]


def test_create_challenge_invalid_coordinates_and_numbers(client, test_user):
    # Negative people_affected
    payload = {
        "title": "Illegal Mining",
        "description": "Unregulated quarrying in forest zone.",
        "submitted_by": test_user.id,
        "state": "Jharkhand",
        "district": "Dhanbad",
        "people_affected": -10,
    }
    response = client.post("/api/challenges", json=payload)
    assert response.status_code == 422

    # Invalid latitude
    payload["people_affected"] = 100
    payload["latitude"] = 120.0
    response = client.post("/api/challenges", json=payload)
    assert response.status_code == 422


def test_get_challenges_list_and_pagination(client, test_user):
    # Create 5 challenges
    for i in range(1, 6):
        client.post(
            "/api/challenges",
            json={
                "title": f"Challenge #{i}",
                "description": f"Description for challenge {i}",
                "submitted_by": test_user.id,
                "category": "Agriculture" if i % 2 == 0 else "Health",
                "state": "Jharkhand",
                "district": "Ranchi" if i <= 3 else "Hazaribagh",
            },
        )

    # Page 1 with page_size=2
    response = client.get("/api/challenges?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] >= 3

    # Page 2 with page_size=2
    response_p2 = client.get("/api/challenges?page=2&page_size=2")
    assert response_p2.status_code == 200
    data_p2 = response_p2.json()
    assert len(data_p2["items"]) == 2
    assert data_p2["items"][0]["id"] != data["items"][0]["id"]


def test_get_challenges_filters(client, test_user):
    # Create specific challenges
    client.post(
        "/api/challenges",
        json={
            "title": "Filtered Education Challenge",
            "description": "Lack of digital connectivity in schools.",
            "submitted_by": test_user.id,
            "category": "Education",
            "state": "Jharkhand",
            "district": "Simdega",
        },
    )
    client.post(
        "/api/challenges",
        json={
            "title": "Filtered Solar Challenge",
            "description": "Off-grid tribal hamlets needing solar mini-grids.",
            "submitted_by": test_user.id,
            "category": "Energy",
            "state": "Jharkhand",
            "district": "Gumla",
        },
    )

    # Filter by category
    res_cat = client.get("/api/challenges?category=Education")
    assert res_cat.status_code == 200
    data_cat = res_cat.json()
    assert any(c["title"] == "Filtered Education Challenge" for c in data_cat["items"])
    assert not any(c["title"] == "Filtered Solar Challenge" for c in data_cat["items"])

    # Filter by district
    res_dist = client.get("/api/challenges?district=gumla")
    assert res_dist.status_code == 200
    data_dist = res_dist.json()
    assert any(c["title"] == "Filtered Solar Challenge" for c in data_dist["items"])
    assert not any(c["title"] == "Filtered Education Challenge" for c in data_dist["items"])


def test_get_challenge_by_id_success(client, test_user):
    create_res = client.post(
        "/api/challenges",
        json={
            "title": "Fluoride in Drinking Water",
            "description": "High fluorosis rate in tribal blocks.",
            "submitted_by": test_user.id,
            "category": "Water & Sanitation",
            "state": "Jharkhand",
            "district": "Palamu",
            "block": "Daltonganj",
        },
    )
    challenge_id = create_res.json()["id"]

    response = client.get(f"/api/challenges/{challenge_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == challenge_id
    assert data["title"] == "Fluoride in Drinking Water"
    assert data["location"]["district"] == "Palamu"
    assert data["location"]["block"] == "Daltonganj"


def test_get_challenge_by_id_not_found(client):
    response = client.get("/api/challenges/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_patch_challenge_success(client, test_user):
    create_res = client.post(
        "/api/challenges",
        json={
            "title": "Initial Title",
            "description": "Initial description.",
            "submitted_by": test_user.id,
            "category": "General",
            "state": "Jharkhand",
            "district": "Bokaro",
            "village": "Old Village",
        },
    )
    challenge_id = create_res.json()["id"]

    patch_payload = {
        "title": "Updated Challenge Title",
        "description": "Updated detailed description.",
        "category": "Healthcare",
        "status": "under_review",
        "village": "New Verified Village",
        "people_affected": 500,
    }
    response = client.patch(f"/api/challenges/{challenge_id}", json=patch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == challenge_id
    assert data["title"] == "Updated Challenge Title"
    assert data["description"] == "Updated detailed description."
    assert data["category"] == "Healthcare"
    assert data["status"] == "under_review"
    assert data["people_affected"] == 500
    assert data["location"]["village"] == "New Verified Village"
    assert data["location"]["district"] == "Bokaro"
    assert data["submitted_by"] == test_user.id


def test_patch_challenge_invalid_state_and_status(client, test_user):
    create_res = client.post(
        "/api/challenges",
        json={
            "title": "Patch Validation Test",
            "description": "Testing validation rules.",
            "submitted_by": test_user.id,
            "state": "Jharkhand",
            "district": "Ranchi",
        },
    )
    challenge_id = create_res.json()["id"]

    # Try to change state to non-Jharkhand
    res_state = client.patch(f"/api/challenges/{challenge_id}", json={"state": "Odisha"})
    assert res_state.status_code in [400, 422]

    # Try invalid status
    res_status = client.patch(f"/api/challenges/{challenge_id}", json={"status": "invalid_status_xyz"})
    assert res_status.status_code == 422


def test_patch_challenge_not_found(client):
    response = client.patch("/api/challenges/999999", json={"title": "New Title"})
    assert response.status_code == 404
