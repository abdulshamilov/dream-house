import requests
import json

# Test JWT token endpoint
url = "http://127.0.0.1:8000/api/token/"
payload = {
    "phone_number": "1234567890",
    "password": "testpass123"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access')
        
        # Now test protected endpoint with token
        print("\n--- Testing protected endpoint with token ---")
        headers = {"Authorization": f"Bearer {access_token}"}
        ai_url = "http://127.0.0.1:8000/api/cards/ai/chat/"
        ai_payload = {
            "message": "Hello",
            "mode": "free"
        }
        
        ai_response = requests.post(ai_url, json=ai_payload, headers=headers)
        print(f"AI Chat Status Code: {ai_response.status_code}")
        print(f"AI Chat Response: {ai_response.text}")
except Exception as e:
    print(f"Error: {e}")
