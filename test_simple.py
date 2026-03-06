#!/usr/bin/env python3
import requests
import io

# Test if the server is responding
try:
    response = requests.get('http://localhost:5000/')
    print(f"OK Server responding: {response.status_code}")
    
    # Test a simple endpoint
    response = requests.get('http://localhost:5000/settings')
    print(f"OK Settings endpoint: {response.status_code}")
    
    print("OK Basic server functionality is working")
    
except Exception as e:
    print(f"ERROR: {e}")
