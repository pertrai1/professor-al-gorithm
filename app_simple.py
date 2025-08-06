#!/usr/bin/env python3
"""
Professor Al Gorithm - AI Agent for Teaching Algorithm Design Canvas Methodology
Simple version with working MCP integration
"""

import gradio as gr
import os
from typing import Dict, Any, Optional, Tuple
import asyncio
import time
import aiohttp
import json
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (for local development)
# In Hugging Face Spaces, environment variables are automatically available
try:
    load_dotenv('.env')
except:
    pass  # Ignore if .env file doesn't exist (normal in Hugging Face Spaces)

# Configuration - Topcoder MCP (Authentication required despite docs claiming otherwise)
MCP_HTTP_ENDPOINT = "https://api.topcoder-dev.com/v6/mcp/mcp"
MCP_SESSION_TOKEN = os.getenv("MCP_SESSION_TOKEN")

print("🎓 Professor Al Gorithm starting...")
print(f"🔗 MCP HTTP endpoint: {MCP_HTTP_ENDPOINT}")
if MCP_SESSION_TOKEN:
    print(f"🔑 Session token: ***{MCP_SESSION_TOKEN[-10:]}")
    print("✅ MCP authentication configured")
else:
    print("❌ No MCP_SESSION_TOKEN found - will use fallback content")

class SimpleMCPClient:
    """Simple MCP client for Topcoder integration"""
    
    def __init__(self, endpoint: str, session_token: str):
        self.endpoint = endpoint
        self.session_token = session_token

    async def _make_mcp_request(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a simple MCP request with session authentication"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream',
                'X-MCP-Session': self.session_token,
            }
            
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments,
                },
                "id": f"req_{int(time.time() * 1000)}"
            }
            
            print(f"🔄 Making MCP request: {tool_name}")
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.endpoint, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    print(f"📊 MCP response ({response.status}): {response_text[:200]}...")
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_text)
                            if 'result' in result:
                                return result['result']
                            elif 'error' in result:
                                print(f"❌ MCP error: {result['error']}")
                                return None
                            return result
                        except json.JSONDecodeError:
                            return self._parse_sse_response(response_text)
                    else:
                        print(f"❌ Request failed ({response.status})")
                        return None
                        
        except Exception as e:
            print(f"❌ MCP request error: {e}")
            return None

    def _parse_sse_response(self, sse_text: str) -> Optional[Dict[str, Any]]:
        """Parse Server-Sent Events response and extract JSON data"""
        try:
            lines = sse_text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    try:
                        data = json.loads(data_str)
                        if isinstance(data, dict) and 'result' in data:
                            result = data['result']
                            if isinstance(result, dict) and 'content' in result:
                                content = result['content']
                                if isinstance(content, list) and len(content) > 0:
                                    first_content = content[0]
                                    if isinstance(first_content, dict) and 'text' in first_content:
                                        text_content = first_content['text']
                                        try:
                                            return json.loads(text_content)
                                        except:
                                            return {'raw_text': text_content}
                            return result
                        return data
                    except json.JSONDecodeError:
                        continue
            return None
        except Exception as e:
            print(f"SSE parsing error: {e}")
            return None
    
    async def get_challenges(self, difficulty: str = "easy", limit: int = 5) -> Optional[Dict[str, Any]]:
        """Get challenges from Topcoder MCP"""
        return await self._make_mcp_request("query-tc-challenges", {
            "difficulty": difficulty,
            "limit": limit
        })
    
    async def get_skills(self, category: str = "algorithms", limit: int = 10) -> Optional[Dict[str, Any]]:
        """Get skills from Topcoder MCP"""
        return await self._make_mcp_request("query-tc-skills", {
            "category": category,
            "limit": limit
        })

# Initialize MCP client - authentication required
mcp_client = None
if MCP_SESSION_TOKEN:
    mcp_client = SimpleMCPClient(MCP_HTTP_ENDPOINT, MCP_SESSION_TOKEN)
    print("🔑 MCP client initialized with session token")
else:
    print("⚠️ No session token - MCP integration disabled")

def test_simple_connection():
    """Simple test function"""
    print("🧪 Testing simple MCP connection...")
    if mcp_client:
        # Run async test
        async def test_async():
            result = await mcp_client.get_challenges("easy", 2)
            if result:
                print("✅ MCP connection successful!")
                print(f"📊 Result type: {type(result)}")
                print(f"📊 Result: {str(result)[:300]}...")
            else:
                print("❌ MCP connection failed")
                
        # Run the test
        asyncio.run(test_async())
    else:
        print("❌ No MCP client available")

if __name__ == "__main__":
    test_simple_connection()