"""
Test Authentication API - Milestone 5
Tests for JWT authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"\n=== Health Check ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_register():
    """Test user registration"""
    print(f"\n=== Test Register ===")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"username": "test_user", "password": "test123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code in [201, 400]  # 400 if already exists


def test_login():
    """Test login and get JWT token"""
    print(f"\n=== Test Login ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "demo_user", "password": "demo123"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    if response.status_code == 200:
        return data.get("access_token")
    return None


def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token"""
    print(f"\n=== Test Protected Endpoint (No Token) ===")
    response = requests.get(f"{BASE_URL}/profile/user_001")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 401  # Should be unauthorized


def test_protected_endpoint_with_token(token: str):
    """Test accessing protected endpoint with valid token"""
    print(f"\n=== Test Protected Endpoint (With Token) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create profile
    response = requests.post(
        f"{BASE_URL}/profile/user_001",
        headers=headers
    )
    print(f"Create Profile Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Then get profile
    response = requests.get(
        f"{BASE_URL}/profile/user_001",
        headers=headers
    )
    print(f"Get Profile Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code in [200, 400]


def test_authorization(token: str):
    """Test that users can only access their own profile"""
    print(f"\n=== Test Authorization (Access Other User's Profile) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access another user's profile (should fail with 403)
    response = requests.get(
        f"{BASE_URL}/profile/user_999",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 403  # Should be forbidden


def test_add_genre_with_auth(token: str):
    """Test adding genre with authentication"""
    print(f"\n=== Test Add Genre (With Auth) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/profile/user_001/genre",
        headers=headers,
        json={"genre": "Fiction"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_get_current_user(token: str):
    """Test /auth/me endpoint"""
    print(f"\n=== Test Get Current User ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def run_all_tests():
    """Run all authentication tests"""
    print("=" * 60)
    print("BC-3 Personalization API - JWT Authentication Tests")
    print("Milestone 5: Implementasi Lanjutan")
    print("=" * 60)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    # Test registration
    results.append(("Registration", test_register()))
    
    # Test login
    token = test_login()
    results.append(("Login", token is not None))
    
    if token:
        # Test protected endpoint without token
        results.append(("Protected (No Token)", test_protected_endpoint_without_token()))
        
        # Test protected endpoint with token
        results.append(("Protected (With Token)", test_protected_endpoint_with_token(token)))
        
        # Test authorization
        results.append(("Authorization", test_authorization(token)))
        
        # Test add genre
        results.append(("Add Genre", test_add_genre_with_auth(token)))
        
        # Test get current user
        results.append(("Get Current User", test_get_current_user(token)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
