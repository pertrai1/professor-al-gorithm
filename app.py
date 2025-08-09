#!/usr/bin/env python3
"""
Professor Al Gorithm - AI Agent for Teaching Algorithm Design Canvas Methodology
Final deployment version with robust fallback content and MCP integration ready for when server is fixed
"""

import gradio as gr
import os
from typing import Dict, Any, Optional, Tuple
import asyncio
import time
import aiohttp
import json
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (for local development)
# In Hugging Face Spaces, environment variables are automatically available
try:
    load_dotenv('.env')
except:
    pass  # Ignore if .env file doesn't exist (normal in Hugging Face Spaces)

# Configuration
MCP_SESSION_TOKEN = os.getenv("MCP_SESSION_TOKEN")

print("🎓 Professor Al Gorithm starting...")
if MCP_SESSION_TOKEN:
    print(f"🔑 Session token configured: ***{MCP_SESSION_TOKEN[-10:]}")
    print("🔧 MCP integration enabled - will attempt to connect to Topcoder")
else:
    print("🔧 Running with educational fallback content (no MCP token)")

class MCPClient:
    """MCP client for Topcoder integration"""
    
    def __init__(self, session_token: str = None):
        self.sse_url = "https://api.topcoder-dev.com/v6/mcp/sse"
        self.session_token = session_token  # Not needed for Topcoder but keeping for compatibility
        self.session_id = None
        self.initialized = False
    
    async def initialize_session(self) -> bool:
        """Initialize MCP session using SSE transport"""
        if self.initialized:
            return True
            
        try:
            # For SSE-based MCP servers, we can skip the formal initialize step
            # and go straight to making tool calls. The server will handle initialization.
            self.session_id = str(uuid.uuid4())
            self.initialized = True
            print(f"✅ MCP SSE client ready for Topcoder server")
            return True
                        
        except Exception as e:
            print(f"❌ MCP initialization error: {str(e)}")
        
        print("📚 Using educational fallback content")
        return False
    
    async def _make_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a tool call to the MCP server using SSE transport"""
        if not await self.initialize_session():
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/json'
                }
                
                # Build payload matching the Inspector format
                payload = {
                    "jsonrpc": "2.0",
                    "id": int(time.time()),  # Use timestamp as ID
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": self._format_arguments_for_mcp(tool_name, arguments),
                        "_meta": {
                            "progressToken": int(time.time()) % 1000
                        }
                    }
                }
                
                print(f"📤 Sending MCP request: {tool_name} with args: {arguments}")
                
                async with session.post(self.sse_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        print(f"📥 MCP response ({len(response_text)} chars): {response_text[:200]}...")
                        
                        try:
                            data = json.loads(response_text)
                            if 'result' in data and 'content' in data['result']:
                                content = data['result']['content']
                                if isinstance(content, list) and len(content) > 0:
                                    text_content = content[0].get('text', '')
                                    try:
                                        return json.loads(text_content)
                                    except json.JSONDecodeError:
                                        return {'raw_response': text_content}
                            elif 'result' in data:
                                return data['result']
                            else:
                                return {'raw_response': response_text}
                        except json.JSONDecodeError:
                            return {'raw_response': response_text}
                    else:
                        error_text = await response.text()
                        print(f"❌ MCP call failed: {response.status} - {error_text[:200]}...")
                        
        except Exception as e:
            print(f"❌ MCP call error: {str(e)}")
        
        return None
    
    def _format_arguments_for_mcp(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Format arguments to match the Inspector's format"""
        if tool_name == "query-tc-skills":
            # Convert category to name array format
            category = arguments.get('category', 'algorithms')
            return {
                "name": [category],  # Convert to array format
                "skillId": [],
                "page": 1,
                "perPage": 20
            }
        elif tool_name == "query-tc-challenges":
            # Format challenges arguments
            difficulty = arguments.get('difficulty', 'easy')
            return {
                "difficulty": difficulty,
                "page": 1,
                "perPage": 20
            }
        else:
            return arguments
    
    async def get_challenges(self, difficulty: str = "easy", limit: int = 5) -> Optional[Dict[str, Any]]:
        """Get challenges from MCP server"""
        print(f"🔄 Fetching {difficulty} challenges from Topcoder MCP...")
        return await self._make_tool_call("query-tc-challenges", {
            "difficulty": difficulty
        })
    
    async def get_skills(self, category: str = "algorithms", limit: int = 10) -> Optional[Dict[str, Any]]:
        """Get skills from MCP server"""
        print(f"🔄 Fetching {category} skills from Topcoder MCP...")
        return await self._make_tool_call("query-tc-skills", {
            "category": category
        })

