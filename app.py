#!/usr/bin/env python3
"""
Professor Al Gorithm - AI Agent for Teaching Algorithm Design Canvas Methodology
Gradio interface for the educational AI agent that integrates with Topcoder MCP server

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

class MCPClient:
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
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.endpoint, json=payload, headers=headers) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            result = json.loads(text)
                            if 'result' in result:
                                return result['result']
                            elif 'error' in result:
                                print(f"❌ MCP error: {result['error']}")
                                return None
                            return result
                        except json.JSONDecodeError:
                            # Try SSE parsing as fallback
                            return self._parse_sse_response(text)
                    else:
                        response_text = await response.text()
                        print(f"❌ Request failed ({response.status}): {response_text[:200]}...")
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
                        # Parse the JSON (might be double-encoded)
                        data = json.loads(data_str)
                        if isinstance(data, dict) and 'result' in data:
                            result = data['result']
                            if isinstance(result, dict) and 'content' in result:
                                content = result['content']
                                if isinstance(content, list) and len(content) > 0:
                                    # Extract the actual data from MCP response
                                    first_content = content[0]
                                    if isinstance(first_content, dict) and 'text' in first_content:
                                        # Sometimes the text is double-encoded JSON
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
    mcp_client = MCPClient(MCP_HTTP_ENDPOINT, MCP_SESSION_TOKEN)
    print("🔑 MCP client initialized with session token")
else:
    print("⚠️ No session token - MCP integration disabled")

class ProfessorAlGorithm:
    """Main class for the Professor Al Gorithm AI agent interface"""
    
    def __init__(self):
        self.current_phase = "constraints"
        self.session_data = {}
        self.selected_challenge = None
        self.available_challenges = []
    
    async def get_challenges(self, difficulty: str = "easy") -> Tuple[str, list]:
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        }
                    },
                    "id": "connect_init"
                },
                # Method 2: Simple connection
                {
                    "jsonrpc": "2.0", 
                    "method": "connect",
                    "params": {},
                    "id": "connect_simple"
                },
                # Method 3: Public handshake
                {
                    "jsonrpc": "2.0",
                    "method": "handshake", 
                    "params": {},
                    "id": "connect_handshake"
                }
            ]
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for i, payload in enumerate(connection_methods, 1):
                    print(f"🔄 Trying connection method {i}: {payload['method']}")
                    
                    async with session.post(self.endpoint, json=payload, headers=headers) as response:
                        response_text = await response.text()
                        print(f"🔍 Connection response ({response.status}): {response_text[:200]}...")
                        
                        if response.status == 200:
                            try:
                                result = json.loads(response_text)
                                if 'result' in result or 'error' not in result:
                                    print(f"✅ MCP connection established with method {i}")
                                    self.session_id = "public"  # Mark as connected
                                    return True
                            except json.JSONDecodeError:
                                pass
                        elif response.status != 400 or "No valid session ID provided" not in response_text:
                            # Different error - might indicate progress
                            print(f"🔍 Different response - continuing with method {i}")
                
                print("⚠️ Standard connection methods failed, trying session refresh...")
                return await self._refresh_session(session, headers)
                
        except Exception as e:
            print(f"❌ Connection establishment error: {e}")
            return False
    
    async def _refresh_session(self, session, headers) -> bool:
        """Try to refresh/re-establish the connection (no auth required)"""
        print("🔄 Attempting connection refresh...")
        
        refresh_methods = [
            # Try to ping/keepalive
            {
                "jsonrpc": "2.0", 
                "method": "ping",
                "params": {},
                "id": "refresh_1"
            },
            # Try connection status
            {
                "jsonrpc": "2.0",
                "method": "status", 
                "params": {},
                "id": "refresh_2"
            },
            # Try list available tools
            {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": "refresh_3"
            }
        ]
        
        for i, payload in enumerate(refresh_methods, 1):
            print(f"🔄 Trying refresh method {i}: {payload['method']}")
            
            async with session.post(self.endpoint, json=payload, headers=headers) as response:
                response_text = await response.text()
                print(f"🔍 Refresh response ({response.status}): {response_text[:200]}...")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        if 'result' in result:
                            print(f"✅ Connection refreshed with method {i}")
                            self.session_id = "public"
                            return True
                    except json.JSONDecodeError:
                        pass
        
        # Last resort - assume connection is working and proceed
        print("🤷 All connection attempts had issues, but proceeding anyway...")
        self.session_id = "public"
        return True

    async def _initialize_session(self) -> bool:
        """Initialize MCP connection (no authentication required)"""
        if self.session_id:
            return True
            
        return await self._establish_connection()

    async def _try_different_endpoints(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try the MCP request with different endpoints"""
        for endpoint in MCP_ENDPOINTS_TO_TRY:
            print(f"🔄 Trying endpoint: {endpoint}")
            original_endpoint = self.endpoint
            self.endpoint = endpoint
            result = await self._make_single_mcp_request(tool_name, arguments)
            self.endpoint = original_endpoint
            if result:
                print(f"✅ Success with endpoint: {endpoint}")
                return result
            print(f"❌ Failed with endpoint: {endpoint}")
        return None

    async def _make_mcp_request(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make MCP request using JSON-RPC 2.0"""
        # Initialize session if needed
        if not await self._initialize_session():
            print("❌ Failed to initialize MCP session")
            return None
            
        # First try the default endpoint
        result = await self._make_single_mcp_request(tool_name, arguments)
        if result:
            return result
            
        # If that fails, try different endpoints
        print("🔄 Default endpoint failed, trying alternatives...")
        return await self._try_different_endpoints(tool_name, arguments)

    async def _make_single_mcp_request(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a single MCP request to the current endpoint"""
            
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream',
            }
            
            # Try different payload formats (no authentication required)
            payloads_to_try = [
                # Format 1: Standard tools/call format
                {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments,
                    },
                    "id": f"req_{int(time.time() * 1000)}"
                },
                # Format 2: Direct tool call
                {
                    "jsonrpc": "2.0",
                    "method": tool_name,
                    "params": arguments,
                    "id": f"req_{int(time.time() * 1000)}"
                },
                # Format 3: Tool call with arguments as top-level
                {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    **arguments,
                    "tool": tool_name,
                    "id": f"req_{int(time.time() * 1000)}"
                }
            ]
            
            print(f"🔍 Debug - Request headers: {list(headers.keys())}")
            print(f"🔍 Debug - Using public MCP server (no authentication)")
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            # Try each payload format until one works
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for i, payload in enumerate(payloads_to_try, 1):
                    print(f"🔍 Trying payload format {i}: {payload.get('method', 'unknown')}")
                    
                    async with session.post(self.endpoint, json=payload, headers=headers) as response:
                        if response.status == 200:
                            text = await response.text()
                            try:
                                result = json.loads(text)
                                if 'result' in result:
                                    print(f"✅ Success with payload format {i}")
                                    return result['result']
                                elif 'error' in result:
                                    print(f"❌ MCP error (format {i}): {result['error']}")
                                    continue  # Try next format
                                return result
                            except json.JSONDecodeError:
                                # Try SSE parsing as fallback
                                parsed = self._parse_sse_response(text)
                                if parsed:
                                    print(f"✅ Success with SSE parsing (format {i})")
                                    return parsed
                                continue  # Try next format
                        else:
                            response_text = await response.text()
                            print(f"❌ Format {i} failed ({response.status}): {response_text[:100]}...")
                            continue  # Try next format
                
                # If we get here, all formats failed
                return None
                        
        except Exception as e:
            print(f"MCP request error: {e}")
            return None
    
    def _parse_sse_response(self, sse_text: str) -> Optional[Dict[str, Any]]:
        """Parse Server-Sent Events response and extract JSON data"""
        try:
            lines = sse_text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    try:
                        # Parse the JSON (might be double-encoded)
                        data = json.loads(data_str)
                        if isinstance(data, dict) and 'result' in data:
                            result = data['result']
                            if isinstance(result, dict) and 'content' in result:
                                content = result['content']
                                if isinstance(content, list) and len(content) > 0:
                                    # Extract the actual data from MCP response
                                    first_content = content[0]
                                    if isinstance(first_content, dict) and 'text' in first_content:
                                        # Sometimes the text is double-encoded JSON
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

