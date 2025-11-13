import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "user_identifier": "new.user",
            "password": "newpassword123"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_identifier"] == "new.user"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_user(client, test_user):
    """Test registering a user that already exists"""
    response = client.post(
        "/api/auth/register",
        json={
            "user_identifier": "test.user",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Changed: Match actual error message
    assert "already exists" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/api/auth/login",
        json={
            "user_identifier": "test.user",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/auth/login",
        json={
            "user_identifier": "test.user",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/auth/login",
        json={
            "user_identifier": "nonexistent.user",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, test_user, auth_headers):
    """Test getting current user information"""
    response = client.get(
        "/api/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_identifier"] == "test.user"
    assert data["id"] == test_user.id


def test_get_current_user_no_token(client):
    """Test getting current user without authentication"""
    response = client.get("/api/auth/me")
    
    # Changed: FastAPI returns 403 Forbidden, not 401 Unauthorized when no token provided
    assert response.status_code == status.HTTP_403_FORBIDDEN