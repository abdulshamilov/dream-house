#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin exists
if User.objects.filter(phone_number='admin').exists():
    print('Admin user already exists')
    user = User.objects.get(phone_number='admin')
    print(f'Admin: {user.phone_number}, is_staff: {user.is_staff}, is_superuser: {user.is_superuser}')
else:
    user = User.objects.create_superuser(phone_number='admin', password='admin123')
    print(f'Created superuser: {user.phone_number}')
