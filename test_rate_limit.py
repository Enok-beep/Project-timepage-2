#!/usr/bin/env python3
"""
Focused test for rate limiting functionality
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
print(f"Testing rate limiting at: {BASE_URL}")

def test_rate_limiting():
    print("\n=== Rate Limiting Test ===")
    
    # Test Case A: First POST with email 'demo@example.com' returns 200
    print("Case A: First POST with email 'demo@example.com'")
    try:
        payload = {"email": "demo@example.com"}
        response = requests.post(f"{BASE_URL}/api/notify", json=payload, timeout=10)
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")
            print("✅ Case A PASSED: First request returned 200")
        else:
            print(f"❌ Case A FAILED: Expected 200, got {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Case A FAILED: {e}")
        return
    
    # Test Case B: Second POST within 60s from same IP and same email returns 429
    print("\nCase B: Second POST within 60s (same email)")
    try:
        payload = {"email": "demo@example.com"}
        response = requests.post(f"{BASE_URL}/api/notify", json=payload, timeout=10)
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 429:
            print("✅ Case B PASSED: Second request with same email returned 429")
        else:
            print(f"❌ Case B FAILED: Expected 429, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Case B FAILED: {e}")
    
    # Test Case C: POST with different email but same IP within 60s returns 429 (per-IP limit)
    print("\nCase C: Different email, same IP within 60s")
    try:
        payload = {"email": "different@example.com"}
        response = requests.post(f"{BASE_URL}/api/notify", json=payload, timeout=10)
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 429:
            print("✅ Case C PASSED: Different email from same IP returned 429")
        else:
            print(f"❌ Case C FAILED: Expected 429, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Case C FAILED: {e}")
    
    # Test Case E: Invalid email returns 422
    print("\nCase E: Invalid email")
    try:
        payload = {"email": "invalid-email"}
        response = requests.post(f"{BASE_URL}/api/notify", json=payload, timeout=10)
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 422:
            print("✅ Case E PASSED: Invalid email returned 422")
        else:
            print(f"❌ Case E FAILED: Expected 422, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Case E FAILED: {e}")

if __name__ == "__main__":
    test_rate_limiting()