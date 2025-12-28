# 📋 Code Style & Refactoring Guidelines

## ✅ Completed Refactoring

### 1. Imports Organized
All imports now follow this pattern:

```python
# Layer 1: Standard Library
import uuid
from datetime import timedelta

# Layer 2: Django
from django.contrib.auth import get_user_model
from django.db.models import Q, Count

# Layer 3: DRF
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken

# Layer 4: Third-party
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

# Layer 5: Local
from .models import Card, CardReview
from .serializers import CardSerializer
```

**Status**: ✅ Applied to:
- `cards/views.py`
- `cards/serializers.py`
- `users/views.py`
- `users/serializers.py`

### 2. View Naming Convention

```python
# Pattern: [Entity][Action]View

# Examples:
CardListView              # List all cards
CardDetailView            # Get single card
CardSearchView            # Search functionality
CardReviewListView        # Reviews for a card
ReviewLikeView            # Like/unlike reviews
SearchHistoryView         # Search history
PersonalRecommendationsView  # Recommendations
```

**Status**: ✅ All views follow this pattern

### 3. Serializer Naming Convention

```python
# Pattern: [Entity]Serializer

# Examples:
CardSerializer
CardReviewSerializer
CardQuestionSerializer
SearchHistorySerializer
```

**Status**: ✅ All serializers follow this pattern

### 4. Model Fields Organization

```python
class Card(models.Model):
    # 1. Core fields (user, title, description)
    owner = models.ForeignKey(User, ...)
    title = models.CharField(...)
    description = models.TextField(...)
    
    # 2. Relationships (ForeignKey, ManyToMany)
    developer = models.ForeignKey(Developer, ...)
    
    # 3. Metadata (created_at, updated_at)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
```

**Status**: ✅ Models properly organized

### 5. Documentation Comments

All new features have docstring headers:

```python
@extend_schema(
    summary="Brief description in Russian",
    description="Full description with parameters and behavior"
)
class CardSearchView(generics.ListAPIView):
    """
    Search cards by text with intelligent filtering.
    
    Features:
    - Auto-correction of typos
    - Synonym replacement
    - Smart filtering by query content
    - Search history tracking
    - Maximum 20 results per request
    """
```

**Status**: ✅ All endpoints documented

## 📊 11 Features Implementation Summary

| # | Feature | Endpoint | Status | File |
|---|---------|----------|--------|------|
| 1 | Photo Change | PUT /api/users/update-profile/ | ✅ | users/views.py |
| 2 | Account Deletion | DELETE /api/users/delete-account/ | ✅ | users/views.py |
| 3 | Password Change | POST /api/users/change-password/ | ✅ | users/views.py |
| 4 | Chat Limit to 5 | GET /api/cards/{id}/chat-history/ | ✅ | cards/views_ai.py |
| 5 | Personalized Recommendations | GET /api/cards/recommendations/for-me/ | ✅ | cards/views.py |
| 6 | Referral Links | GET /api/users/referral/ | ✅ | users/views.py |
| 7 | Address in Curations | CardCurationSerializer | ✅ | cards/serializers.py |
| 8 | Recently Viewed Cards | GET /api/cards/recent-views/ | ✅ | cards/views.py |
| 9 | Pagination (limit/page) | All list endpoints | ✅ | cards/pagination.py |
| 10 | Price Per Meter (price_metr) | Card.price_metr property | ✅ | cards/models.py |
| 11 | Review Likes System | PUT/DELETE /api/cards/reviews/{id}/like/ | ✅ | cards/views.py |

## 🔍 Code Quality Checklist

### Documentation
- [x] All endpoints have @extend_schema decorators
- [x] All classes have docstrings
- [x] All complex methods have inline comments
- [x] API endpoints documented in API_ENDPOINTS_REFERENCE.md
- [x] Testing guide provided in TESTING_GUIDE.md

### Imports
- [x] Imports organized by layer (std lib → Django → DRF → third-party → local)
- [x] No circular imports
- [x] Unused imports removed
- [x] Consistent import ordering

### Error Handling
- [x] All views catch DoesNotExist and return 404
- [x] All serializers validate input data
- [x] Proper HTTP status codes used
- [x] User-friendly error messages in Russian

### Security
- [x] Authentication required for sensitive endpoints (like delete account)
- [x] Authorization checks in place (IsAuthenticated, IsAdminOrReadOnly)
- [x] Password hashed using Django's set_password()
- [x] CSRF protection enabled
- [x] Unique constraints on sensitive data (ReviewLike unique_together)

### Performance
- [x] Search results capped at 20
- [x] Chat history limited to 5 messages
- [x] Search history limited to 30 days
- [x] Pagination with configurable limit (max 100)
- [x] Recommendations limited to 20 items
- [x] Database queries optimized with select_related()

### API Design
- [x] RESTful principles followed
- [x] Consistent naming conventions
- [x] Proper HTTP methods used (GET, POST, PUT, DELETE)
- [x] Pagination implemented for all list endpoints
- [x] Filtering and search implemented
- [x] Versioning ready (can add /api/v1/ if needed)

## 🛠️ Maintenance Guidelines

### Adding New Features

1. **Create Model** in `models.py`
   ```python
   class NewModel(models.Model):
       """Description"""
       owner = models.ForeignKey(User, ...)
       created_at = models.DateTimeField(auto_now_add=True)
       
       class Meta:
           ordering = ['-created_at']
       
       def __str__(self):
           return f"..."
   ```

2. **Create Serializer** in `serializers.py`
   ```python
   class NewModelSerializer(serializers.ModelSerializer):
       class Meta:
           model = NewModel
           fields = ['id', 'field1', 'field2', ...]
   ```

3. **Create View** in `views.py`
   ```python
   @extend_schema(
       summary="Brief description",
       description="Full description"
   )
   class NewModelView(generics.ListCreateAPIView):
       queryset = NewModel.objects.all()
       serializer_class = NewModelSerializer
       permission_classes = [IsAuthenticated]
   ```

4. **Register URL** in `urls.py`
   ```python
   path('new-model/', NewModelView.as_view(), name='new_model')
   ```

5. **Create Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Test**
   - Write test in appropriate test file
   - Add endpoint to TESTING_GUIDE.md
   - Update API_ENDPOINTS_REFERENCE.md

### Bug Fixes

1. Identify affected files
2. Write test that reproduces the bug
3. Implement fix
4. Ensure all tests pass
5. Update CHANGELOG.md

### Performance Optimization

Check with:
```bash
# Enable Django Debug Toolbar
# Install: pip install django-debug-toolbar
# Add to INSTALLED_APPS and MIDDLEWARE in settings.py

# Then monitor:
# - Query count (target: < 10 queries per request)
# - Query execution time
# - Template rendering time
# - Memory usage
```

## 🚀 Deployment Checklist

Before deploying to production:

```bash
# 1. Run migrations
python manage.py migrate

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run tests
python manage.py test

# 4. Check for security issues
python manage.py check --deploy

# 5. Verify environment variables
# Required in .env:
# - SECRET_KEY
# - DEBUG=False
# - ALLOWED_HOSTS
# - DATABASE_URL
# - CORS_ALLOWED_ORIGINS
```

## 📚 References

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Python PEP 8 Style Guide](https://pep8.org/)
- [API Endpoints Reference](API_ENDPOINTS_REFERENCE.md)
- [Testing Guide](TESTING_GUIDE.md)

## 🔄 Next Steps

1. Run full test suite (see TESTING_GUIDE.md)
2. Deploy to staging environment
3. Perform load testing
4. Monitor for errors in production
5. Gather user feedback
6. Plan next feature release
