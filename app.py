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
import requests
import json
import os
from typing import Dict, Any, Optional, Tuple
import asyncio
import aiohttp
import time

# Configuration - Force 127.0.0.1 for Hugging Face Spaces
BACKEND_URL = "http://127.0.0.1:3000"  # Force this for now
print(f"🔗 Backend URL configured as: {BACKEND_URL}")
print(f"🌍 Environment variables: SPACE_ID={os.getenv('SPACE_ID', 'None')}, GRADIO_SERVER_NAME={os.getenv('GRADIO_SERVER_NAME', 'None')}")

class ProfessorAlGorithm:
    """Main class for the Professor Al Gorithm AI agent interface"""
    
    def __init__(self):
        self.current_phase = "constraints"
        self.session_data = {}
    
    async def get_challenges(self, difficulty: str = "easy") -> str:
        """Fetch coding challenges from MCP server via backend with retry logic"""
        try:
            # Validate input
            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'easy'
                
            # Retry logic for Hugging Face Spaces startup
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=30)  # Reduced timeout per attempt
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(
                            f"{BACKEND_URL}/api/challenges",
                            json={"difficulty": difficulty, "limit": 5},
                            headers={'Content-Type': 'application/json'}
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                return self._format_challenges_for_display(data)
                            elif response.status == 400:
                                error_data = await response.json() if response.content_type == 'application/json' else {}
                                return f"Invalid request: {error_data.get('error', 'Bad request')}"
                            elif response.status == 408:
                                return "⏰ Request timed out. The system may be busy. Please try again in a moment."
                            elif response.status >= 500:
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(2)  # Wait before retry
                                    continue
                                return "🔧 Server is temporarily unavailable. Using fallback challenges...\n\n" + self._get_fallback_challenges()
                            else:
                                return f"Unexpected error (Status {response.status}). Using fallback challenges...\n\n" + self._get_fallback_challenges()
                                
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt < max_retries - 1:
                        print(f"Connection attempt {attempt + 1} failed: {e}. Retrying...")
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    else:
                        print(f"❌ Backend connection failed completely: {str(e)}")
                        print(f"🔗 Attempted to connect to: {BACKEND_URL}")
                        return f"🔧 Backend service unavailable. Using offline mode.\n\n" + self._get_fallback_challenges()
                        
        except Exception as e:
            print(f"Unexpected error in get_challenges: {e}")  # Log for debugging
            return "❌ An unexpected error occurred. Using fallback challenges...\n\n" + self._get_fallback_challenges()
    
    def _get_fallback_challenges(self) -> str:
        """Provide fallback challenges when MCP is unavailable"""
        return """## Sample Coding Challenges

**🎯 Two Sum Problem**
Difficulty: Easy
Description: Given an array of integers and a target sum, find two numbers that add up to the target.

**🎯 Valid Parentheses**
Difficulty: Easy  
Description: Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

**🎯 Maximum Subarray**
Difficulty: Medium
Description: Find the contiguous subarray within a one-dimensional array of numbers that has the largest sum.

💡 **Pro Tip**: Start with the easiest problem and work your way up!"""
    
    async def get_skills(self, category: str = "algorithms") -> str:
        """Fetch skills data from MCP server via backend with retry logic"""
        try:
            # Validate input
            valid_categories = ['algorithms', 'data-structures', 'dynamic-programming', 'graphs']
            if category not in valid_categories:
                category = 'algorithms'
                
            # Retry logic for Hugging Face Spaces startup
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=30)  # Reduced timeout per attempt
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(
                            f"{BACKEND_URL}/api/skills",
                            json={"category": category, "limit": 10},
                            headers={'Content-Type': 'application/json'}
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                return self._format_skills_for_display(data)
                            elif response.status == 400:
                                error_data = await response.json() if response.content_type == 'application/json' else {}
                                return f"Invalid request: {error_data.get('error', 'Bad request')}"
                            elif response.status == 408:
                                return "⏰ Request timed out. The system may be busy. Please try again in a moment."
                            elif response.status >= 500:
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(2)  # Wait before retry
                                    continue
                                return "🔧 Server is temporarily unavailable. Using fallback skills...\n\n" + self._get_fallback_skills(category)
                            else:
                                return f"Unexpected error (Status {response.status}). Using fallback skills...\n\n" + self._get_fallback_skills(category)
                                
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt < max_retries - 1:
                        print(f"Connection attempt {attempt + 1} failed: {e}. Retrying...")
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    else:
                        print(f"❌ Backend connection failed completely: {str(e)}")
                        print(f"🔗 Attempted to connect to: {BACKEND_URL}")
                        return f"🔧 Backend service unavailable. Using offline mode.\n\n" + self._get_fallback_skills(category)
                        
        except Exception as e:
            print(f"Unexpected error in get_skills: {e}")  # Log for debugging
            return "❌ An unexpected error occurred. Using fallback skills...\n\n" + self._get_fallback_skills(category)
    
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