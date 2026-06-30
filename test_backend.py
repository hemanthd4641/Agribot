import requests
import time
import json
import threading
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    print("Testing /health ...", end=" ")
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=5)
        if res.status_code == 200:
            print("OK [PASS]")
        else:
            print(f"FAILED [FAIL] (Status: {res.status_code})")
    except Exception as e:
        print(f"FAILED [FAIL] ({e})")

def test_domain_guard():
    print("Testing Domain Guard (Non-Agri Query) ...", end=" ")
    try:
        res = requests.post(f"{BASE_URL}/chat", data={"text": "Write a python script for a discord bot."}, timeout=10)
        data = res.json()
        if "error" in data.get("text", "").lower() or "not related" in data.get("text", "").lower() or "agriculture" in data.get("text", "").lower():
            print("OK [PASS] (Rejected successfully)")
        else:
            print("FAILED [FAIL] (Did not reject)")
            print(data)
    except Exception as e:
        print(f"FAILED [FAIL] ({e})")

def test_intent_router_simple():
    print("Testing Intent Router (Weather Query) ...", end=" ")
    
    session = requests.Session() # To keep cookies/session ID
    
    # We will start the request in a thread so we can poll the status
    result = {}
    
    def run_req():
        try:
            res = session.post(f"{BASE_URL}/chat", data={"text": "What is the weather tomorrow in Bengaluru for my tomato crop?"}, timeout=60)
            result['data'] = res.json()
        except Exception as e:
            result['error'] = e

    t = threading.Thread(target=run_req)
    t.start()
    
    # Poll status while waiting
    statuses_seen = set()
    for _ in range(15):
        time.sleep(1)
        if not t.is_alive():
            break
        try:
            status_res = session.get(f"{BASE_URL}/chat/status")
            if status_res.status_code == 200:
                for agent_stat in status_res.json():
                    statuses_seen.add(agent_stat.get('agent'))
        except:
            pass
            
    t.join()
    
    if 'error' in result:
        print(f"FAILED [FAIL] ({result['error']})")
        return
        
    data = result.get('data', {})
    if "Weather" in data.get("text", ""):
        print("OK [PASS]")
        print(f"  -> Agents activated: {list(statuses_seen)}")
    else:
        print("FAILED [FAIL] (Weather data missing)")
        print(data)

if __name__ == "__main__":
    try:
        requests.get(BASE_URL, timeout=2)
    except:
        print("Server is not running on port 5000. Please start the server first.")
        sys.exit(1)
        
    print("Starting Automated Backend Tests...\n")
    test_health()
    test_domain_guard()
    test_intent_router_simple()
    print("\nTests complete.")
