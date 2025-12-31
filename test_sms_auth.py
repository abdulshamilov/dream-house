#!/usr/bin/env python
"""
Test SMS-based authentication
Usage: python test_sms_auth.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_sms_auth():
    phone = "+79991234567"
    
    print("=" * 60)
    print("SMS-Based Authentication Test")
    print("=" * 60)
    
    # Step 1: Request OTP
    print("\n[1] Requesting OTP...")
    response = requests.post(f"{BASE_URL}/users/sms/request/", 
        json={"phone_number": phone})
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    otp = data.get('otp')
    print(f"✓ OTP requested successfully")
    print(f"  OTP: {otp}")
    print(f"  Valid for: 5 minutes")
    
    # Step 2: Verify OTP
    print("\n[2] Verifying OTP and logging in...")
    time.sleep(1)  # Small delay
    
    response = requests.post(f"{BASE_URL}/users/sms/verify/", 
        json={"phone_number": phone, "otp": otp})
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    access_token = data.get('access')
    refresh_token = data.get('refresh')
    user = data.get('user')
    is_new = data.get('is_new')
    
    print(f"✓ OTP verified successfully")
    print(f"  User ID: {user['id']}")
    print(f"  Phone: {user['phone_number']}")
    print(f"  New user: {is_new}")
    print(f"  Access Token: {access_token[:50]}...")
    
    # Step 3: Use token to access protected endpoint
    print("\n[3] Testing protected endpoint (/me/)...")
    
    response = requests.get(f"{BASE_URL}/users/me/",
        headers={"Authorization": f"Bearer {access_token}"})
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False
    
    user_data = response.json()
    print(f"✓ Access token is valid")
    print(f"  Response: {json.dumps(user_data, indent=2)}")
    
    # Step 4: Test with invalid OTP
    print("\n[4] Testing with invalid OTP...")
    response = requests.post(f"{BASE_URL}/users/sms/verify/", 
        json={"phone_number": phone, "otp": "000000"})
    
    if response.status_code != 400:
        print(f"❌ Should have failed with 400, got {response.status_code}")
        return False
    
    error_data = response.json()
    print(f"✓ Invalid OTP rejected correctly")
    print(f"  Error: {error_data['detail']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_sms_auth()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
