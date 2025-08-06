#!/usr/bin/env python3
"""
Direct MCP server testing - bypass our application logic
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('.env')

MCP_ENDPOINT = "https://api.topcoder-dev.com/v6/mcp/mcp"
SESSION_TOKEN = os.getenv("MCP_SESSION_TOKEN")

def test_direct_request():
    """Test direct HTTP request to MCP server"""
    print(f"🔗 Testing direct request to: {MCP_ENDPOINT}")
    print(f"🔑 Using session token: ***{SESSION_TOKEN[-10:] if SESSION_TOKEN else 'None'}")
    
    # Test different header combinations
    header_combinations = [
        # Combination 1: X-MCP-Session only
        {
            'Content-Type': 'application/json',
            'X-MCP-Session': SESSION_TOKEN,
        },
        # Combination 2: Authorization Bearer
        {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SESSION_TOKEN}',
        },
        # Combination 3: Both headers
        {
            'Content-Type': 'application/json',
            'X-MCP-Session': SESSION_TOKEN,
            'Authorization': f'Bearer {SESSION_TOKEN}',
        },
        # Combination 4: Alternative session header
        {
            'Content-Type': 'application/json',
            'X-Session-Token': SESSION_TOKEN,
        },
        # Combination 5: Session in User-Agent (some APIs do this)
        {
            'Content-Type': 'application/json',
            'User-Agent': f'MCP-Client-Session-{SESSION_TOKEN}',
        }
    ]
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query-tc-challenges",
            "arguments": {
                "difficulty": "easy",
                "limit": 2
            }
        },
        "id": "test_request"
    }
    
    for i, headers in enumerate(header_combinations, 1):
        print(f"\n🧪 Testing header combination {i}:")
        print(f"   Headers: {list(headers.keys())}")
        
        try:
            response = requests.post(MCP_ENDPOINT, json=payload, headers=headers, timeout=30)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}...")
            
            if response.status_code == 200:
                print("✅ SUCCESS! This header combination works!")
                return True
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n❌ All header combinations failed")
    return False

def test_simple_endpoints():
    """Test different endpoint variants"""
    endpoints_to_test = [
        "https://api.topcoder-dev.com/v6/mcp/mcp",
        "https://api.topcoder-dev.com/v6/mcp",
        "https://api.topcoder-dev.com/v6/mcp/sse",
        "https://api.topcoder-dev.com/v6/mcp/tools",
        "https://api.topcoder-dev.com/v6/mcp/health",
    ]
    
    print(f"\n🌐 Testing different endpoints:")
    
    for endpoint in endpoints_to_test:
        print(f"\n🔗 Testing: {endpoint}")
        try:
            # Try GET request first
            response = requests.get(endpoint, timeout=10)
            print(f"   GET {response.status_code}: {response.text[:200]}...")
            
            if response.status_code not in [404, 405]:  # If GET works or method not allowed
                print(f"   ✅ Endpoint responds to GET")
            
        except Exception as e:
            print(f"   ❌ GET Error: {e}")

if __name__ == "__main__":
    print("🧪 Direct MCP Server Testing")
    print("=" * 50)
    
    if not SESSION_TOKEN:
        print("❌ No session token found in environment")
        exit(1)
    
    # Test 1: Direct requests with different headers
    success = test_direct_request()
    
    # Test 2: Different endpoints
    test_simple_endpoints()
    
    if not success:
        print("\n💡 Next steps:")
        print("1. Verify session token is current and valid")
        print("2. Check Topcoder challenge discussion for updated endpoints")
        print("3. Contact Topcoder support about MCP server status")