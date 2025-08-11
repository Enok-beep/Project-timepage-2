#!/usr/bin/env python3
"""
Backend API Testing Script for Timepage-style App
Tests the FastAPI backend endpoints per contracts.md requirements
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

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
if not BASE_URL:
    print("ERROR: Could not determine backend URL")
    sys.exit(1)

print(f"Testing backend at: {BASE_URL}")

class TestResults:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        self.results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def summary(self):
        print(f"\n=== TEST SUMMARY ===")
        print(f"Total tests: {len(self.results)}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success rate: {(self.passed/len(self.results)*100):.1f}%")
        
        if self.failed > 0:
            print(f"\n=== FAILED TESTS ===")
            for result in self.results:
                if not result['passed']:
                    print(f"❌ {result['test']}: {result['details']}")

def test_get_palettes(test_results: TestResults):
    """Test GET /api/palettes endpoint"""
    print("\n--- Testing GET /api/palettes ---")
    
    try:
        response = requests.get(f"{BASE_URL}/api/palettes", timeout=10)
        
        # Test 1: Status code should be 200
        if response.status_code == 200:
            test_results.add_result("GET /api/palettes - Status 200", True)
        else:
            test_results.add_result("GET /api/palettes - Status 200", False, 
                                   f"Got status {response.status_code}")
            return
        
        # Test 2: Response should be valid JSON
        try:
            data = response.json()
            test_results.add_result("GET /api/palettes - Valid JSON", True)
        except json.JSONDecodeError as e:
            test_results.add_result("GET /api/palettes - Valid JSON", False, str(e))
            return
        
        # Test 3: Should return an array
        if isinstance(data, list):
            test_results.add_result("GET /api/palettes - Returns array", True)
        else:
            test_results.add_result("GET /api/palettes - Returns array", False, 
                                   f"Got {type(data).__name__}")
            return
        
        # Test 4: Should have 9 curated palettes
        if len(data) == 9:
            test_results.add_result("GET /api/palettes - 9 palettes", True)
        else:
            test_results.add_result("GET /api/palettes - 9 palettes", False, 
                                   f"Got {len(data)} palettes")
        
        # Test 5: Each palette should have required fields
        required_fields = ['id', 'name', 'bg', 'color', 'baseBg', 'baseColor', 'accent', 'subtle']
        all_fields_valid = True
        missing_fields = []
        
        for i, palette in enumerate(data):
            for field in required_fields:
                if field not in palette:
                    all_fields_valid = False
                    missing_fields.append(f"Palette {i}: missing '{field}'")
                elif not isinstance(palette[field], str):
                    all_fields_valid = False
                    missing_fields.append(f"Palette {i}: '{field}' is not string")
        
        if all_fields_valid:
            test_results.add_result("GET /api/palettes - All fields present and strings", True)
        else:
            test_results.add_result("GET /api/palettes - All fields present and strings", False, 
                                   "; ".join(missing_fields[:3]))  # Show first 3 issues
        
        # Test 6: Verify specific palette IDs exist
        expected_ids = ['arctic', 'azure', 'indigo', 'scarlet', 'mandarin', 'mint', 'forest', 'charcoal', 'sand']
        actual_ids = [p['id'] for p in data]
        
        if set(expected_ids) == set(actual_ids):
            test_results.add_result("GET /api/palettes - Expected palette IDs", True)
        else:
            missing = set(expected_ids) - set(actual_ids)
            extra = set(actual_ids) - set(expected_ids)
            details = f"Missing: {missing}, Extra: {extra}" if missing or extra else "IDs match"
            test_results.add_result("GET /api/palettes - Expected palette IDs", 
                                   len(missing) == 0 and len(extra) == 0, details)
        
    except requests.exceptions.RequestException as e:
        test_results.add_result("GET /api/palettes - Request", False, str(e))

def test_post_preferences(test_results: TestResults):
    """Test POST /api/preferences endpoint"""
    print("\n--- Testing POST /api/preferences ---")
    
    # Test Case A: Send palette_id without session_id
    print("Case A: New preference without session_id")
    try:
        payload = {"palette_id": "arctic"}
        response = requests.post(f"{BASE_URL}/api/preferences", 
                               json=payload, timeout=10)
        
        if response.status_code == 200:
            test_results.add_result("POST /api/preferences - Case A Status 200", True)
            
            try:
                data = response.json()
                
                # Should have session_id, palette_id, updated_at
                required_fields = ['session_id', 'palette_id', 'updated_at']
                has_all_fields = all(field in data for field in required_fields)
                
                if has_all_fields:
                    test_results.add_result("POST /api/preferences - Case A Required fields", True)
                    
                    # Verify palette_id matches
                    if data['palette_id'] == 'arctic':
                        test_results.add_result("POST /api/preferences - Case A Palette ID match", True)
                    else:
                        test_results.add_result("POST /api/preferences - Case A Palette ID match", False,
                                               f"Expected 'arctic', got '{data['palette_id']}'")
                    
                    # Verify session_id is generated
                    if data['session_id'] and len(data['session_id']) > 0:
                        test_results.add_result("POST /api/preferences - Case A Session ID generated", True)
                        session_id = data['session_id']  # Save for Case B
                    else:
                        test_results.add_result("POST /api/preferences - Case A Session ID generated", False)
                        session_id = None
                    
                    # Verify updated_at is ISO format
                    try:
                        datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
                        test_results.add_result("POST /api/preferences - Case A ISO timestamp", True)
                    except ValueError:
                        test_results.add_result("POST /api/preferences - Case A ISO timestamp", False,
                                               f"Invalid timestamp: {data['updated_at']}")
                else:
                    missing = [f for f in required_fields if f not in data]
                    test_results.add_result("POST /api/preferences - Case A Required fields", False,
                                           f"Missing: {missing}")
                    session_id = None
                    
            except json.JSONDecodeError as e:
                test_results.add_result("POST /api/preferences - Case A Valid JSON", False, str(e))
                session_id = None
        else:
            test_results.add_result("POST /api/preferences - Case A Status 200", False,
                                   f"Got status {response.status_code}")
            session_id = None
            
    except requests.exceptions.RequestException as e:
        test_results.add_result("POST /api/preferences - Case A Request", False, str(e))
        session_id = None
    
    # Test Case B: Reuse session_id with new palette_id
    if session_id:
        print("Case B: Update preference with existing session_id")
        try:
            payload = {"palette_id": "mint", "session_id": session_id}
            response = requests.post(f"{BASE_URL}/api/preferences", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                test_results.add_result("POST /api/preferences - Case B Status 200", True)
                
                try:
                    data = response.json()
                    
                    # Should return same session_id
                    if data.get('session_id') == session_id:
                        test_results.add_result("POST /api/preferences - Case B Same session ID", True)
                    else:
                        test_results.add_result("POST /api/preferences - Case B Same session ID", False,
                                               f"Expected '{session_id}', got '{data.get('session_id')}'")
                    
                    # Should have updated palette_id
                    if data.get('palette_id') == 'mint':
                        test_results.add_result("POST /api/preferences - Case B Updated palette ID", True)
                    else:
                        test_results.add_result("POST /api/preferences - Case B Updated palette ID", False,
                                               f"Expected 'mint', got '{data.get('palette_id')}'")
                    
                    # Should have updated timestamp
                    if 'updated_at' in data:
                        test_results.add_result("POST /api/preferences - Case B Updated timestamp", True)
                    else:
                        test_results.add_result("POST /api/preferences - Case B Updated timestamp", False)
                        
                except json.JSONDecodeError as e:
                    test_results.add_result("POST /api/preferences - Case B Valid JSON", False, str(e))
            else:
                test_results.add_result("POST /api/preferences - Case B Status 200", False,
                                       f"Got status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            test_results.add_result("POST /api/preferences - Case B Request", False, str(e))
    
    # Test Case C: Invalid palette_id
    print("Case C: Invalid palette_id")
    try:
        payload = {"palette_id": "invalid_palette"}
        response = requests.post(f"{BASE_URL}/api/preferences", 
                               json=payload, timeout=10)
        
        if response.status_code == 404:
            test_results.add_result("POST /api/preferences - Case C Status 404", True)
            
            try:
                data = response.json()
                if data.get('detail') == 'Palette not found':
                    test_results.add_result("POST /api/preferences - Case C Error message", True)
                else:
                    test_results.add_result("POST /api/preferences - Case C Error message", False,
                                           f"Expected 'Palette not found', got '{data.get('detail')}'")
            except json.JSONDecodeError:
                test_results.add_result("POST /api/preferences - Case C Error message", False,
                                       "Response not valid JSON")
        else:
            test_results.add_result("POST /api/preferences - Case C Status 404", False,
                                   f"Got status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        test_results.add_result("POST /api/preferences - Case C Request", False, str(e))

def test_post_notify(test_results: TestResults):
    """Test POST /api/notify endpoint"""
    print("\n--- Testing POST /api/notify ---")
    
    # Test Case A: Valid email
    print("Case A: Valid email")
    try:
        payload = {"email": "test@example.com"}
        response = requests.post(f"{BASE_URL}/api/notify", 
                               json=payload, timeout=10)
        
        if response.status_code == 200:
            test_results.add_result("POST /api/notify - Case A Status 200", True)
            
            try:
                data = response.json()
                if data.get('status') == 'ok':
                    test_results.add_result("POST /api/notify - Case A Response format", True)
                else:
                    test_results.add_result("POST /api/notify - Case A Response format", False,
                                           f"Expected {{'status': 'ok'}}, got {data}")
            except json.JSONDecodeError as e:
                test_results.add_result("POST /api/notify - Case A Valid JSON", False, str(e))
        else:
            test_results.add_result("POST /api/notify - Case A Status 200", False,
                                   f"Got status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        test_results.add_result("POST /api/notify - Case A Request", False, str(e))
    
    # Test Case B: Repeat same email (should still work - upsert)
    print("Case B: Repeat same email")
    try:
        payload = {"email": "test@example.com"}
        response = requests.post(f"{BASE_URL}/api/notify", 
                               json=payload, timeout=10)
        
        if response.status_code == 200:
            test_results.add_result("POST /api/notify - Case B Status 200 (upsert)", True)
            
            try:
                data = response.json()
                if data.get('status') == 'ok':
                    test_results.add_result("POST /api/notify - Case B Response format", True)
                else:
                    test_results.add_result("POST /api/notify - Case B Response format", False,
                                           f"Expected {{'status': 'ok'}}, got {data}")
            except json.JSONDecodeError as e:
                test_results.add_result("POST /api/notify - Case B Valid JSON", False, str(e))
        else:
            test_results.add_result("POST /api/notify - Case B Status 200 (upsert)", False,
                                   f"Got status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        test_results.add_result("POST /api/notify - Case B Request", False, str(e))
    
    # Test Case C: Invalid email formats
    print("Case C: Invalid email formats")
    invalid_emails = ["invalid-email", "test@", "@example.com", "test.example.com", ""]
    
    for invalid_email in invalid_emails:
        try:
            payload = {"email": invalid_email}
            response = requests.post(f"{BASE_URL}/api/notify", 
                                   json=payload, timeout=10)
            
            if response.status_code == 422:
                test_results.add_result(f"POST /api/notify - Invalid email '{invalid_email}' -> 422", True)
            else:
                test_results.add_result(f"POST /api/notify - Invalid email '{invalid_email}' -> 422", False,
                                       f"Got status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            test_results.add_result(f"POST /api/notify - Invalid email '{invalid_email}' request", False, str(e))

def main():
    print("=== Backend API Testing ===")
    print(f"Target: {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    test_results = TestResults()
    
    # Run tests in order as specified
    test_get_palettes(test_results)
    test_post_preferences(test_results)
    test_post_notify(test_results)
    
    # Print summary
    test_results.summary()
    
    # Return exit code based on results
    return 0 if test_results.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())