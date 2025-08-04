#!/usr/bin/env python3
"""
Professor Al Gorithm - AI Agent for Teaching Algorithm Design Canvas Methodology
Gradio interface for the educational AI agent that integrates with Topcoder MCP server

Module 7 Enhanced Version: End-to-End Testing & Debugging Features
- Comprehensive error handling and fallback behavior
- Timeout management and retry logic  
- Edge case handling for unexpected inputs
- Enhanced user feedback and loading states
- Performance monitoring and optimization
"""

import gradio as gr
import os
from typing import Dict, Any, Optional, Tuple
import asyncio
import time
import aiohttp
import json

# Configuration - Updated for Topcoder MCP (no auth required)
MCP_SSE_ENDPOINT = "https://api.topcoder-dev.com/v6/mcp/sse"
MCP_HTTP_ENDPOINT = "https://api.topcoder-dev.com/v6/mcp/mcp"

print("🎓 Professor Al Gorithm starting...")
print(f"🔗 MCP SSE endpoint: {MCP_SSE_ENDPOINT}")
print(f"🔗 MCP HTTP endpoint: {MCP_HTTP_ENDPOINT}")
print("📚 No authentication required for Topcoder MCP")
print("🔄 Trying HTTP endpoint first...")

class MCPClient:
    """Python MCP client for Topcoder integration"""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
    
    async def _make_mcp_request(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make MCP request using JSON-RPC 2.0"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": f"req_{int(time.time() * 1000)}"
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            # Try different approaches based on endpoint
            if "sse" in self.endpoint:
                # For SSE endpoint, try GET first
                print("🔄 Trying SSE endpoint with GET...")
                headers = {'Accept': 'text/event-stream'}
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    params = {"tools": tool_name, **arguments}
                    async with session.get(self.endpoint, params=params, headers=headers) as response:
                        if response.status == 200:
                            text = await response.text()
                            return self._parse_sse_response(text)
                        else:
                            print(f"SSE GET failed with status {response.status}")
            
            # For HTTP endpoint or if SSE failed, try POST
            print(f"🔄 Trying POST to {self.endpoint}...")
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.endpoint, json=payload, headers=headers) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Try parsing as JSON first, then SSE
                        try:
                            return json.loads(text)
                        except:
                            return self._parse_sse_response(text)
                    elif response.status == 404:
                        print(f"MCP endpoint not found (404) - endpoint may be incorrect")
                        return None
                    elif response.status == 503:
                        print(f"MCP server unavailable (503) - service may be down or overloaded")
                        return None
                    elif response.status == 401:
                        print(f"MCP authentication failed (401)")
                        return None
                    elif response.status == 429:
                        print(f"MCP rate limited (429) - too many requests")
                        return None
                    else:
                        print(f"MCP request failed with status {response.status}")
                        response_text = await response.text()
                        print(f"Response body: {response_text[:200]}...")
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

# Initialize MCP client - no auth required for Topcoder
# Try HTTP endpoint first since SSE gave 404
mcp_client = MCPClient(MCP_HTTP_ENDPOINT)

class ProfessorAlGorithm:
    """Main class for the Professor Al Gorithm AI agent interface"""
    
    def __init__(self):
        self.current_phase = "constraints"
        self.session_data = {}
    
    async def get_challenges(self, difficulty: str = "easy") -> str:
        """Get coding challenges from Topcoder MCP or fallback content"""
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
                    return self._format_mcp_challenges(mcp_data, difficulty)
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
        return self._get_fallback_challenges(difficulty)
    
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
        """Guide user through Algorithm Design Canvas phases"""
        phase_guidance = {
            "constraints": {
                "title": "Phase 1: Define Constraints",
                "guidance": """Let's start by understanding the problem constraints:

1. **Input Format**: What type of data are you working with?
2. **Output Format**: What should your solution return?
3. **Performance Requirements**: Time and space complexity limits?
4. **Edge Cases**: What special cases should you consider?

Share your problem statement and I'll help you identify the key constraints."""
            },
            "ideas": {
                "title": "Phase 2: Brainstorm Solution Ideas", 
                "guidance": """Now let's explore different approaches:

1. **Brute Force**: What's the most straightforward solution?
2. **Optimized Approaches**: Can we improve time/space complexity?
3. **Algorithm Patterns**: Which common patterns might apply?
4. **Trade-offs**: What are the pros and cons of each approach?

What ideas do you have for solving this problem?"""
            },
            "tests": {
                "title": "Phase 3: Design Test Cases",
                "guidance": """Let's create comprehensive test scenarios:

1. **Basic Cases**: Simple, expected inputs
2. **Edge Cases**: Empty inputs, single elements, boundaries  
3. **Corner Cases**: Unusual but valid scenarios
4. **Invalid Cases**: How should your solution handle bad input?

What test cases can you think of for your problem?"""
            },
            "code": {
                "title": "Phase 4: Structure Your Code",
                "guidance": """Time to organize your implementation:

1. **Function Signature**: Define your main function
2. **Algorithm Steps**: Break down your chosen approach
3. **Helper Functions**: What utilities do you need?
4. **Implementation Plan**: Step-by-step coding strategy

Remember: I'll guide your thinking, not write the code for you!"""
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
                get_challenges_btn = gr.Button("🎯 Get New Challenge", variant="primary")
                challenges_display = gr.Markdown("Click 'Get New Challenge' to start!")
                
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
                    return "❌ Please select a difficulty level first."
                return await professor.get_challenges(difficulty)
            except Exception as e:
                print(f"Error in fetch_challenges: {e}")
                return f"❌ Unexpected error: {str(e)}\n\n" + professor._get_fallback_challenges()
        
        async def fetch_skills(category):
            try:
                if not category:
                    return "❌ Please select a skill category first."
                return await professor.get_skills(category)
            except Exception as e:
                print(f"Error in fetch_skills: {e}")
                return f"❌ Unexpected error: {str(e)}\n\n" + professor._get_fallback_skills(category)
        
        def guide_phase(phase, user_input):
            try:
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
            outputs=[challenges_display],
            show_progress="full",
            scroll_to_output=True,
            show_api=False  # Hide API details from users
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
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        debug=False
    )