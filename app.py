#!/usr/bin/env python3
"""
Professor Al Gorithm - AI Agent for Teaching Algorithm Design Canvas Methodology
Gradio interface for the educational AI agent that integrates with Topcoder MCP server
"""

import gradio as gr
import requests
import json
import os
from typing import Dict, Any, Optional, Tuple
import asyncio
import aiohttp

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")

class ProfessorAlGorithm:
    """Main class for the Professor Al Gorithm AI agent interface"""
    
    def __init__(self):
        self.current_phase = "constraints"
        self.session_data = {}
    
    async def get_challenges(self, difficulty: str = "easy") -> str:
        """Fetch coding challenges from MCP server via backend"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/challenges",
                    json={"difficulty": difficulty},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_challenges_for_display(data)
                    else:
                        return f"Error fetching challenges: {response.status}"
        except Exception as e:
            return f"Connection error: {str(e)}\n\nFallback: Here's a sample algorithm problem to get started:\n\n**Two Sum Problem**\nGiven an array of integers and a target sum, find two numbers that add up to the target."
    
    async def get_skills(self, category: str = "algorithms") -> str:
        """Fetch skills data from MCP server via backend"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/skills",
                    json={"category": category},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_skills_for_display(data)
                    else:
                        return f"Error fetching skills: {response.status}"
        except Exception as e:
            return f"Connection error: {str(e)}\n\nFallback: Focus on these core algorithm skills:\n- Array manipulation\n- Two pointers technique\n- Hash tables\n- Recursion basics"
    
    def _format_challenges_for_display(self, data: Dict[str, Any]) -> str:
        """Format challenge data for educational display"""
        if not data or 'challenges' not in data:
            return "No challenges available"
        
        formatted = "## Available Coding Challenges\n\n"
        for challenge in data['challenges'][:3]:  # Show top 3
            formatted += f"**{challenge.get('name', 'Unknown Challenge')}**\n"
            formatted += f"Difficulty: {challenge.get('difficulty', 'Unknown')}\n"
            formatted += f"Description: {challenge.get('description', 'No description available')}\n\n"
        
        return formatted
    
    def _format_skills_for_display(self, data: Dict[str, Any]) -> str:
        """Format skills data for educational display"""
        if not data or 'skills' not in data:
            return "No skills data available"
        
        formatted = "## Recommended Skills to Practice\n\n"
        for skill in data['skills'][:5]:  # Show top 5
            formatted += f"• **{skill.get('name', 'Unknown Skill')}**\n"
            formatted += f"  Category: {skill.get('category', 'Unknown')}\n"
            formatted += f"  Level: {skill.get('level', 'Unknown')}\n\n"
        
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
        
        # Status and Progress
        with gr.Row():
            status_display = gr.Markdown("**Status:** Ready to start learning! 🚀")
        
        # Event handlers
        async def fetch_challenges(difficulty):
            return await professor.get_challenges(difficulty)
        
        async def fetch_skills(category):
            return await professor.get_skills(category)
        
        def guide_phase(phase, user_input):
            return professor.guide_canvas_phase(phase, user_input)
        
        # Connect buttons to functions with loading states
        get_challenges_btn.click(
            fn=fetch_challenges,
            inputs=[difficulty_select],
            outputs=[challenges_display],
            show_progress="full"
        )
        
        get_skills_btn.click(
            fn=fetch_skills,
            inputs=[category_select],
            outputs=[skills_display],
            show_progress="full"
        )
        
        # Canvas phase guidance with progress indicators
        constraints_btn.click(
            fn=lambda inp: guide_phase("constraints", inp),
            inputs=[constraints_input],
            outputs=[constraints_output],
            show_progress="minimal"
        )
        
        ideas_btn.click(
            fn=lambda inp: guide_phase("ideas", inp),
            inputs=[ideas_input],
            outputs=[ideas_output],
            show_progress="minimal"
        )
        
        tests_btn.click(
            fn=lambda inp: guide_phase("tests", inp),
            inputs=[tests_input],
            outputs=[tests_output],
            show_progress="minimal"
        )
        
        code_btn.click(
            fn=lambda inp: guide_phase("code", inp),
            inputs=[code_input],
            outputs=[code_output],
            show_progress="minimal"
        )
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    app = create_gradio_interface()
    
    # Launch configuration for Hugging Face Spaces
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )