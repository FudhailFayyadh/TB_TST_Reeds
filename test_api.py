"""
Simple test script to verify the implementation
Run this after starting the server with: uvicorn main:app --reload
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    print(f"{'='*60}\n")

def main():
    """Test the Personalization Context API"""
    
    user_id = "user-001"
    
    # 1. Create Profile
    print("\n🚀 Starting API Tests...\n")
    response = requests.post(f"{BASE_URL}/profile/{user_id}")
    print_response(response, "1. CREATE PROFILE")
    
    # 2. Add Genre Favorit (Test 1)
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/genre",
        json={"genre": "Fantasy"}
    )
    print_response(response, "2. ADD GENRE: Fantasy")
    
    # 3. Add Genre Favorit (Test 2)
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/genre",
        json={"genre": "Science Fiction"}
    )
    print_response(response, "3. ADD GENRE: Science Fiction")
    
    # 4. Add Rating (Test 1)
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/rating",
        json={"book_id": "book-101", "rating": 5}
    )
    print_response(response, "4. ADD RATING: book-101 → 5 stars")
    
    # 5. Add Rating (Test 2)
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/rating",
        json={"book_id": "book-102", "rating": 4}
    )
    print_response(response, "5. ADD RATING: book-102 → 4 stars")
    
    # 6. Add Rating (Test 3)
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/rating",
        json={"book_id": "book-103", "rating": 3}
    )
    print_response(response, "6. ADD RATING: book-103 → 3 stars")
    
    # 7. Block Item
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/block",
        json={"book_id": "book-999"}
    )
    print_response(response, "7. BLOCK ITEM: book-999")
    
    # 8. Get Profile
    response = requests.get(f"{BASE_URL}/profile/{user_id}")
    print_response(response, "8. GET PROFILE")
    
    # 9. Get Snapshot (Read Model)
    response = requests.get(f"{BASE_URL}/profile/{user_id}/snapshot")
    print_response(response, "9. GET SNAPSHOT (Read Model)")
    
    # 10. Test Invariant: Maximum 5 genres
    print("\n🔒 Testing Invariant: Maximum 5 Favorite Genres")
    genres = ["Romance", "Mystery", "Thriller", "Horror"]
    for genre in genres:
        response = requests.post(
            f"{BASE_URL}/profile/{user_id}/genre",
            json={"genre": genre}
        )
        print(f"  Adding '{genre}': Status {response.status_code}")
    
    # This should fail (6th genre)
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/genre",
        json={"genre": "Biography"}
    )
    print(f"  Adding 'Biography' (6th): Status {response.status_code} ❌ (Expected to fail)")
    if response.status_code == 400:
        print(f"  ✅ Invariant enforced: {response.json()['detail']}")
    
    # 11. Test Invariant: Cannot block active book
    print("\n🔒 Testing Invariant: Cannot Block Active Book")
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/block",
        json={"book_id": "book-101"}  # This book has a rating
    )
    print(f"  Blocking book-101 (has rating): Status {response.status_code} ❌ (Expected to fail)")
    if response.status_code == 400:
        print(f"  ✅ Invariant enforced: {response.json()['detail']}")
    
    # 12. Test Invariant: Rating must be 1-5
    print("\n🔒 Testing Invariant: Rating Must Be 1-5")
    response = requests.post(
        f"{BASE_URL}/profile/{user_id}/rating",
        json={"book_id": "book-200", "rating": 6}
    )
    print(f"  Rating 6: Status {response.status_code} ❌ (Expected to fail)")
    if response.status_code == 422:
        print(f"  ✅ Invariant enforced: Invalid rating value")
    
    print("\n✅ All tests completed!")
    print("\n📊 Final Snapshot:")
    response = requests.get(f"{BASE_URL}/profile/{user_id}/snapshot")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print("Please make sure the server is running:")
        print("  uvicorn main:app --reload")
        print("\nThen run this script again.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
