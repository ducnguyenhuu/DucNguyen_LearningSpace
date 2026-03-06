#!/usr/bin/env python3
"""
Debug script to show exactly what's being sent to New Relic.
"""

import requests
import json

print("API Key Debug - Showing exact request details")
print("=" * 70)

# Load from config
from modules.config_loader import load_config
config = load_config('dev')
api_key = config['api_key']

print(f"API Key from config file:")
print(f"  Raw value: '{api_key}'")
print(f"  Length: {len(api_key)} characters")
print(f"  First 10 chars: '{api_key[:10]}'")
print(f"  Last 10 chars: '{api_key[-10:]}'")
print(f"  Has spaces at start? {api_key[0] == ' '}")
print(f"  Has spaces at end? {api_key[-1] == ' '}")
print(f"  Stripped length: {len(api_key.strip())}")
print()

# Show what we're sending
query = '{ actor { user { email } } }'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print("Request Details:")
print(f"  Endpoint: https://api.newrelic.com/graphql")
print(f"  Authorization header: 'Bearer {api_key[:15]}...'")
print(f"  Full header length: {len(headers['Authorization'])}")
print()

# Make request with verbose output
print("Making request...")
response = requests.post(
    'https://api.newrelic.com/graphql',
    json={'query': query},
    headers=headers,
    timeout=10
)

print(f"Response Status: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Body: {response.text[:500]}")
print()

if response.status_code == 401:
    print("=" * 70)
    print("DIAGNOSIS:")
    print()
    print("Still getting 401 after trying multiple new keys suggests:")
    print()
    print("1. CHECK: Are you creating keys in the SAME account (2760100)?")
    print("   - When creating key, verify account dropdown shows 2760100")
    print()
    print("2. CHECK: User account permissions")
    print("   - Your New Relic user might not have API key usage rights")
    print("   - Ask your New Relic admin to verify your user role")
    print()
    print("3. CHECK: Organization API restrictions")
    print("   - Your org might require API keys to be approved/activated")
    print("   - Contact your New Relic admin")
    print()
    print("4. TRY: Use an EXISTING working key")
    print("   - If you have Postman/curl working with New Relic API")
    print("   - Use that exact same API key here")
    print()
    print("5. VERIFY: Copy-paste the key correctly")
    print("   - Make sure no extra spaces before/after")
    print("   - Should be exactly NRAK- followed by 30 more characters")
