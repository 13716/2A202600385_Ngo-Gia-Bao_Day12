import requests
import time

BASE_URL = "http://localhost:8000"
API_KEY = "super-secret-key-123"
HEADERS = {"X-API-Key": API_KEY}
SESSION_ID = "chat-101"

def print_result(step: str, resp: requests.Response):
    print(f"\n[{step}] Status: {resp.status_code}")
    try:
        print(resp.json())
    except:
        print(resp.text)
    time.sleep(1)

def test_full_pipeline():
    print("🚀 TESTING COST GUARD & CONVERSATION HISTORY...")
    
    # 1. Chat Turn 1
    resp1 = requests.post(
        f"{BASE_URL}/ask",
        headers=HEADERS,
        json={"question": "Hello, my name is Alex.", "session_id": SESSION_ID}
    )
    print_result("Chat Turn 1", resp1)

    # 2. Chat Turn 2
    resp2 = requests.post(
        f"{BASE_URL}/ask",
        headers=HEADERS,
        json={"question": "What is my name?", "session_id": SESSION_ID}
    )
    print_result("Chat Turn 2", resp2)

    # 3. View History
    resp_hist = requests.get(
        f"{BASE_URL}/history/{SESSION_ID}",
        headers=HEADERS
    )
    print("\n[View History]")
    history = resp_hist.json().get('history', [])
    for msg in history:
        print(f"[{msg['role']}]: {msg['content']}")
        
    # Lấy budget từ response cuối
    if resp2.status_code == 200:
        budget_usd = resp2.json().get('budget_used_usd')
        print(f"\n💰 Total Estimated Cost this month: ${budget_usd}")

if __name__ == "__main__":
    test_full_pipeline()
