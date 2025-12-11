#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if test user exists
if User.objects.filter(phone_number='1234567890').exists():
    print('Test user already exists')
else:
    user = User.objects.create_user(phone_number='1234567890', password='testpass123', name='Test User')
    print(f'Created user: {user.phone_number}')
