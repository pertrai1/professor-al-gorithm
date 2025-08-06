#!/usr/bin/env python3
"""
Test Topcoder authentication flow to get JWT token
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('.env')

BASE_URL = "https://api.topcoder-dev.com"
SESSION_TOKEN = os.getenv("MCP_SESSION_TOKEN")
TOPCODER_HANDLE = os.getenv("TOPCODER_HANDLE")

def test_auth_endpoints():
    """Test potential authentication endpoints"""
    auth_endpoints = [
        f"{BASE_URL}/v6/mcp/auth",
        f"{BASE_URL}/v6/mcp/login", 
        f"{BASE_URL}/v6/mcp/token",
        f"{BASE_URL}/v6/mcp/jwt",
        f"{BASE_URL}/v6/auth",
        f"{BASE_URL}/v6/login",
        f"{BASE_URL}/auth",
        f"{BASE_URL}/login"
    ]
    
    print("🔍 Testing potential authentication endpoints:")
    
    for endpoint in auth_endpoints:
        print(f"\n🔗 Testing: {endpoint}")
        
        try:
            # Try GET first
            response = requests.get(endpoint, timeout=10)
            print(f"   GET {response.status_code}: {response.text[:200]}...")
            
            if response.status_code in [200, 405]:  # Success or method not allowed
                print("   ✅ Endpoint exists - trying POST...")
                
                # Try POST with session token
                post_data = {
                    "sessionId": SESSION_TOKEN,
                    "sessionToken": SESSION_TOKEN,
                    "handle": TOPCODER_HANDLE
                }
                
                try:
                    post_response = requests.post(endpoint, json=post_data, timeout=10)
                    print(f"   POST {post_response.status_code}: {post_response.text[:200]}...")
                    
                    if post_response.status_code == 200:
                        try:
                            result = post_response.json()
                            if 'token' in result or 'jwt' in result or 'accessToken' in result:
                                print("   🎉 FOUND JWT TOKEN ENDPOINT!")
                                return endpoint, result
                        except:
                            pass
                            
                except Exception as e:
                    print(f"   POST Error: {e}")
            
        except Exception as e:
            print(f"   GET Error: {e}")
    
    return None, None

def test_mcp_initialization():
    """Test MCP initialization handshake"""
    endpoint = f"{BASE_URL}/v6/mcp/mcp"
    
    print(f"\n🤝 Testing MCP initialization handshake:")
    
    # Try standard MCP initialization
    init_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "sessionId": SESSION_TOKEN
        },
        "id": "init"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-MCP-Session': SESSION_TOKEN,
    }
    
    try:
        response = requests.post(endpoint, json=init_payload, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            print("   ✅ Initialization successful!")
            return True
            
    except Exception as e:
        print(f"   Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🔐 Testing Topcoder Authentication Flow")
    print("=" * 60)
    
    if not SESSION_TOKEN:
        print("❌ No session token found")
        exit(1)
    
    print(f"🔑 Session token: ***{SESSION_TOKEN[-10:]}")
    print(f"👤 Topcoder handle: {TOPCODER_HANDLE}")
    
    # Test 1: Look for auth endpoints
    auth_endpoint, jwt_result = test_auth_endpoints()
    
    if auth_endpoint:
        print(f"\n✅ Found working auth endpoint: {auth_endpoint}")
        print(f"📄 Result: {jwt_result}")
    else:
        print("\n❌ No working auth endpoints found")
    
    # Test 2: Try MCP initialization
    init_success = test_mcp_initialization()
    
    if not init_success:
        print(f"\n💡 Recommendations:")
        print(f"1. Check Topcoder challenge forum for JWT token instructions")
        print(f"2. Your session token might need to be exchanged for a JWT")
        print(f"3. Contact Topcoder support about MCP authentication")