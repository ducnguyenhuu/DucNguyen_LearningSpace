#!/usr/bin/env python3
"""
Test script to verify New Relic API credentials.
"""

import requests
import json
from modules.config_loader import load_config

def test_api_connection():
    """Test basic API connectivity and authentication."""
    
    print("Loading configuration...")
    try:
        config = load_config('dev')
        api_key = config['api_key']
        account_id = config['account_id']
        app_ids = config['app_ids']
        
        print(f"✓ Configuration loaded")
        print(f"  - API Key: {api_key[:10]}... ({len(api_key)} chars)")
        print(f"  - Account ID: {account_id}")
        print(f"  - App IDs: {app_ids}")
        print()
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return
    
    # Test 1: Simple query to verify authentication
    print("Test 1: Verifying API authentication...")
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
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'query': query
    }
    
    try:
        response = requests.post(
            'https://api.newrelic.com/graphql',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for errors
            if 'errors' in data:
                print(f"✗ GraphQL Errors:")
                for error in data['errors']:
                    print(f"  - {error.get('message', error)}")
                return
            
            user = data.get('data', {}).get('actor', {}).get('user', {})
            if user:
                print(f"✓ Authentication successful!")
                print(f"  - Name: {user.get('name', 'N/A')}")
                print(f"  - Email: {user.get('email', 'N/A')}")
                print()
            else:
                print(f"✗ No user data returned")
                print(f"Response: {json.dumps(data, indent=2)}")
                return
        elif response.status_code == 401:
            print(f"✗ Authentication failed (401 Unauthorized)")
            print(f"   → Your API key is invalid or expired")
            print(f"   → Get a new User API key from: New Relic → API Keys")
            return
        elif response.status_code == 403:
            print(f"✗ Forbidden (403)")
            print(f"   → Your API key doesn't have required permissions")
            return
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return
    
    # Test 2: Query account to verify account_id
    print("Test 2: Verifying account access...")
    query = f"""
    {{
      actor {{
        account(id: {account_id}) {{
          id
          name
        }}
      }}
    }}
    """
    
    payload = {'query': query}
    
    try:
        response = requests.post(
            'https://api.newrelic.com/graphql',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"✗ GraphQL Errors:")
                for error in data['errors']:
                    print(f"  - {error.get('message', error)}")
                print()
                print("Common causes:")
                print("  - Wrong account_id (check New Relic account settings)")
                print("  - API key doesn't have access to this account")
                return
            
            account = data.get('data', {}).get('actor', {}).get('account', {})
            if account:
                print(f"✓ Account access verified!")
                print(f"  - Account ID: {account.get('id')}")
                print(f"  - Account Name: {account.get('name', 'N/A')}")
                print()
            else:
                print(f"✗ Cannot access account {account_id}")
                print(f"Response: {json.dumps(data, indent=2)}")
                return
        else:
            print(f"✗ Status code: {response.status_code}")
            return
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return
    
    # Test 3: Verify app_id access with NRQL query
    print("Test 3: Verifying application access...")
    app_id = app_ids[0]
    
    nrql_query = f"SELECT count(*) FROM Transaction WHERE appId = '{app_id}' SINCE 1 day ago"
    
    query = f"""
    query($accountId: Int!) {{
      actor {{
        account(id: $accountId) {{
          nrql(query: "{nrql_query}") {{
            results
          }}
        }}
      }}
    }}
    """
    
    variables = {
        'accountId': int(account_id)
    }
    
    payload = {
        'query': query,
        'variables': variables
    }
    
    try:
        response = requests.post(
            'https://api.newrelic.com/graphql',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"✗ GraphQL Errors:")
                for error in data['errors']:
                    print(f"  - {error.get('message', error)}")
                print()
                print("Common causes:")
                print("  - Wrong app_id (check New Relic APM application ID)")
                print("  - No data for this application in the last day")
                return
            
            results = data.get('data', {}).get('actor', {}).get('account', {}).get('nrql', {}).get('results', [])
            if results:
                print(f"✓ Application access verified!")
                print(f"  - App ID: {app_id}")
                print(f"  - Transaction count (last 24h): {results[0].get('count', 0)}")
                print()
                print("=" * 70)
                print("✓ ALL TESTS PASSED - Your credentials are working correctly!")
                print("=" * 70)
            else:
                print(f"⚠ Warning: No transaction data found for app_id={app_id}")
                print(f"  - The app_id might be correct but has no recent data")
                print(f"  - Check if the application is actively sending data to New Relic")
                
        else:
            print(f"✗ Status code: {response.status_code}")
            return
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return


if __name__ == '__main__':
    test_api_connection()
