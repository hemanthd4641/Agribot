import requests

url = "http://127.0.0.1:5000/chat"
payload = {"text": "What is the weather in Bengaluru for my tomato crop?"}
try:
    print(f"Sending POST to {url} with {payload}")
    response = requests.post(url, data=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
