#!/usr/bin/env python3
import requests
import json

def test_endpoints():
    base_url = "http://localhost:5000"
    
    tests = [
        ("GET", "/", "Home page"),
        ("GET", "/settings", "Settings endpoint"),
        ("POST", "/merge", "Merge endpoint"),
        ("POST", "/word-to-pdf", "Word to PDF endpoint"),
        ("POST", "/compress", "Compress endpoint"),
    ]
    
    print("Testing PDF Tools endpoints...")
    print("=" * 50)
    
    for method, endpoint, description in tests:
        try:
            if method == "GET":
                response = requests.get(base_url + endpoint, timeout=5)
            else:
                # For POST endpoints, just test if they respond (without files)
                response = requests.post(base_url + endpoint, timeout=5)
            
            status = "✓" if response.status_code in [200, 400] else "✗"
            print(f"{status} {method} {endpoint} - {response.status_code} - {description}")
            
            if response.status_code == 400:
                try:
                    error = response.json()
                    print(f"    Error: {error.get('error', 'Unknown error')}")
                except:
                    print(f"    Response: {response.text[:100]}")
                    
        except Exception as e:
            print(f"✗ {method} {endpoint} - ERROR: {e}")
    
    print("=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_endpoints()
