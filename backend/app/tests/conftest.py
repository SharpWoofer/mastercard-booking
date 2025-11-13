import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.db import Base, get_db
from app.main import app
from app.models.models import User
from app.services.auth_service import AuthService

# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(test_db):
    """Create a test user"""
    user = User(
        user_identifier="test.user",
        hashed_password=AuthService.get_password_hash("testpassword123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_user_token(client, test_user):
    """Get authentication token for test user"""
    response = client.post(
        "/api/auth/login",
        json={
            "user_identifier": "test.user",
            "password": "testpassword123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def auth_headers(test_user_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {test_user_token}"}