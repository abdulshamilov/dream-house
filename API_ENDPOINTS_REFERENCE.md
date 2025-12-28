# 📚 API Endpoints Reference

## 🔐 Authentication Endpoints

### Register User
```
POST /api/users/register/
Content-Type: application/json

{
  "phone_number": "+79991234567",
  "password": "securepass123",
  "ref_code": "optional-referral-code"
}

Response (201):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 🏠 Card (Property) Endpoints

### 1. List Cards with Pagination
```
GET /api/cards/?limit=10&page=1
```
Parameters:
- `limit` (int): Page size, max 100. Default: 10
- `page` (int): Page number. Default: 1

### 2. Smart Search with History Tracking
```
GET /api/cards/search/?q=квартира%202%20комнаты&price_from=1000000&price_to=5000000&rooms=2&city=москва&rating_min=4.0
```

Query Parameters:
- `q` (string, required): Search term (searches title, description, address)
- `price_from` (float, optional): Minimum price
- `price_to` (float, optional): Maximum price
- `city` (string, optional): City filter
- `rooms` (int, optional): Number of rooms
- `building_material` (string, optional): Building material
- `rating_min` (float, optional): Minimum rating

Features:
- Auto-corrects typos and applies synonyms
- Saves search to user's history (if authenticated)
- Intelligent filtering based on query content
- Returns up to 20 most relevant results

### 3. Get Search History & Analytics
```
GET /api/cards/search-history/
Authorization: Bearer <token>
```

Response:
```json
{
  "total_searches": 15,
  "popular_queries": [
    {"query": "квартира москва", "count": 5},
    {"query": "2 комнаты", "count": 3}
  ],
  "recent_searches": [
    {"query": "квартира", "created_at": "2025-12-28T10:30:00Z"},
    {"query": "2 комнаты", "created_at": "2025-12-28T10:25:00Z"}
  ]
}
```

### 4. Clear Search History
```
DELETE /api/cards/search-history/
Authorization: Bearer <token>

Response (204): No Content
```

### 5. Get Recently Viewed Cards
```
GET /api/cards/recent-views/
Authorization: Bearer <token>
```
Returns last 3-4 recently viewed cards

### 6. Get Personalized Recommendations
```
GET /api/cards/recommendations/for-me/
Authorization: Bearer <token>
```
Returns 20 personalized recommendations based on:
- User's recently viewed cards
- User's card ratings

## ⭐ Review Endpoints

### 1. List Reviews for Card
```
GET /api/cards/{card_id}/reviews/
```

### 2. Create Review
```
POST /api/cards/{card_id}/reviews/
Authorization: Bearer <token>
Content-Type: application/json

{
  "rating": 5,
  "text": "Excellent property!"
}

Response:
{
  "id": 1,
  "user": {"id": 1, "phone_number": "+79991234567"},
  "card": 5,
  "rating": 5,
  "text": "Excellent property!",
  "likes_count": 0,
  "is_liked": false,
  "created_at": "2025-12-28T10:30:00Z"
}
```

### 3. Like a Review
```
PUT /api/cards/reviews/{review_id}/like/
Authorization: Bearer <token>

Response (200):
{
  "message": "Review liked successfully",
  "likes_count": 5
}
```

### 4. Unlike a Review
```
DELETE /api/cards/reviews/{review_id}/like/
Authorization: Bearer <token>

Response (204): No Content
```

Response returns updated likes_count

## 👤 User Account Endpoints

### 1. Update Profile (Change Photo)
```
PUT /api/users/update-profile/
Authorization: Bearer <token>
Content-Type: multipart/form-data

{
  "avatar": <file>,
  "first_name": "John",
  "last_name": "Doe"
}

Response:
{
  "id": 1,
  "phone_number": "+79991234567",
  "avatar": "https://...",
  "first_name": "John",
  "last_name": "Doe"
}
```

### 2. Change Password
```
POST /api/users/change-password/
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}

Response (200):
{
  "message": "Password changed successfully"
}
```

### 3. Delete Account
```
DELETE /api/users/delete-account/
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "your_password"
}

Response (204): No Content
```
Completely removes user account and all associated data

### 4. Get Referral Link
```
GET /api/users/referral/
Authorization: Bearer <token>

Response:
{
  "code": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "referred_count": 3,
  "link": "https://dream-house.com/ref/f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

## 💬 Chat (AI Assistant) Endpoints

### 1. Send Message (Chat with AI)
```
POST /api/cards/{card_id}/chat/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Tell me about this property"
}

Response:
{
  "id": 1,
  "role": "assistant",
  "message": "This beautiful property features...",
  "created_at": "2025-12-28T10:30:00Z"
}
```

### 2. Get Chat History
```
GET /api/cards/{card_id}/chat-history/
Authorization: Bearer <token>

Response:
[
  {"id": 1, "role": "user", "message": "Tell me more", "created_at": "..."},
  {"id": 2, "role": "assistant", "message": "This property...", "created_at": "..."}
]
```
Limit: Last 5 messages (for performance)

## 🔍 Filtering Examples

### Search with All Filters
```
GET /api/cards/search/?q=квартира&price_from=2000000&price_to=5000000&city=москва&rooms=2&building_material=кирпич&rating_min=4.0
```

### Smart Synonyms Supported
- "хорошие" → searches rating >= 4.0
- "дешевые" → price < 3,000,000
- "премиум" → price >= 5,000,000
- "дорогие" → price >= 5,000,000
- "новые" → created in 2025
- "спальни" → rooms filter

## 📊 Response Pagination Format

```json
{
  "count": 45,
  "next": "http://api.example.com/cards/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Apartment",
      "price": 3000000,
      "price_metr": 150000.50,
      "area": 20.0,
      "rooms": 2,
      "city": "Moscow",
      "rating": 4.5
    }
  ]
}
```

## ✅ 11 Implemented Features

1. ✅ **Photo Change** - PUT /api/users/update-profile/ with avatar
2. ✅ **Account Deletion** - DELETE /api/users/delete-account/
3. ✅ **Password Change** - POST /api/users/change-password/
4. ✅ **Chat History Limit** - Last 5 messages per property
5. ✅ **Personalized Recommendations** - GET /api/cards/recommendations/for-me/
6. ✅ **Referral Links** - GET /api/users/referral/
7. ✅ **Address in Curations** - Added to recommendation serializers
8. ✅ **Recently Viewed Cards** - GET /api/cards/recent-views/
9. ✅ **Pagination** - limit & page parameters
10. ✅ **Price Per Meter** - price_metr field in card responses
11. ✅ **Review Likes** - PUT/DELETE /api/cards/reviews/{id}/like/

## 🎯 Intelligent Search Features

- **Multi-field search**: title, description, address
- **Auto-correction**: Typo detection and fixes
- **Synonyms**: Russian synonyms for common queries
- **Smart filters**: Price ranges, location, ratings
- **Number recognition**: Automatic room/price detection
- **History tracking**: Saves all searches for analytics
- **Popular queries**: Shows user's most frequent searches
- **User history based sorting**: Personalizes results
