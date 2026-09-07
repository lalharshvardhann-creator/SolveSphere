def test_create_institution_success(client):
    payload = {
        "name": "Indian Institute of Technology (ISM) Dhanbad",
        "institution_type": "National Institute of Importance",
        "district": "Dhanbad",
        "address": "Sardar Patel Nagar, Dhanbad, Jharkhand 826004",
        "latitude": 23.814,
        "longitude": 86.441,
        "website": "https://www.iitism.ac.in",
        "description": "Premier mining, engineering and earth sciences institute.",
    }
    response = client.post("/api/institutions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["institution_type"] == payload["institution_type"]
    assert data["district"] == "Dhanbad"
    assert data["verification_status"] == "pending"
    assert data["latitude"] == 23.814
    assert data["longitude"] == 86.441
    assert data["website"] == "https://www.iitism.ac.in"


def test_create_institution_missing_required_fields(client):
    # Missing name, institution_type, district
    response = client.post("/api/institutions", json={"address": "Just an address"})
    assert response.status_code == 422


def test_get_institutions_list_and_pagination(client):
    for i in range(1, 6):
        client.post(
            "/api/institutions",
            json={
                "name": f"College of Technology #{i}",
                "institution_type": "Polytechnic" if i % 2 == 0 else "Engineering",
                "district": "Ranchi" if i <= 3 else "Jamshedpur",
            },
        )

    response = client.get("/api/institutions?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] >= 3


def test_get_institutions_filters(client):
    client.post(
        "/api/institutions",
        json={
            "name": "Birsa Agricultural University",
            "institution_type": "Agriculture",
            "district": "Ranchi",
        },
    )
    client.post(
        "/api/institutions",
        json={
            "name": "National Institute of Technology Jamshedpur",
            "institution_type": "Engineering",
            "district": "East Singhbhum",
        },
    )

    # Filter by district
    res_dist = client.get("/api/institutions?district=ranchi")
    assert res_dist.status_code == 200
    data_dist = res_dist.json()
    assert any(inst["name"] == "Birsa Agricultural University" for inst in data_dist["items"])

    # Filter by type
    res_type = client.get("/api/institutions?institution_type=Engineering")
    assert res_type.status_code == 200
    data_type = res_type.json()
    assert any(inst["name"] == "National Institute of Technology Jamshedpur" for inst in data_type["items"])


def test_get_institution_by_id_with_expertise(client):
    inst_res = client.post(
        "/api/institutions",
        json={
            "name": "Ranchi University",
            "institution_type": "State University",
            "district": "Ranchi",
            "website": "https://www.ranchiuniversity.ac.in",
        },
    )
    inst_id = inst_res.json()["id"]

    # Add expertise
    client.post(
        f"/api/institutions/{inst_id}/expertise",
        json={
            "domain": "Tribal Studies & Ethnobotany",
            "subdomain": "Medicinal Plants of Jharkhand",
            "keywords": "ayurveda, ethnobotany, tribal knowledge systems",
            "expertise_level": "Expert",
            "facilities": "Herbarium & Bio-analytical Lab",
            "research_areas": "Traditional medicine documentation and active compound analysis",
        },
    )

    # Fetch detail
    response = client.get(f"/api/institutions/{inst_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == inst_id
    assert data["name"] == "Ranchi University"
    assert len(data["expertise_entries"]) == 1
    assert data["expertise_entries"][0]["domain"] == "Tribal Studies & Ethnobotany"
    assert data["expertise_entries"][0]["expertise_level"] == "Expert"


def test_get_institution_by_id_not_found(client):
    response = client.get("/api/institutions/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_create_institution_expertise_success(client):
    inst_res = client.post(
        "/api/institutions",
        json={
            "name": "Xavier Institute of Social Service (XISS)",
            "institution_type": "Management & Social Work",
            "district": "Ranchi",
        },
    )
    inst_id = inst_res.json()["id"]

    payload = {
        "domain": "Rural Development",
        "subdomain": "Livelihoods & SHG Strengthening",
        "keywords": "microfinance, SHG, rural entrepreneurship",
        "expertise_level": "advanced",  # Should normalize to "Advanced"
        "facilities": "Field research stations across 5 districts",
        "research_areas": "Tribal Women Empowerment and Micro-enterprises",
    }
    response = client.post(f"/api/institutions/{inst_id}/expertise", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["institution_id"] == inst_id
    assert data["domain"] == "Rural Development"
    assert data["expertise_level"] == "Advanced"


def test_create_institution_expertise_invalid_level(client):
    inst_res = client.post(
        "/api/institutions",
        json={
            "name": "Sample College",
            "institution_type": "Degree College",
            "district": "Bokaro",
        },
    )
    inst_id = inst_res.json()["id"]

    payload = {
        "domain": "Biotechnology",
        "expertise_level": "SuperEliteNinjaLevel",  # Invalid
    }
    response = client.post(f"/api/institutions/{inst_id}/expertise", json=payload)
    assert response.status_code == 422


def test_create_institution_expertise_institution_not_found(client):
    payload = {
        "domain": "Renewable Energy",
        "expertise_level": "Intermediate",
    }
    response = client.post("/api/institutions/999999/expertise", json=payload)
    assert response.status_code == 404


def test_get_institution_expertise_list(client):
    inst_res = client.post(
        "/api/institutions",
        json={
            "name": "AIIMS Deoghar",
            "institution_type": "Medical Institute",
            "district": "Deoghar",
        },
    )
    inst_id = inst_res.json()["id"]

    # Add 2 expertise domains
    client.post(
        f"/api/institutions/{inst_id}/expertise",
        json={"domain": "Public Health & Epidemiology", "expertise_level": "Expert"},
    )
    client.post(
        f"/api/institutions/{inst_id}/expertise",
        json={"domain": "Telemedicine & Rural Health Delivery", "expertise_level": "Advanced"},
    )

    response = client.get(f"/api/institutions/{inst_id}/expertise")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    domains = [exp["domain"] for exp in data]
    assert "Public Health & Epidemiology" in domains
    assert "Telemedicine & Rural Health Delivery" in domains


def test_get_institution_expertise_list_not_found(client):
    response = client.get("/api/institutions/999999/expertise")
    assert response.status_code == 404