# Initialize MCP client - no authentication required
mcp_client = MCPClient(MCP_HTTP_ENDPOINT)
print("🔓 MCP client initialized for public access")

class ProfessorAlGorithm:
    """Main class for the Professor Al Gorithm AI agent interface"""
    
    def __init__(self):
        self.current_phase = "constraints"
        self.session_data = {}
        self.selected_challenge = None
        self.available_challenges = []
    
    async def get_challenges(self, difficulty: str = "easy") -> Tuple[str, list]:
        """Get coding challenges and return both display text and challenge data"""
        # Validate input
        if difficulty not in ['easy', 'medium', 'hard']:
            difficulty = 'easy'
        
        # Try MCP first if available
        if mcp_client:
            try:
                print(f"🔍 Fetching {difficulty} challenges from Topcoder MCP...")
                print(f"🔗 MCP endpoint: {mcp_client.endpoint}")
                mcp_data = await mcp_client.get_challenges(difficulty, 5)
                print(f"📊 MCP response: {type(mcp_data)} - {str(mcp_data)[:200] if mcp_data else 'None'}...")
                
                if mcp_data and 'challenges' in mcp_data:
                    print(f"✅ Got {len(mcp_data['challenges'])} challenges from MCP")
                    challenges = mcp_data['challenges']
                    self.available_challenges = challenges
                    display_text = self._format_mcp_challenges(mcp_data, difficulty)
                    return display_text, challenges
                else:
                    print(f"⚠️ MCP returned no challenges: {mcp_data}")
                    
            except Exception as e:
                print(f"❌ MCP request failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("🚫 No MCP client available")
        
        # Fallback to educational content
        print(f"📚 Using educational {difficulty} challenges")
        await asyncio.sleep(0.5)  # Simulate fetch delay
        challenges = self._get_fallback_challenge_data(difficulty)
        self.available_challenges = challenges
        display_text = self._format_challenge_selection(challenges, difficulty)
        return display_text, challenges
    
    def _get_fallback_challenge_data(self, difficulty: str = "easy") -> list:
        """Get structured challenge data for selection"""
        
        challenges_by_difficulty = {
            'easy': [
                {
                    "id": "two-sum",
                    "name": "Two Sum Problem",
                    "description": "Given an array of integers and a target sum, find two numbers that add up to the target.",
                    "skills": ["Hash tables", "Array traversal"],
                    "difficulty": "easy",
                    "examples": [
                        {"input": "[2,7,11,15], target=9", "output": "[0,1]"},
                        {"input": "[3,2,4], target=6", "output": "[1,2]"}
                    ]
                },
                {
                    "id": "valid-parentheses",
                    "name": "Valid Parentheses",
                    "description": "Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
                    "skills": ["Stack data structure", "String processing"],
                    "difficulty": "easy",
                    "examples": [
                        {"input": "\"()\"", "output": "true"},
                        {"input": "\"([)]\"", "output": "false"}
                    ]
                },
                {
                    "id": "palindrome-check",
                    "name": "Palindrome Check",
                    "description": "Determine if a given string reads the same forward and backward.",
                    "skills": ["Two pointers technique", "String manipulation"],
                    "difficulty": "easy",
                    "examples": [
                        {"input": "\"racecar\"", "output": "true"},
                        {"input": "\"hello\"", "output": "false"}
                    ]
                },
                {
                    "id": "merge-sorted-lists",
                    "name": "Merge Two Sorted Lists",
                    "description": "Merge two sorted linked lists and return it as a new sorted list.",
                    "skills": ["Linked lists", "Merge algorithms"],
                    "difficulty": "easy",
                    "examples": [
                        {"input": "[1,2,4], [1,3,4]", "output": "[1,1,2,3,4,4]"},
                        {"input": "[], [0]", "output": "[0]"}
                    ]
                },
                {
                    "id": "remove-duplicates",
                    "name": "Remove Duplicates",
                    "description": "Remove duplicates from a sorted array in-place.",
                    "skills": ["Two pointers", "Array manipulation"],
                    "difficulty": "easy",
                    "examples": [
                        {"input": "[1,1,2]", "output": "[1,2]"},
                        {"input": "[0,0,1,1,1,2,2,3,3,4]", "output": "[0,1,2,3,4]"}
                    ]
                }
            ],
            'medium': [
                {
                    "id": "maximum-subarray",
                    "name": "Maximum Subarray (Kadane's Algorithm)",
                    "description": "Find the contiguous subarray within a one-dimensional array that has the largest sum.",
                    "skills": ["Dynamic programming", "Optimization"],
                    "difficulty": "medium",
                    "examples": [
                        {"input": "[-2,1,-3,4,-1,2,1,-5,4]", "output": "6 (subarray [4,-1,2,1])"},
                        {"input": "[1]", "output": "1"}
                    ]
                },
                {
                    "id": "longest-substring",
                    "name": "Longest Substring Without Repeating Characters",
                    "description": "Find the length of the longest substring without repeating characters.",
                    "skills": ["Sliding window", "Hash maps"],
                    "difficulty": "medium",
                    "examples": [
                        {"input": "\"abcabcbb\"", "output": "3 (\"abc\")"},
                        {"input": "\"bbbbb\"", "output": "1 (\"b\")"}
                    ]
                }
            ],
            'hard': [
                {
                    "id": "median-two-arrays",
                    "name": "Median of Two Sorted Arrays",
                    "description": "Find the median of two sorted arrays with optimal time complexity.",
                    "skills": ["Binary search", "Divide and conquer"],
                    "difficulty": "hard",
                    "examples": [
                        {"input": "[1,3], [2]", "output": "2.0"},
                        {"input": "[1,2], [3,4]", "output": "2.5"}
                    ]
                }
            ]
        }
        
        return challenges_by_difficulty.get(difficulty, challenges_by_difficulty['easy'])
    
    def _format_challenge_selection(self, challenges: list, difficulty: str) -> str:
        """Format challenges for selection UI"""
        result = f"## 🎯 Select a {difficulty.title()} Challenge\n\n"
        result += "Choose a challenge to work on using the Algorithm Design Canvas:\n\n"
        
        for i, challenge in enumerate(challenges, 1):
            result += f"**{i}. {challenge['name']}**\n"
            result += f"📝 {challenge['description']}\n"
            result += f"🛠️ Skills: {', '.join(challenge['skills'])}\n"
            if 'examples' in challenge and challenge['examples']:
                example = challenge['examples'][0]
                result += f"💡 Example: {example['input']} → {example['output']}\n"
            result += "\n"
        
        result += "🎨 **Next Step**: Click on a challenge number below to select it and start working!"
        return result
    
    def select_challenge(self, challenge_index: int) -> str:
        """Select a challenge and prepare for Algorithm Design Canvas"""
        if not self.available_challenges:
            return "❌ No challenges available. Please get challenges first."
        
        if challenge_index < 1 or challenge_index > len(self.available_challenges):
            return f"❌ Invalid selection. Please choose a number between 1 and {len(self.available_challenges)}."
        
        self.selected_challenge = self.available_challenges[challenge_index - 1]
        self.current_phase = "constraints"
        
        challenge = self.selected_challenge
        result = f"## ✅ Challenge Selected: {challenge['name']}\n\n"
        result += f"**Description:** {challenge['description']}\n\n"
        result += f"**Skills Focus:** {', '.join(challenge['skills'])}\n\n"
        
        if 'examples' in challenge and challenge['examples']:
            result += "**Examples:**\n"
            for ex in challenge['examples'][:2]:  # Show up to 2 examples
                result += f"• Input: {ex['input']} → Output: {ex['output']}\n"
            result += "\n"
        
        result += "🎨 **Ready for Algorithm Design Canvas!**\n"
        result += "Now click on the **1️⃣ Constraints** tab to start working through this challenge step by step."
        
        return result
    
    def _get_fallback_challenges(self, difficulty: str = "easy") -> str:
        """Provide educational challenges based on difficulty level"""
        
        challenges_by_difficulty = {
            'easy': [
                "**🎯 Two Sum Problem**\nGiven an array of integers and a target sum, find two numbers that add up to the target.\n*Skills: Hash tables, array traversal*",
                "**🎯 Valid Parentheses**\nGiven a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n*Skills: Stack data structure, string processing*",
                "**🎯 Palindrome Check**\nDetermine if a given string reads the same forward and backward.\n*Skills: Two pointers technique, string manipulation*",
                "**🎯 Merge Two Sorted Lists**\nMerge two sorted linked lists and return it as a new sorted list.\n*Skills: Linked lists, merge algorithms*",
                "**🎯 Remove Duplicates**\nRemove duplicates from a sorted array in-place.\n*Skills: Two pointers, array manipulation*"
            ],
            'medium': [
                "**🎯 Maximum Subarray (Kadane's Algorithm)**\nFind the contiguous subarray within a one-dimensional array that has the largest sum.\n*Skills: Dynamic programming, optimization*",
                "**🎯 Longest Substring Without Repeating Characters**\nFind the length of the longest substring without repeating characters.\n*Skills: Sliding window, hash maps*",
                "**🎯 Binary Tree Level Order Traversal**\nReturn the level order traversal of a binary tree's nodes' values.\n*Skills: BFS, queue data structure, trees*",
                "**🎯 3Sum Problem**\nFind all unique triplets in an array that sum to zero.\n*Skills: Two pointers, sorting, array manipulation*",
                "**🎯 Rotated Sorted Array Search**\nSearch for a target value in a rotated sorted array.\n*Skills: Binary search, modified algorithms*"
            ],
            'hard': [
                "**🎯 Median of Two Sorted Arrays**\nFind the median of two sorted arrays with optimal time complexity.\n*Skills: Binary search, divide and conquer*",
                "**🎯 N-Queens Problem**\nPlace N queens on an N×N chessboard so that no two queens attack each other.\n*Skills: Backtracking, constraint satisfaction*",
                "**🎯 Word Ladder**\nFind the shortest transformation sequence from a start word to an end word.\n*Skills: BFS, graph algorithms, string manipulation*",
                "**🎯 Serialize and Deserialize Binary Tree**\nDesign an algorithm to serialize and deserialize a binary tree.\n*Skills: Tree traversal, string parsing, design patterns*",
                "**🎯 Regular Expression Matching**\nImplement regular expression matching with support for '.' and '*'.\n*Skills: Dynamic programming, recursion, pattern matching*"
            ]
        }
        
        selected_challenges = challenges_by_difficulty.get(difficulty, challenges_by_difficulty['easy'])
        
        result = f"## 🎯 {difficulty.title()} Coding Challenges\n\n"
        for i, challenge in enumerate(selected_challenges, 1):
            result += f"{i}. {challenge}\n\n"
        
        result += f"💡 **Learning Focus**: These {difficulty} challenges help you practice fundamental problem-solving patterns!\n"
        result += "🎨 **Next Step**: Choose one challenge and work through it using the Algorithm Design Canvas below."
        
        return result
    
    def _format_mcp_challenges(self, mcp_data: Dict[str, Any], difficulty: str) -> str:
        """Format MCP challenge data for display"""
        try:
            challenges = mcp_data.get('challenges', [])
            if not challenges:
                return self._get_fallback_challenges(difficulty)
            
            result = f"## 🎯 Topcoder {difficulty.title()} Challenges\n\n"
            
            for i, challenge in enumerate(challenges[:5], 1):
                name = challenge.get('name', f'Challenge #{i}')
                track = challenge.get('track', 'Programming')
                description = challenge.get('description', 'No description available')
                
                # Truncate long descriptions
                if len(description) > 200:
                    description = description[:200] + "..."
                
                result += f"{i}. **{name}**\n"
                result += f"   📚 Track: {track}\n"
                result += f"   📝 {description}\n\n"
            
            result += f"🌟 **Real Challenges**: These are actual {difficulty} challenges from Topcoder!\n"
            result += "🎨 **Next Step**: Choose one challenge and work through it using the Algorithm Design Canvas below."
            
            return result
            
        except Exception as e:
            print(f"Error formatting MCP challenges: {e}")
            return self._get_fallback_challenges(difficulty)
    
    async def get_skills(self, category: str = "algorithms") -> str:
        """Get skills data from Topcoder MCP or fallback content"""
        # Validate input
        valid_categories = ['algorithms', 'data-structures', 'dynamic-programming', 'graphs']
        if category not in valid_categories:
            category = 'algorithms'
        
        # Try MCP first if available
        if mcp_client:
            try:
                print(f"🔍 Fetching {category} skills from Topcoder MCP...")
                mcp_data = await mcp_client.get_skills(category, 10)
                
                if mcp_data and 'skills' in mcp_data:
                    return self._format_mcp_skills(mcp_data, category)
                else:
                    print("⚠️ MCP returned no skills, using fallback")
                    
            except Exception as e:
                print(f"❌ MCP request failed: {e}")
        
        # Fallback to educational content
        print(f"📚 Using educational {category} skills")
        await asyncio.sleep(0.5)  # Simulate fetch delay
        return self._get_fallback_skills(category)
    
    def _get_fallback_skills(self, category: str = "algorithms") -> str:
        """Provide fallback skills when MCP is unavailable"""
        skills_by_category = {
            'algorithms': [
                "**Array Manipulation** - Working with arrays, indices, and traversal patterns",
                "**Two Pointers Technique** - Efficient array traversal using multiple pointers", 
                "**Hash Tables** - Fast lookups, counting, and memoization strategies",
                "**Sorting & Searching** - Binary search, merge sort, quicksort fundamentals",
                "**Recursion & Backtracking** - Breaking problems into smaller subproblems"
            ],
            'data-structures': [
                "**Linked Lists** - Node-based data structures and pointer manipulation",
                "**Stacks & Queues** - LIFO and FIFO data structures for problem solving",
                "**Trees & Binary Trees** - Hierarchical data structures and traversals",
                "**Heaps** - Priority queues and heap-based algorithms",
                "**Graphs** - Graph representation, traversal, and pathfinding"
            ],
            'dynamic-programming': [
                "**Memoization** - Top-down approach with caching",
                "**Tabulation** - Bottom-up approach with iterative solutions",
                "**Optimal Substructure** - Breaking problems into optimal subproblems",
                "**State Transition** - Defining states and transitions between them",
                "**Space Optimization** - Reducing memory usage in DP solutions"
            ],
            'graphs': [
                "**Graph Representation** - Adjacency lists, matrices, and edge lists",
                "**BFS & DFS** - Breadth-first and depth-first search algorithms",
                "**Shortest Paths** - Dijkstra's algorithm and pathfinding",
                "**Topological Sorting** - Ordering vertices in directed acyclic graphs",
                "**Connected Components** - Finding and analyzing graph connectivity"
            ]
        }
        
        skills = skills_by_category.get(category, skills_by_category['algorithms'])
        return f"## Recommended {category.title()} Skills to Practice\n\n" + "\n".join(f"• {skill}" for skill in skills)
    
    def _format_mcp_skills(self, mcp_data: Dict[str, Any], category: str) -> str:
        """Format MCP skills data for display"""
        try:
            skills = mcp_data.get('skills', [])
            if not skills:
                return self._get_fallback_skills(category)
            
            result = f"## 🛠️ Topcoder {category.title()} Skills\n\n"
            
            for i, skill in enumerate(skills[:8], 1):
                name = skill.get('name', f'Skill #{i}')
                description = skill.get('description', 'No description available')
                category_info = skill.get('category', {})
                
                if isinstance(category_info, dict):
                    cat_name = category_info.get('name', 'Unknown')
                else:
                    cat_name = str(category_info) if category_info else 'Unknown'
                
                # Truncate long descriptions
                if len(description) > 150:
                    description = description[:150] + "..."
                
                result += f"• **{name}**\n"
                result += f"  📂 Category: {cat_name}\n"
                if description and description != 'No description available':
                    result += f"  📖 {description}\n"
                result += "\n"
            
            result += f"🌟 **Real Skills**: These are actual {category} skills from Topcoder's platform!\n"
            result += "💡 **Practice Tip**: Focus on one skill at a time and solve related challenges."
            
            return result
            
        except Exception as e:
            print(f"Error formatting MCP skills: {e}")
            return self._get_fallback_skills(category)
    
    def _format_challenges_for_display(self, data: Dict[str, Any]) -> str:
        """Format challenge data for educational display"""
        if not data or 'challenges' not in data:
            return "No challenges available. Try refreshing or check your connection."
        
        challenges = data['challenges']
        if not challenges:
            return "No challenges found for the selected difficulty. Try a different difficulty level."
            
        count = data.get('count', len(challenges))
        processing_time = data.get('processingTime', 0)
        
        formatted = f"## 🎯 Available Coding Challenges ({count} found)\n\n"
        
        for i, challenge in enumerate(challenges[:5], 1):  # Show top 5
            name = challenge.get('name', f'Challenge #{i}')
            track = challenge.get('track', 'Unknown Track')
            status = challenge.get('status', 'Unknown Status')
            description = challenge.get('description', 'No description available')
            
            # Truncate long descriptions
            if len(description) > 200:
                description = description[:200] + "..."
                
            formatted += f"**{i}. {name}**\n"
            formatted += f"📚 Track: {track}\n"
            formatted += f"🔄 Status: {status}\n"
            formatted += f"📝 Description: {description}\n\n"
        
        if processing_time > 0:
            formatted += f"\n⚡ *Retrieved in {processing_time}ms*"
        
        return formatted
    
    def _format_skills_for_display(self, data: Dict[str, Any]) -> str:
        """Format skills data for educational display"""
        if not data or 'skills' not in data:
            return "No skills data available. Try refreshing or check your connection."
        
        skills = data['skills']
        if not skills:
            return "No skills found for the selected category. Try a different category."
            
        count = len(skills)
        processing_time = data.get('processingTime', 0)
        
        formatted = f"## 🛠️ Recommended Skills to Practice ({count} found)\n\n"
        
        for i, skill in enumerate(skills[:8], 1):  # Show top 8
            name = skill.get('name', f'Skill #{i}')
            category_info = skill.get('category', {})
            
            if isinstance(category_info, dict):
                category = category_info.get('name', 'Unknown Category')
                category_desc = category_info.get('description', '')
            else:
                category = str(category_info) if category_info else 'Unknown Category'
                category_desc = ''
            
            description = skill.get('description', 'No description available')
            
            # Truncate long descriptions
            if len(description) > 150:
                description = description[:150] + "..."
                
            formatted += f"• **{name}**\n"
            formatted += f"  📂 Category: {category}\n"
            
            if description and description != 'No description available':
                formatted += f"  📖 Description: {description}\n"
            
            if category_desc:
                formatted += f"  🎯 Focus: {category_desc[:100]}{'...' if len(category_desc) > 100 else ''}\n"
                
            formatted += "\n"
        
        if processing_time > 0:
            formatted += f"\n⚡ *Retrieved in {processing_time}ms*"
        
        return formatted
    
    def guide_canvas_phase(self, phase: str, user_input: str) -> Tuple[str, str]:
        """Guide user through Algorithm Design Canvas phases with context awareness"""
        
        # Get challenge-specific context
        challenge_context = ""
        if self.selected_challenge:
            challenge = self.selected_challenge
            challenge_context = f"\n\n**📋 Current Challenge: {challenge['name']}**\n"
            challenge_context += f"*{challenge['description']}*\n"
            if 'examples' in challenge and challenge['examples']:
                challenge_context += f"*Example: {challenge['examples'][0]['input']} → {challenge['examples'][0]['output']}*\n"
        
        phase_guidance = {
            "constraints": {
                "title": "Phase 1: Define Constraints",
                "guidance": f"""Let's analyze the constraints for your selected challenge:{challenge_context}

🔍 **Key Questions to Consider:**

1. **Input Format**: What type of data are you working with?
   - What data structures are involved?
   - What are the input ranges or limits?

2. **Output Format**: What should your solution return?
   - Exact format required?
   - Any specific data type?

3. **Performance Requirements**: Are there time/space complexity limits?
   - How many elements might you process?
   - Memory constraints?

4. **Edge Cases**: What special scenarios should you handle?
   - Empty inputs, null values?
   - Minimum/maximum cases?

💡 **Your Task**: Analyze the challenge above and define the constraints clearly."""
            },
            "ideas": {
                "title": "Phase 2: Brainstorm Solution Ideas", 
                "guidance": f"""Now let's explore different approaches for your challenge:{challenge_context}

🧠 **Brainstorming Framework:**

1. **Brute Force**: What's the most straightforward solution?
   - How would you solve this step by step?
   - Don't worry about efficiency yet!

2. **Pattern Recognition**: What algorithmic patterns might apply?
   {f"- Consider: {', '.join(self.selected_challenge['skills'])}" if self.selected_challenge else ""}
   - Hash tables, two pointers, sliding window, etc.?

3. **Optimized Approaches**: Can we improve time/space complexity?
   - What's the bottleneck in the brute force approach?
   - Which data structures could help?

4. **Trade-offs**: What are the pros and cons of each approach?

💡 **Your Task**: Share your solution ideas and I'll help you evaluate them!"""
            },
            "tests": {
                "title": "Phase 3: Design Test Cases",
                "guidance": f"""Let's create comprehensive test scenarios for your challenge:{challenge_context}

🧪 **Testing Strategy:**

1. **Basic Cases**: Start with the given examples
   {f"- Try working through: {self.selected_challenge['examples'][0]['input']}" if self.selected_challenge and 'examples' in self.selected_challenge else ""}

2. **Edge Cases**: What boundary conditions exist?
   - Empty inputs, single elements
   - Minimum/maximum values
   - Zero, negative numbers?

3. **Corner Cases**: Unusual but valid scenarios
   - What tricky inputs might break your solution?

4. **Invalid Cases**: How should your solution handle bad input?
   - Null inputs, wrong data types

💡 **Your Task**: Design test cases that thoroughly validate your solution!"""
            },
            "code": {
                "title": "Phase 4: Structure Your Code",
                "guidance": f"""Time to organize your implementation for:{challenge_context}

👩‍💻 **Implementation Planning:**

1. **Function Signature**: Define your main function
   - What parameters does it need?
   - What should it return?

2. **Algorithm Steps**: Break down your chosen approach
   - List the main steps in order
   - Identify the core logic

3. **Helper Functions**: What utilities do you need?
   - Validation, data processing, etc.

4. **Implementation Plan**: Step-by-step coding approach
   - Which part will you implement first?
   - How will you test as you go?

💡 **Remember**: I'll guide your thinking and help you structure your approach, but you'll write the actual code!"""
            }
        }
        
        current_guidance = phase_guidance.get(phase, phase_guidance["constraints"])
        response = f"## {current_guidance['title']}\n\n{current_guidance['guidance']}"
        
        if user_input.strip():
            response += f"\n\n**Your Input:** {user_input}\n\nGreat! Let me help you think through this..."
        
        return response, phase

def create_gradio_interface():
    """Create and configure the Gradio interface"""
    
    professor = ProfessorAlGorithm()
    
    with gr.Blocks(
        title="Professor Al Gorithm - Algorithm Design Canvas",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1200px; margin: auto; }
        .phase-header { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
        .canvas-section { border: 2px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
        """
    ) as interface:
        
        # Header
        gr.Markdown("""
        # 🎓 Professor Al Gorithm
        ## Learn Algorithm Design Canvas Methodology with Real Topcoder Challenges
        
        Master problem-solving through our structured 4-phase approach: **Constraints → Ideas → Tests → Code**
        """, elem_classes=["phase-header"])
        
        with gr.Row():
            with gr.Column(scale=1):
                # Challenge Selection
                gr.Markdown("### 📚 Challenge Library")
                difficulty_select = gr.Dropdown(
                    choices=["easy", "medium", "hard"],
                    value="easy",
                    label="Difficulty Level"
                )
                get_challenges_btn = gr.Button("🎯 Get New Challenges", variant="primary")
                challenges_display = gr.Markdown("Click 'Get New Challenges' to start!")
                
                # Challenge Selection
                gr.Markdown("### 🎯 Select Your Challenge")
                challenge_selector = gr.Radio(
                    choices=[],
                    label="Choose a challenge to work on:",
                    visible=False
                )
                select_challenge_btn = gr.Button("📝 Select This Challenge", visible=False)
                challenge_status = gr.Markdown("")
                
                # Skills Recommendations  
                gr.Markdown("### 🛠️ Skills to Practice")
                category_select = gr.Dropdown(
                    choices=["algorithms", "data-structures", "dynamic-programming", "graphs"],
                    value="algorithms",
                    label="Skill Category"
                )
                get_skills_btn = gr.Button("📖 Get Skills Guide")
                skills_display = gr.Markdown("Click 'Get Skills Guide' for recommendations!")
            
            with gr.Column(scale=2):
                # Algorithm Design Canvas
                gr.Markdown("### 🎨 Algorithm Design Canvas", elem_classes=["canvas-section"])
                
                phase_tabs = gr.Tabs()
                with phase_tabs:
                    with gr.TabItem("1️⃣ Constraints", id="constraints"):
                        constraints_input = gr.Textbox(
                            label="Define your problem constraints",
                            placeholder="Describe the problem, input/output format, and requirements...",
                            lines=4
                        )
                        constraints_output = gr.Markdown()
                        constraints_btn = gr.Button("Guide Me Through Constraints")
                    
                    with gr.TabItem("2️⃣ Ideas", id="ideas"):
                        ideas_input = gr.Textbox(
                            label="Share your solution ideas",
                            placeholder="What approaches are you considering?",
                            lines=4
                        )
                        ideas_output = gr.Markdown()
                        ideas_btn = gr.Button("Help Me Brainstorm")
                    
                    with gr.TabItem("3️⃣ Test Cases", id="tests"):
                        tests_input = gr.Textbox(
                            label="Design your test cases",
                            placeholder="What test scenarios should you consider?",
                            lines=4
                        )
                        tests_output = gr.Markdown()
                        tests_btn = gr.Button("Review My Test Cases")
                    
                    with gr.TabItem("4️⃣ Code Structure", id="code"):
                        code_input = gr.Textbox(
                            label="Plan your implementation",
                            placeholder="How will you structure your solution?",
                            lines=4
                        )
                        code_output = gr.Markdown()
                        code_btn = gr.Button("Guide My Implementation")
        
        # Status and Progress with enhanced information
        with gr.Row():
            status_display = gr.Markdown(
                """**Status:** Ready to start learning! 🚀  
                **System:** Professor Al Gorithm
                
                💡 **Tips:**
                - Start with an easy challenge to warm up
                - Follow the 4-phase Canvas approach: Constraints → Ideas → Tests → Code  
                - Take your time with each phase - learning is more important than speed!
                """
            )
        
        # Event handlers with error handling and loading states
        async def fetch_challenges(difficulty):
            try:
                if not difficulty:
                    return "❌ Please select a difficulty level first.", gr.update(visible=False), gr.update(visible=False), gr.update(value="")
                    
                display_text, challenges = await professor.get_challenges(difficulty)
                
                # Create radio button choices
                radio_choices = [f"{i}. {challenge['name']}" for i, challenge in enumerate(challenges, 1)]
                
                return (
                    display_text,
                    gr.update(choices=radio_choices, visible=True, value=None),
                    gr.update(visible=True),
                    gr.update(value="")
                )
            except Exception as e:
                print(f"Error in fetch_challenges: {e}")
                fallback_text = professor._get_fallback_challenges()
                return fallback_text, gr.update(visible=False), gr.update(visible=False), gr.update(value="")
        
        async def fetch_skills(category):
            try:
                if not category:
                    return "❌ Please select a skill category first."
                return await professor.get_skills(category)
            except Exception as e:
                print(f"Error in fetch_skills: {e}")
                return f"❌ Unexpected error: {str(e)}\n\n" + professor._get_fallback_skills(category)
        
        def select_challenge_handler(selected_challenge):
            try:
                if not selected_challenge:
                    return "❌ Please select a challenge first."
                
                # Extract challenge number from selection (e.g., "1. Two Sum Problem" -> 1)
                challenge_num = int(selected_challenge.split('.')[0])
                return professor.select_challenge(challenge_num)
            except Exception as e:
                print(f"Error in select_challenge_handler: {e}")
                return f"❌ Error selecting challenge: {str(e)}"

        def guide_phase(phase, user_input):
            try:
                if not professor.selected_challenge:
                    return "❌ Please select a challenge first before working on the Algorithm Design Canvas.", phase
                    
                if not user_input or not user_input.strip():
                    return f"Please provide some input for the {phase} phase to get guidance.", phase
                    
                if len(user_input.strip()) < 10:
                    return f"Please provide more detailed input for the {phase} phase (at least 10 characters).", phase
                    
                return professor.guide_canvas_phase(phase, user_input.strip())
            except Exception as e:
                print(f"Error in guide_phase: {e}")
                return f"❌ Error processing your input: {str(e)}\n\nPlease try again with your {phase} phase input.", phase
        
        # Connect buttons to functions with enhanced loading states and error handling
        get_challenges_btn.click(
            fn=fetch_challenges,
            inputs=[difficulty_select],
            outputs=[challenges_display, challenge_selector, select_challenge_btn, challenge_status],
            show_progress="full",
            scroll_to_output=True,
            show_api=False  # Hide API details from users
        )
        
        select_challenge_btn.click(
            fn=select_challenge_handler,
            inputs=[challenge_selector],
            outputs=[challenge_status],
            show_progress="minimal",
            scroll_to_output=True,
            show_api=False
        )
        
        get_skills_btn.click(
            fn=fetch_skills,
            inputs=[category_select],
            outputs=[skills_display],
            show_progress="full",
            scroll_to_output=True,
            show_api=False
        )
        
        # Canvas phase guidance with enhanced progress indicators
        constraints_btn.click(
            fn=lambda inp: guide_phase("constraints", inp),
            inputs=[constraints_input],
            outputs=[constraints_output],
            show_progress="minimal",
            scroll_to_output=True,
            show_api=False
        )
        
        ideas_btn.click(
            fn=lambda inp: guide_phase("ideas", inp),
            inputs=[ideas_input],
            outputs=[ideas_output],
            show_progress="minimal",
            scroll_to_output=True,
            show_api=False
        )
        
        tests_btn.click(
            fn=lambda inp: guide_phase("tests", inp),
            inputs=[tests_input],
            outputs=[tests_output],
            show_progress="minimal",
            scroll_to_output=True,
            show_api=False
        )
        
        code_btn.click(
            fn=lambda inp: guide_phase("code", inp),
            inputs=[code_input],
            outputs=[code_output],
            show_progress="minimal",
            scroll_to_output=True,
            show_api=False
        )
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    app = create_gradio_interface()
    
    # Launch configuration for Hugging Face Spaces
    # Allow port to be overridden by environment variable
    port = int(os.getenv("GRADIO_SERVER_PORT", 7860))
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        debug=False
    )
