import requests
import time

BASE_URL = "http://localhost:8000"
API_KEY = "super-secret-key-123"

def test_health():
    print("\n[1] Testing Health Check...")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Status: {resp.status_code}, Response: {resp.json()}")

def test_ask_auth_fail():
    print("\n[2] Testing Auth Failure (No Key)...")
    resp = requests.post(f"{BASE_URL}/ask?question=Hello")
    print(f"Status: {resp.status_code}, Response: {resp.json()}")

def test_ask_rate_limit():
    print("\n[3] Testing Rate Limiting (Limit: 5 req/min)...")
    headers = {"X-API-Key": API_KEY}
    
    for i in range(7):
        resp = requests.post(
            f"{BASE_URL}/ask",
            headers=headers,
            json={"question": f"Question {i+1}"}
        )
        print(f"Request {i+1}: Status {resp.status_code}", end=" ")
        if resp.status_code == 200:
            print(f"| Remaining: {resp.json().get('rate_info', {}).get('remaining')}")
        else:
            print(f"| Detail: {resp.json().get('detail')}")
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        test_health()
        test_ask_auth_fail()
        test_ask_rate_limit()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the agent is running at http://localhost:8000")
