import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal

# Create a TestClient instance correctly
client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    """Fixture to create a new database session for each test"""
    Base.metadata.drop_all(bind=engine)  # Clear database
    Base.metadata.create_all(bind=engine)  # Recreate tables
    db = SessionLocal()
    yield db
    db.close()

def test_homepage():
    """Test if the root URL returns a valid response"""
    response = client.get("/")
    assert response.status_code == 200
    assert "URL Shortener" in response.text  # Adjust this based on actual response

def test_shorten_url():
    """Test URL shortening functionality"""
    response = client.post("/shorten", json={"url": "http://127.0.0.1:8000/static/index.html"})
    assert response.status_code == 200
    assert "short_url" in response.json()

# def test_redirect():
#     """Test redirection from a short URL to the original URL"""
#     shorten_response = client.post("/shorten", json={"url": "https://example.com"})
#     short_url = shorten_response.json()["short_url"].split("/")[-1]

#     redirect_response = client.get(f"/{short_url}", follow_redirects=False)
#     assert redirect_response.status_code == 307  # Ensure it's a redirect
#     assert redirect_response.headers["location"] == "https://example.com"

# def test_invalid_redirect():
#     """Test redirection for a non-existent short URL"""
#     response = client.get("/invalid123")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "URL not found"
