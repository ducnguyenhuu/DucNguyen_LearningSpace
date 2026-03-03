#!/usr/bin/env python3
"""
Test network connectivity to New Relic API endpoints.
"""

import requests
import socket

print("Testing Network Connectivity to New Relic")
print("=" * 70)
print()

# Test 1: DNS resolution
print("Test 1: DNS Resolution")
try:
    ip = socket.gethostbyname('api.newrelic.com')
    print(f"  ✓ api.newrelic.com resolves to: {ip}")
except Exception as e:
    print(f"  ✗ Cannot resolve api.newrelic.com: {e}")
    print("  → You might need to be on company VPN/network")
print()

# Test 2: Basic connectivity (no auth)
print("Test 2: Basic HTTPS Connectivity")
try:
    response = requests.get('https://api.newrelic.com/graphql', timeout=10)
    print(f"  ✓ Can reach api.newrelic.com (Status: {response.status_code})")
    if response.status_code == 405:
        print("  ✓ Endpoint is reachable (405 is expected for GET request)")
except requests.exceptions.SSLError as e:
    print(f"  ✗ SSL/Certificate error: {e}")
    print("  → Your network might be using SSL inspection/corporate proxy")
except requests.exceptions.ProxyError as e:
    print(f"  ✗ Proxy error: {e}")
    print("  → You might need proxy configuration")
except requests.exceptions.ConnectionError as e:
    print(f"  ✗ Connection error: {e}")
    print("  → Firewall might be blocking api.newrelic.com")
    print("  → Try connecting to company VPN")
except Exception as e:
    print(f"  ✗ Error: {e}")
print()

# Test 3: Check if behind proxy
print("Test 3: Proxy Detection")
import os
http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

if http_proxy or https_proxy:
    print(f"  ⚠ Proxy detected:")
    if http_proxy:
        print(f"    HTTP_PROXY: {http_proxy}")
    if https_proxy:
        print(f"    HTTPS_PROXY: {https_proxy}")
    print(f"  → Requests will use this proxy")
else:
    print(f"  ℹ No proxy configured")
print()

# Test 4: Actual API request
print("Test 4: API Request (with your key)")
from modules.config_loader import load_config

try:
    config = load_config('dev')
    api_key = config['api_key']
    
    query = '{ actor { user { email } } }'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {'query': query}
    
    response = requests.post(
        'https://api.newrelic.com/graphql',
        json=payload,
        headers=headers,
        timeout=10
    )
    
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"  ✓ API request successful!")
        print(f"  → Your API key works from this network")
    elif response.status_code == 401:
        print(f"  ✗ 401 Unauthorized")
        print(f"  → Network is OK, but API key is invalid")
        print(f"  → Create a new User API key in New Relic")
    elif response.status_code == 403:
        print(f"  ✗ 403 Forbidden")
        print(f"  → API key lacks permissions")
    else:
        print(f"  ⚠ Unexpected response: {response.text[:200]}")
        
except Exception as e:
    print(f"  ✗ Error: {e}")

print()
print("=" * 70)
print("SUMMARY:")
print()
print("If DNS/connectivity tests pass but API returns 401:")
print("  → Network is fine, API key is the problem")
print("  → Create a new User API key in New Relic")
print()
print("If DNS/connectivity tests fail:")
print("  → Connect to company VPN and try again")
print("  → Check with IT if firewall blocks api.newrelic.com")
