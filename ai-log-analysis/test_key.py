#!/usr/bin/env python3
"""
Simple API key validator - tests both US and EU endpoints.
"""

import requests
import json

# Your credentials
API_KEY = "NRAK-00DM4KGG7CVZ0XNBHJ864BHTBHW"
ACCOUNT_ID = "2760100"

print("Testing New Relic API Key Authentication")
print("=" * 70)
print(f"API Key: {API_KEY[:15]}... ({len(API_KEY)} characters)")
print(f"Account ID: {ACCOUNT_ID}")
print()

# Test both US and EU endpoints
endpoints = {
    "US": "https://api.newrelic.com/graphql",
    "EU": "https://api.eu.newrelic.com/graphql"
}

query = """
{
  actor {
    user {
      email
      name
    }
  }
}
"""

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
    'API-Key': API_KEY  # Some endpoints want this too
}

payload = {'query': query}

for region, endpoint in endpoints.items():
    print(f"Testing {region} endpoint: {endpoint}")
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"  ✗ GraphQL errors: {data['errors']}")
            elif 'data' in data:
                user = data.get('data', {}).get('actor', {}).get('user', {})
                print(f"  ✓ SUCCESS!")
                print(f"    Name: {user.get('name', 'N/A')}")
                print(f"    Email: {user.get('email', 'N/A')}")
                print()
                print(f">>> CORRECT ENDPOINT: {region} ({endpoint})")
                break
        elif response.status_code == 401:
            print(f"  ✗ 401 Unauthorized - API key rejected")
        elif response.status_code == 403:
            print(f"  ✗ 403 Forbidden - Insufficient permissions")
        else:
            print(f"  ✗ Unexpected status: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()

print("=" * 70)
print("DIAGNOSIS:")
print()
print("If BOTH failed with 401:")
print("  → Your API key is invalid/expired/wrong type")
print("  → Go to New Relic → API Keys → Create a NEW 'User' key")
print()
print("If one succeeded:")
print("  → Update config.yaml or api_client.py to use that endpoint")