# Initialize MCP client
mcp_client = None
if MCP_SESSION_TOKEN:
    mcp_client = MCPClient(MCP_SESSION_TOKEN)

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
                mcp_data = await mcp_client.get_challenges(difficulty, 5)
                if mcp_data:
                    # Handle different response formats
                    if 'challenges' in mcp_data:
                        challenges = mcp_data['challenges']
                    elif isinstance(mcp_data, dict) and 'raw_response' in mcp_data:
                        # Parse raw response if needed
                        try:
                            parsed_data = json.loads(mcp_data['raw_response'])
                            challenges = parsed_data.get('challenges', [])
                        except:
                            challenges = []
                    else:
                        challenges = []
                    
                    if challenges:
                        self.available_challenges = challenges
                        display_text = self._format_mcp_challenges({'challenges': challenges}, difficulty)
                        print(f"✅ Loaded {len(challenges)} challenges from Topcoder MCP")
                        return display_text, challenges
            except Exception as e:
                print(f"MCP request failed: {e}")
        
        # Use educational fallback content
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
                },
                {
                    "id": "binary-tree-traversal",
                    "name": "Binary Tree Level Order Traversal",
                    "description": "Return the level order traversal of a binary tree's nodes' values.",
                    "skills": ["BFS", "Queue data structure", "Trees"],
                    "difficulty": "medium",
                    "examples": [
                        {"input": "[3,9,20,null,null,15,7]", "output": "[[3],[9,20],[15,7]]"}
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
                },
                {
                    "id": "n-queens",
                    "name": "N-Queens Problem",
                    "description": "Place N queens on an N×N chessboard so that no two queens attack each other.",
                    "skills": ["Backtracking", "Constraint satisfaction"],
                    "difficulty": "hard",
                    "examples": [
                        {"input": "4", "output": "2 solutions"}
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
    
    async def get_skills(self, category: str = "algorithms") -> str:
        """Get skills data with fallback content"""
        # Validate input
        valid_categories = ['algorithms', 'data-structures', 'dynamic-programming', 'graphs']
        if category not in valid_categories:
            category = 'algorithms'
        
        # Try MCP first if available
        if mcp_client:
            try:
                mcp_data = await mcp_client.get_skills(category, 10)
                if mcp_data:
                    # Handle different response formats
                    if 'skills' in mcp_data:
                        skills = mcp_data['skills']
                    elif isinstance(mcp_data, dict) and 'raw_response' in mcp_data:
                        # Parse raw response if needed
                        try:
                            parsed_data = json.loads(mcp_data['raw_response'])
                            skills = parsed_data.get('skills', [])
                        except:
                            skills = []
                    else:
                        skills = []
                    
                    if skills:
                        print(f"✅ Loaded {len(skills)} skills from Topcoder MCP")
                        return self._format_mcp_skills({'skills': skills}, category)
            except Exception as e:
                print(f"MCP request failed: {e}")
        
        # Use educational fallback content
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
        return f"## 🛠️ Recommended {category.title()} Skills to Practice\n\n" + "\n".join(f"• {skill}" for skill in skills)
    
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
        .accordion { margin-bottom: 1rem; border: 1px solid #e2e8f0; border-radius: 8px; }
        .accordion summary { padding: 0.5rem; font-weight: 600; cursor: pointer; }
        .accordion[open] { border-color: #667eea; }
        """
    ) as interface:
        
        # Header
        gr.Markdown("""
        # 🎓 Professor Al Gorithm
        ## Learn Algorithm Design Canvas Methodology with Educational Challenges
        
        Master problem-solving through our structured 4-phase approach: **Constraints → Ideas → Tests → Code**
        
        *Note: MCP integration ready for when Topcoder server issues are resolved*
        """, elem_classes=["phase-header"])
        
        with gr.Row():
            with gr.Column(scale=1):
                # Challenge Library Accordion
                with gr.Accordion("📚 Challenge Library", open=True) as challenge_library_accordion:
                    difficulty_select = gr.Dropdown(
                        choices=["easy", "medium", "hard"],
                        value="easy",
                        label="Difficulty Level"
                    )
                    get_challenges_btn = gr.Button("🎯 Get New Challenges", variant="primary")
                    challenges_display = gr.Markdown("Click 'Get New Challenges' to start!")
                
                # Challenge Selection Accordion
                with gr.Accordion("🎯 Select Your Challenge", open=False) as challenge_selection_accordion:
                    challenge_selector = gr.Radio(
                        choices=[],
                        label="Choose a challenge to work on:",
                        visible=False
                    )
                    select_challenge_btn = gr.Button("📝 Select This Challenge", visible=False)
                    challenge_status = gr.Markdown("")
                
                # Skills Recommendations Accordion
                with gr.Accordion("🛠️ Skills to Practice", open=False) as skills_accordion:
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
        
        # Status and Progress
        with gr.Row():
            status_display = gr.Markdown(
                """**Status:** Ready to start learning! 🚀  
                **System:** Professor Al Gorithm Educational Platform
                
                💡 **Tips:**
                - Start with an easy challenge to warm up
                - Follow the 4-phase Canvas approach: Constraints → Ideas → Tests → Code  
                - Take your time with each phase - learning is more important than speed!
                
                🔧 **MCP Integration:** Ready for when Topcoder server is available
                """
            )
        
        # Event handlers
        async def fetch_challenges(difficulty):
            try:
                if not difficulty:
                    return ("❌ Please select a difficulty level first.", gr.update(visible=False), 
                           gr.update(visible=False), gr.update(value=""), gr.update(open=True), gr.update(open=False))
                    
                display_text, challenges = await professor.get_challenges(difficulty)
                
                # Create radio button choices
                radio_choices = [f"{i}. {challenge['name']}" for i, challenge in enumerate(challenges, 1)]
                
                return (
                    display_text,
                    gr.update(choices=radio_choices, visible=True, value=None),
                    gr.update(visible=True),
                    gr.update(value=""),
                    gr.update(open=False),  # Close the challenge library accordion
                    gr.update(open=True)    # Open the challenge selection accordion
                )
            except Exception as e:
                print(f"Error in fetch_challenges: {e}")
                fallback_text = "❌ Error loading challenges. Please try again."
                return (fallback_text, gr.update(visible=False), gr.update(visible=False), 
                       gr.update(value=""), gr.update(open=True), gr.update(open=False))
        
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
                    return "❌ Please select a challenge first.", gr.update(open=False), gr.update(open=True)
                
                # Extract challenge number from selection (e.g., "1. Two Sum Problem" -> 1)
                challenge_num = int(selected_challenge.split('.')[0])
                result = professor.select_challenge(challenge_num)
                
                # Close challenge selection accordion and open skills accordion
                return result, gr.update(open=False), gr.update(open=True)
            except Exception as e:
                print(f"Error in select_challenge_handler: {e}")
                return f"❌ Error selecting challenge: {str(e)}", gr.update(open=True), gr.update(open=False)

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
        
        # Connect buttons to functions
        get_challenges_btn.click(
            fn=fetch_challenges,
            inputs=[difficulty_select],
            outputs=[challenges_display, challenge_selector, select_challenge_btn, challenge_status, challenge_library_accordion, challenge_selection_accordion],
            show_progress="full",
            scroll_to_output=True
        )
        
        select_challenge_btn.click(
            fn=select_challenge_handler,
            inputs=[challenge_selector],
            outputs=[challenge_status, challenge_selection_accordion, skills_accordion],
            show_progress="minimal",
            scroll_to_output=True
        )
        
        get_skills_btn.click(
            fn=fetch_skills,
            inputs=[category_select],
            outputs=[skills_display],
            show_progress="full",
            scroll_to_output=True
        )
        
        # Canvas phase guidance
        constraints_btn.click(
            fn=lambda inp: guide_phase("constraints", inp),
            inputs=[constraints_input],
            outputs=[constraints_output],
            show_progress="minimal",
            scroll_to_output=True
        )
        
        ideas_btn.click(
            fn=lambda inp: guide_phase("ideas", inp),
            inputs=[ideas_input],
            outputs=[ideas_output],
            show_progress="minimal",
            scroll_to_output=True
        )
        
        tests_btn.click(
            fn=lambda inp: guide_phase("tests", inp),
            inputs=[tests_input],
            outputs=[tests_output],
            show_progress="minimal",
            scroll_to_output=True
        )
        
        code_btn.click(
            fn=lambda inp: guide_phase("code", inp),
            inputs=[code_input],
            outputs=[code_output],
            show_progress="minimal",
            scroll_to_output=True
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