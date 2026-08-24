import pytest
from models.user import User
from config.database import db

def test_successful_user_registration(client):
    payload = {
        "name": "Jane Customer",
        "email": "jane@example.com",
        "password": "Password123!",
        "phone": "1234567890",
        "role": "CUSTOMER"
    }
    res = client.post("/api/register", json=payload)
    assert res.status_code == 201
    assert "User Registration Successful" in res.json["message"]
    assert res.json["user"]["email"] == "jane@example.com"
    assert res.json["user"]["role"] == "CUSTOMER"

def test_manager_registration(client):
    payload = {
        "name": "Mark Manager",
        "email": "manager@example.com",
        "password": "Password123!",
        "role": "EVENT_MANAGER"
    }
    res = client.post("/api/register", json=payload)
    assert res.status_code == 201
    assert res.json["user"]["role"] == "EVENT_MANAGER"

def test_registration_validation_missing_fields(client):
    payload = {
        "email": "incomplete@example.com",
        "password": "Password123!"
    }
    res = client.post("/api/register", json=payload)
    assert res.status_code == 400
    assert "Name, email, password are required" in res.json["message"]

def test_duplicate_email_registration(client):
    payload = {
        "name": "First User",
        "email": "duplicate@example.com",
        "password": "Password123!",
        "role": "CUSTOMER"
    }
    client.post("/api/register", json=payload)

    res = client.post("/api/register", json=payload)
    assert res.status_code == 400
    assert "Email already registered" in res.json["message"]

def test_invalid_role_registration(client):
    payload = {
        "name": "Hacker User",
        "email": "hacker@example.com",
        "password": "Password123!",
        "role": "ADMIN"
    }
    res = client.post("/api/register", json=payload)
    assert res.status_code == 400
    assert "Invalid Role" in res.json["message"]

def test_successful_login(client):
    reg_payload = {
        "name": "Login User",
        "email": "login@example.com",
        "password": "SecurePassword123",
        "role": "CUSTOMER"
    }
    client.post("/api/register", json=reg_payload)

    login_payload = {
        "email": "login@example.com",
        "password": "SecurePassword123"
    }
    res = client.post("/api/login", json=login_payload)
    assert res.status_code == 200
    assert "access_token" in res.json
    assert "Login successful" in res.json["message"]

def test_login_non_existent_email(client):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "Password123!"
    }
    res = client.post("/api/login", json=login_payload)
    assert res.status_code == 401
    assert "Invalid email or password" in res.json["message"]

def test_login_wrong_password(client):
    reg_payload = {
        "name": "User WrongPass",
        "email": "wrongpass@example.com",
        "password": "RightPassword123",
        "role": "CUSTOMER"
    }
    client.post("/api/register", json=reg_payload)

    login_payload = {
        "email": "wrongpass@example.com",
        "password": "WrongPassword123"
    }
    res = client.post("/api/login", json=login_payload)
    assert res.status_code == 401
    assert "Invalid email or password" in res.json["message"]

def test_login_deactivated_account(app, client):
    reg_payload = {
        "name": "Deactivated User",
        "email": "deactivated@example.com",
        "password": "Password123!",
        "role": "CUSTOMER"
    }
    res_reg = client.post("/api/register", json=reg_payload)
    user_id = res_reg.json["user"]["id"]

    with app.app_context():
        user = User.query.get(user_id)
        user.is_active = False
        db.session.commit()

    login_payload = {
        "email": "deactivated@example.com",
        "password": "Password123!"
    }
    res = client.post("/api/login", json=login_payload)
    assert res.status_code == 401
    assert "Account is deactivated" in res.json["message"]

def test_update_user_profile_api(client):
    reg_payload = {
        "name": "Update User",
        "email": "update_me@example.com",
        "password": "Password123!",
        "role": "CUSTOMER"
    }
    client.post("/api/register", json=reg_payload)

    login_res = client.post("/api/login", json={"email": "update_me@example.com", "password": "Password123!"})
    token = login_res.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "name": "Updated Name",
        "phone": "9998887776"
    }
    res = client.put("/api/me", json=update_payload, headers=headers)
    assert res.status_code == 200
    assert res.json["message"] == "Profile updated successfully"
    assert res.json["user"]["name"] == "Updated Name"
    assert res.json["user"]["phone"] == "9998887776"

def test_update_profile_duplicate_email(client):
    client.post("/api/register", json={"name": "User One", "email": "user1@example.com", "password": "Password123!", "role": "CUSTOMER"})
    client.post("/api/register", json={"name": "User Two", "email": "user2@example.com", "password": "Password123!", "role": "CUSTOMER"})

    login_res = client.post("/api/login", json={"email": "user2@example.com", "password": "Password123!"})
    token = login_res.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.put("/api/me", json={"email": "user1@example.com"}, headers=headers)
    assert res.status_code == 400
    assert "Email is already in use" in res.json["message"]

def test_registration_invalid_email_format(client):
    payload = {
        "name": "Invalid Email User",
        "email": "invalid-email-string",
        "password": "Password123!",
        "role": "CUSTOMER"
    }
    res = client.post("/api/register", json=payload)
    assert res.status_code == 400
    assert "Invalid email format" in res.json["message"]

def test_registration_invalid_phone_number_length(client):
    # Test short phone number (< 10 digits)
    payload_short = {
        "name": "Short Phone User",
        "email": "shortphone@example.com",
        "password": "Password123!",
        "phone": "12345",
        "role": "CUSTOMER"
    }
    res_short = client.post("/api/register", json=payload_short)
    assert res_short.status_code == 400
    assert "Phone number must be exactly 10 digits" in res_short.json["message"]

    # Test long phone number (> 10 digits)
    payload_long = {
        "name": "Long Phone User",
        "email": "longphone@example.com",
        "password": "Password123!",
        "phone": "123456789012",
        "role": "CUSTOMER"
    }
    res_long = client.post("/api/register", json=payload_long)
    assert res_long.status_code == 400
    assert "Phone number must be exactly 10 digits" in res_long.json["message"]

    # Test non-digit phone number
    payload_alpha = {
        "name": "Alpha Phone User",
        "email": "alphaphone@example.com",
        "password": "Password123!",
        "phone": "abcdefghij",
        "role": "CUSTOMER"
    }
    res_alpha = client.post("/api/register", json=payload_alpha)
    assert res_alpha.status_code == 400
    assert "Phone number must be exactly 10 digits" in res_alpha.json["message"]

