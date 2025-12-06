import random
import requests

API_KEY = "73CF6BC6-704B-5E02-91A4-0E762C179A22"  # твой ключ sms.ru

def generate_otp():
    return f"{random.randint(1000, 9999)}"

def send_sms(phone_number, otp):
    url = "https://sms.ru/sms/send"
    params = {
        "api_id": API_KEY,
        "to": phone_number,
        "msg": f"Ваш код подтверждения: {otp}",
        "json": 1
    }
    response = requests.get(url, params=params)
    result = response.json()
    if result.get("status") != "OK":
        print("Ошибка отправки SMS:", result)
    return result
