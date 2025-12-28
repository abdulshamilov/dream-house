# 🧪 Testing Guide for All Endpoints

## Prerequisites

```bash
# 1. Create superuser for testing
python manage.py createsuperuser --phone_number=+79991111111

# 2. Run migrations if needed
python manage.py migrate

# 3. Load sample data (if available)
python manage.py loaddata sample_cards.json

# 4. Start server
python manage.py runserver
```

## Test Scenarios

### 1️⃣ Authentication Tests

#### Register New User
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+79991234567",
    "password": "testpass123"
  }'

# Expected: 201 Created with access & refresh tokens
```

#### Register with Referral Code
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+79999999999",
    "password": "testpass456",
    "ref_code": "YOUR_CODE_HERE"
  }'
```

---

### 2️⃣ Card Search Tests

#### Basic Search
```bash
curl http://localhost:8000/api/cards/search/?q=квартира
```

#### Search with Price Range
```bash
curl "http://localhost:8000/api/cards/search/?q=квартира&price_from=1000000&price_to=5000000"
```

#### Search with Multiple Filters
```bash
curl "http://localhost:8000/api/cards/search/?q=квартира&city=москва&rooms=2&rating_min=4.0"
```

#### Search - Smart Synonyms Test
```bash
# Search for "cheap" apartments
curl "http://localhost:8000/api/cards/search/?q=дешевые%20квартиры"
# Should return: price < 3,000,000

# Search for "premium"
curl "http://localhost:8000/api/cards/search/?q=премиум%20жилье"
# Should return: price >= 5,000,000 AND rating >= 4.0
```

---

### 3️⃣ Search History Tests

#### Get Search History (Authenticated)
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/cards/search-history/

# Expected response:
# {
#   "total_searches": 5,
#   "popular_queries": [...],
#   "recent_searches": [...]
# }
```

#### Clear Search History
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/cards/search-history/

# Expected: 204 No Content
```

#### Verify History Cleared
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/cards/search-history/

# Should return: total_searches: 0
```

---

### 4️⃣ Recently Viewed Cards Test

```bash
# First - View several cards (by visiting them)
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 30}' \
  http://localhost:8000/api/cards/1/view-history/

# Then - Get recently viewed
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/cards/recent-views/

# Expected: 3-4 most recently viewed cards
```

---

### 5️⃣ Personalized Recommendations Test

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/cards/recommendations/for-me/

# Expected: 20 cards based on:
# - Recently viewed cards
# - User's ratings (likes similar properties)
```

---

### 6️⃣ Review & Like Tests

#### Create Review
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "text": "Отличная квартира! Очень доволен покупкой."
  }' \
  http://localhost:8000/api/cards/1/reviews/

# Response should include:
# {
#   "id": 1,
#   "likes_count": 0,
#   "is_liked": false
# }
```

#### Like a Review
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/cards/reviews/1/like/

# Expected: 200 OK
# Response: {"message": "Review liked successfully", "likes_count": 1}
```

#### Unlike a Review
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/cards/reviews/1/like/

# Expected: 204 No Content
```

#### Get Reviews with Like Info
```bash
curl http://localhost:8000/api/cards/1/reviews/

# Each review should show:
# {
#   "likes_count": 2,
#   "is_liked": true/false  (if authenticated)
# }
```

---

### 7️⃣ User Account Tests

#### Update Profile (Photo)
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "avatar=@/path/to/photo.jpg" \
  -F "first_name=John" \
  -F "last_name=Doe" \
  http://localhost:8000/api/users/update-profile/

# Expected: 200 OK with updated user data
```

#### Change Password
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "testpass123",
    "new_password": "newpass456"
  }' \
  http://localhost:8000/api/users/change-password/

# Expected: 200 OK
```

#### Get Referral Info
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/users/referral/

# Response:
# {
#   "code": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
#   "referred_count": 2,
#   "link": "https://dream-house.com/ref/..."
# }
```

#### Delete Account
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "testpass456"}' \
  http://localhost:8000/api/users/delete-account/

# Expected: 204 No Content
# Verify: User should be deleted from database
```

---

### 8️⃣ Pagination Tests

#### Test Limit Parameter
```bash
# Get first 5 cards
curl "http://localhost:8000/api/cards/?limit=5&page=1"

# Get first 20 cards
curl "http://localhost:8000/api/cards/?limit=20&page=1"

# Get second page with 10 cards per page
curl "http://localhost:8000/api/cards/?limit=10&page=2"
```

#### Max Limit Test
```bash
# Try to exceed max (100)
curl "http://localhost:8000/api/cards/?limit=150&page=1"
# Should cap at 100
```

---

### 9️⃣ Price Per Meter (price_metr) Test

```bash
curl "http://localhost:8000/api/cards/1/"

# Response should include:
# {
#   "price": 5000000,
#   "area": 100.0,
#   "price_metr": 50000.00  (calculated as price/area)
# }
```

---

### 🔟 Chat History Limit Test

```bash
# Send 10 messages
for i in {1..10}; do
  curl -X POST \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test message $i\"}" \
    http://localhost:8000/api/cards/1/chat/
done

# Get chat history
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/cards/1/chat-history/

# Expected: Only last 5 messages returned
```

---

## Automated Test Suite (Python)

Save as `test_all_endpoints.py`:

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

class TestSuite:
    def __init__(self):
        self.token = None
        self.user_phone = f"+7999{int(datetime.now().timestamp() % 1000000):07d}"
        
    def register_user(self):
        """Test: User Registration"""
        print("Testing: User Registration...")
        response = requests.post(
            f"{BASE_URL}/users/register/",
            json={
                "phone_number": self.user_phone,
                "password": "testpass123"
            }
        )
        if response.status_code == 201:
            self.token = response.json()['access']
            print("✅ Registration passed")
            return True
        print(f"❌ Registration failed: {response.text}")
        return False
    
    def test_search(self):
        """Test: Smart Search"""
        print("Testing: Smart Search...")
        response = requests.get(
            f"{BASE_URL}/cards/search/?q=квартира&price_from=1000000&price_to=5000000"
        )
        if response.status_code == 200:
            data = response.json()
            if 'results' in data or isinstance(data, list):
                print("✅ Search passed")
                return True
        print(f"❌ Search failed: {response.text}")
        return False
    
    def test_search_history(self):
        """Test: Search History"""
        if not self.token:
            print("⚠️  Skipping - No auth token")
            return False
            
        print("Testing: Search History...")
        
        # Do some searches first
        requests.get(f"{BASE_URL}/cards/search/?q=квартира")
        requests.get(f"{BASE_URL}/cards/search/?q=дом")
        
        response = requests.get(
            f"{BASE_URL}/cards/search-history/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'total_searches' in data and 'recent_searches' in data:
                print("✅ Search history passed")
                return True
        print(f"❌ Search history failed: {response.text}")
        return False
    
    def test_delete_search_history(self):
        """Test: Delete Search History"""
        if not self.token:
            return False
            
        print("Testing: Delete Search History...")
        response = requests.delete(
            f"{BASE_URL}/cards/search-history/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 204:
            print("✅ Delete search history passed")
            return True
        print(f"❌ Delete search history failed: {response.status_code}")
        return False
    
    def run_all(self):
        """Run all tests"""
        print("=" * 50)
        print("🧪 Dream House API Test Suite")
        print("=" * 50 + "\n")
        
        results = {
            "Registration": self.register_user(),
            "Search": self.test_search(),
            "Search History": self.test_search_history(),
            "Delete Search History": self.test_delete_search_history(),
        }
        
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print("=" * 50)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{name}: {status}")
        
        print(f"\nTotal: {passed}/{total} passed")
        print("=" * 50)

if __name__ == "__main__":
    suite = TestSuite()
    suite.run_all()
```

Run tests:
```bash
python test_all_endpoints.py
```

---

## Troubleshooting

### Issue: 401 Unauthorized
**Solution**: Ensure token is valid and not expired. Get new token:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+79991234567", "password": "testpass123"}'
```

### Issue: 404 Not Found
**Solution**: Check URLs match the routing configuration in urls.py

### Issue: CORS Errors
**Solution**: Add domain to CORS_ALLOWED_ORIGINS in settings.py

### Issue: Empty Results
**Solution**: Ensure test data exists in database. Load sample data or create manually via admin panel.

---

## Performance Checklist

- [ ] Search returns results < 500ms
- [ ] Pagination works with limit=100 max
- [ ] Chat history limited to 5 messages
- [ ] Search history shows up to 30 days
- [ ] Recommendations return 20 items
- [ ] No N+1 queries (check Django Debug Toolbar)
- [ ] All endpoints properly authenticated

---

## Database Checks

```bash
# Check search history entries
python manage.py shell
>>> from cards.models import SearchHistory
>>> SearchHistory.objects.all().count()  # Should grow with searches

# Check review likes
>>> from cards.models import ReviewLike
>>> ReviewLike.objects.all().count()  # Should grow with likes

# Check view history
>>> from cards.models import ViewHistory  
>>> ViewHistory.objects.filter(user__phone_number="+79991234567").count()

# Check referrals
>>> from users.models import Referral
>>> Referral.objects.filter(referrer__phone_number="+79991234567").count()
```
