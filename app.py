#!/usr/bin/env python3
"""
Professor Al Gorithm - AI Agent for Teaching Algorithm Design Canvas Methodology
Context-aware teaching assistant that helps users work through any coding challenge
"""

import gradio as gr
import re
import os
from typing import Dict, Any, Optional, Tuple
import time

print("🎓 Professor Al Gorithm starting...")
print("🧠 Context-aware professor ready to help with any coding challenge!")

class ProfessorAlGorithm:
    """Main class for the Professor Al Gorithm AI agent interface"""
    
    def __init__(self):
        self.current_phase = "constraints"
        self.session_data = {}
        self.challenge_title = ""
        self.challenge_description = ""
        self.challenge_set = False
    
    def set_challenge(self, title: str, description: str) -> str:
        """Set the current challenge title and description"""
        if not title or not title.strip():
            return "❌ Please provide a challenge title."
        
        if not description or not description.strip():
            return "❌ Please provide a challenge description."
        
        # Clean and store challenge details
        self.challenge_title = title.strip()
        self.challenge_description = description.strip()
        self.challenge_set = True
        self.current_phase = "constraints"
        
        return f"""## ✅ Challenge Set Successfully!
        
**Title:** {self.challenge_title}

**Description:** {self.challenge_description}

🎨 **Ready for Algorithm Design Canvas!**
Now work through each phase step by step:

1️⃣ **Constraints** - Define input/output format, edge cases, and performance requirements
2️⃣ **Ideas** - Brainstorm different solution approaches and algorithms  
3️⃣ **Tests** - Design comprehensive test cases to validate your solution
4️⃣ **Code** - Structure and plan your implementation

Click on the **Constraints** tab to begin!"""
    
    def _analyze_challenge_context(self) -> Dict[str, Any]:
        """Analyze the challenge title and description to provide intelligent context"""
        if not self.challenge_set:
            return {}
        
        title_lower = self.challenge_title.lower()
        desc_lower = self.challenge_description.lower()
        combined_text = f"{title_lower} {desc_lower}"
        
        # Pattern detection for intelligent guidance
        patterns = {
            'data_structures': {
                'array': ['array', 'list', 'elements', 'index', 'sort'],
                'string': ['string', 'text', 'character', 'substring', 'palindrome'],
                'tree': ['tree', 'binary', 'node', 'leaf', 'root', 'traversal'],
                'graph': ['graph', 'vertex', 'edge', 'path', 'connected', 'bfs', 'dfs'],
                'stack': ['stack', 'lifo', 'push', 'pop', 'parentheses', 'bracket'],
                'queue': ['queue', 'fifo', 'dequeue', 'level order'],
                'hash': ['hash', 'map', 'dictionary', 'lookup', 'count', 'frequency'],
                'linked_list': ['linked', 'node', 'next', 'pointer', 'merge']
            },
            'algorithms': {
                'sorting': ['sort', 'order', 'arrange', 'merge', 'quick'],
                'searching': ['search', 'find', 'binary search', 'target'],
                'two_pointers': ['two pointer', 'left', 'right', 'pair', 'sum'],
                'sliding_window': ['window', 'subarray', 'substring', 'contiguous'],
                'dynamic_programming': ['optimal', 'maximum', 'minimum', 'dp', 'fibonacci', 'knapsack'],
                'backtracking': ['backtrack', 'permutation', 'combination', 'generate', 'all possible'],
                'greedy': ['greedy', 'minimum', 'maximum', 'optimal choice']
            },
            'complexity_hints': {
                'time_critical': ['o(n)', 'o(log n)', 'efficient', 'fast', 'optimal time'],
                'space_critical': ['in-place', 'constant space', 'o(1) space', 'memory efficient']
            }
        }
        
        detected_patterns = []
        suggested_approaches = []
        
        # Detect patterns in the challenge
        for category, subcategories in patterns.items():
            for pattern_name, keywords in subcategories.items():
                if any(keyword in combined_text for keyword in keywords):
                    detected_patterns.append({
                        'category': category,
                        'pattern': pattern_name,
                        'keywords_found': [kw for kw in keywords if kw in combined_text]
                    })
        
        # Generate approach suggestions based on detected patterns
        approach_map = {
            'array': ['Two pointers', 'Sliding window', 'Hash map for lookups'],
            'string': ['Two pointers', 'String manipulation', 'Character frequency counting'],
            'tree': ['Tree traversal (DFS/BFS)', 'Recursive solutions', 'Level-order processing'],
            'graph': ['BFS for shortest path', 'DFS for connectivity', 'Topological sort'],
            'sorting': ['Merge sort', 'Quick sort', 'Built-in sorting'],
            'searching': ['Binary search', 'Hash table lookup', 'Linear scan'],
            'dynamic_programming': ['Memoization (top-down)', 'Tabulation (bottom-up)', 'State optimization']
        }
        
        for pattern in detected_patterns:
            if pattern['pattern'] in approach_map:
                suggested_approaches.extend(approach_map[pattern['pattern']])
        
        return {
            'detected_patterns': detected_patterns,
            'suggested_approaches': list(set(suggested_approaches)),
            'challenge_complexity': self._estimate_complexity(combined_text)
        }
    
    def _estimate_complexity(self, text: str) -> str:
        """Estimate challenge complexity based on description"""
        complexity_indicators = {
            'easy': ['simple', 'basic', 'straightforward', 'easy', 'find', 'check'],
            'medium': ['optimal', 'efficient', 'multiple', 'various', 'complex'],
            'hard': ['minimum', 'maximum', 'all possible', 'optimize', 'constraint', 'advanced']
        }
        
        scores = {'easy': 0, 'medium': 0, 'hard': 0}
        
        for level, keywords in complexity_indicators.items():
            for keyword in keywords:
                if keyword in text:
                    scores[level] += 1
        
        return max(scores.keys(), key=lambda k: scores[k])
    
    def _get_context_specific_guidance(self, phase: str, context: Dict[str, Any]) -> str:
        """Generate phase-specific guidance based on detected patterns"""
        if not context.get('detected_patterns'):
            return ""
        
        phase_specific_tips = {
            'constraints': {
                'array': '- Consider array bounds, negative indices, and empty arrays',
                'string': '- Think about string length, character encoding, and empty strings',
                'tree': '- Consider null nodes, tree height, and balanced vs unbalanced trees',
                'graph': '- Think about disconnected components, cycles, and node/edge counts',
                'dynamic_programming': '- Define the state space and identify overlapping subproblems'
            },
            'ideas': {
                'array': '- Two pointers, sliding window, or prefix sums might be useful',
                'string': '- Consider character frequency, substring matching, or string building',
                'tree': '- Tree traversal (DFS/BFS) or divide-and-conquer approaches',
                'graph': '- BFS for shortest paths, DFS for connectivity, topological sort',
                'dynamic_programming': '- Memoization (top-down) or tabulation (bottom-up)'
            },
            'tests': {
                'array': '- Test with empty arrays, single elements, and sorted/unsorted data',
                'string': '- Test with empty strings, single characters, and special characters',
                'tree': '- Test with null trees, single nodes, and deeply nested trees',
                'graph': '- Test with single nodes, disconnected graphs, and cyclic graphs',
                'dynamic_programming': '- Test base cases and optimal substructure properties'
            },
            'code': {
                'array': '- Use clear variable names for indices and consider boundary checks',
                'string': '- Plan string manipulation carefully to avoid index errors',
                'tree': '- Handle null checks and consider recursive vs iterative approaches',
                'graph': '- Choose appropriate graph representation (adjacency list/matrix)',
                'dynamic_programming': '- Initialize your DP table/memo properly'
            }
        }
        
        tips = []
        for pattern in context['detected_patterns'][:2]:  # Top 2 patterns
            pattern_name = pattern['pattern']
            if pattern_name in phase_specific_tips.get(phase, {}):
                tips.append(phase_specific_tips[phase][pattern_name])
        
        if tips:
            return f"\n**🎯 Context-Specific Tips:**\n" + "\n".join(tips)
        return ""
    
    def guide_canvas_phase(self, phase: str, user_input: str) -> Tuple[str, str]:
        """Guide user through Algorithm Design Canvas phases with context awareness"""
        
        if not self.challenge_set:
            return "❌ Please set a challenge first using the form above.", phase
        
        # Get intelligent challenge analysis
        context = self._analyze_challenge_context()
        
        # Build challenge context section
        challenge_context = f"\n\n**📋 Current Challenge: {self.challenge_title}**\n"
        challenge_context += f"*{self.challenge_description}*\n"
        
        # Add AI-detected patterns and suggestions
        if context.get('detected_patterns'):
            patterns_text = []
            for pattern in context['detected_patterns'][:3]:  # Top 3 patterns
                pattern_name = pattern['pattern'].replace('_', ' ').title()
                patterns_text.append(pattern_name)
            challenge_context += f"*🧠 AI Detected: {', '.join(patterns_text)} patterns*\n"
        
        if context.get('suggested_approaches'):
            challenge_context += f"*💡 Suggested Approaches: {', '.join(context['suggested_approaches'][:3])}*\n"
        
        phase_guidance = {
            "constraints": {
                "title": "Phase 1: Define Constraints",
                "guidance": f"""Let's analyze the constraints for your challenge:{challenge_context}

🔍 **Key Questions to Consider:**

1. **Input Format**: What type of data are you working with?
   - What data structures are involved? 
   - What are the input ranges or limits?
   - Are there any implicit constraints in the description?

2. **Output Format**: What should your solution return?
   - Exact format required?
   - Any specific data type?

3. **Performance Requirements**: Are there time/space complexity hints?
   - How many elements might you process?
   - Any efficiency requirements mentioned?

4. **Edge Cases**: What special scenarios should you handle?
   - Empty inputs, single elements?
   - Minimum/maximum values, boundary conditions?

{self._get_context_specific_guidance(phase, context)}

💡 **Your Task**: Analyze the challenge and define the constraints clearly. Consider both explicit and implicit requirements."""
            },
            "ideas": {
                "title": "Phase 2: Brainstorm Solution Ideas", 
                "guidance": f"""Let's explore different approaches for your challenge:{challenge_context}

🧠 **Brainstorming Framework:**

1. **Brute Force**: What's the most straightforward solution?
   - How would you solve this step by step manually?
   - Don't worry about efficiency yet!

2. **Pattern Recognition**: What algorithmic patterns might apply?
   {f"- AI suggests considering: {', '.join(context['suggested_approaches'])}" if context.get('suggested_approaches') else ""}
   
3. **Data Structure Selection**: What structures could help?
   - Based on your challenge, consider the detected patterns above
   
4. **Optimization Opportunities**: Can we improve time/space complexity?
   - What's the bottleneck in the brute force approach?
   - Which algorithms or data structures could optimize this?

{self._get_context_specific_guidance(phase, context)}

💡 **Your Task**: Share your solution ideas and I'll help you evaluate them based on the challenge context!"""
            },
            "tests": {
                "title": "Phase 3: Design Test Cases",
                "guidance": f"""Let's create comprehensive test scenarios for your challenge:{challenge_context}

🧪 **Testing Strategy:**

1. **Basic Cases**: Start with simple, expected inputs
   - What's the most straightforward example?
   - Test your main logic path

2. **Edge Cases**: What boundary conditions exist?
   - Empty inputs, single elements
   - Minimum/maximum values
   - Zero, negative numbers (if applicable)

3. **Corner Cases**: Unusual but valid scenarios
   - What tricky inputs might break your solution?
   - Consider the edge cases specific to your detected patterns

4. **Invalid Cases**: How should your solution handle bad input?
   - Null inputs, wrong data types
   - Out-of-bounds values

{self._get_context_specific_guidance(phase, context)}

💡 **Your Task**: Design test cases that thoroughly validate your solution across all scenarios!"""
            },
            "code": {
                "title": "Phase 4: Structure Your Code",
                "guidance": f"""Time to organize your implementation:{challenge_context}

👩‍💻 **Implementation Planning:**

1. **Function Signature**: Define your main function
   - What parameters does it need based on your constraints?
   - What should it return?

2. **Algorithm Steps**: Break down your chosen approach
   - List the main steps in order
   - Identify the core logic and any helper operations

3. **Data Structures**: Based on your brainstorming
   - What structures will you use for efficiency?
   - Any temporary storage needed?

4. **Implementation Strategy**: Step-by-step coding approach
   - Which part will you implement first?
   - How will you test incrementally?

{self._get_context_specific_guidance(phase, context)}

💡 **Remember**: Focus on clean, readable code that handles your identified constraints and edge cases!"""
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
        .challenge-input { background: #f8fafc; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
        """
    ) as interface:
        
        # Header
        gr.Markdown("""
        # 🎓 Professor Al Gorithm
        ## AI-Powered Algorithm Design Canvas Assistant
        
        Master problem-solving through our structured 4-phase approach: **Constraints → Ideas → Tests → Code**
        
        🧠 **Intelligent Context Analysis**: Enter any coding challenge and get personalized guidance based on detected patterns!
        """, elem_classes=["phase-header"])
        
        with gr.Row():
            with gr.Column(scale=1):
                # Challenge Input Section  
                gr.Markdown("## 📝 Enter Your Challenge", elem_classes=["challenge-input"])
                
                challenge_title = gr.Textbox(
                    label="Challenge Title",
                    placeholder="e.g., Two Sum, Binary Tree Traversal, Maximum Subarray...",
                    info="Enter a descriptive title for your coding challenge"
                )
                
                challenge_description = gr.Textbox(
                    label="Challenge Description", 
                    placeholder="Describe the problem you want to solve. Include input/output format, constraints, and any examples...",
                    lines=5,
                    info="The more detail you provide, the better guidance the AI professor can give!"
                )
                
                set_challenge_btn = gr.Button("🎯 Set Challenge & Start Learning!", variant="primary", size="lg")
                challenge_status = gr.Markdown("### 🎨 Algorithm Design Canvas\n*Enter a challenge above to begin!*")
            
            with gr.Column(scale=2):
                # Algorithm Design Canvas
                phase_tabs = gr.Tabs()
                with phase_tabs:
                    with gr.TabItem("1️⃣ Constraints", id="constraints"):
                        constraints_input = gr.Textbox(
                            label="Define your problem constraints",
                            placeholder="Analyze input/output format, edge cases, performance requirements...",
                            lines=4,
                            info="Think about data types, ranges, edge cases, and complexity requirements"
                        )
                        constraints_output = gr.Markdown("*Set a challenge first to receive intelligent guidance*")
                        constraints_btn = gr.Button("🔍 Get AI Guidance on Constraints")
                    
                    with gr.TabItem("2️⃣ Ideas", id="ideas"):
                        ideas_input = gr.Textbox(
                            label="Share your solution approaches",
                            placeholder="What solution strategies are you considering?",
                            lines=4,
                            info="Brainstorm different algorithms, data structures, and optimization approaches"
                        )
                        ideas_output = gr.Markdown("*Set a challenge first to receive intelligent guidance*")
                        ideas_btn = gr.Button("🧠 Get AI Help with Solution Ideas")
                    
                    with gr.TabItem("3️⃣ Test Cases", id="tests"):
                        tests_input = gr.Textbox(
                            label="Design comprehensive test cases", 
                            placeholder="What test scenarios should you consider?",
                            lines=4,
                            info="Include basic cases, edge cases, corner cases, and invalid inputs"
                        )
                        tests_output = gr.Markdown("*Set a challenge first to receive intelligent guidance*")
                        tests_btn = gr.Button("🧪 Get AI Help with Test Design")
                    
                    with gr.TabItem("4️⃣ Code Structure", id="code"):
                        code_input = gr.Textbox(
                            label="Plan your implementation structure",
                            placeholder="How will you organize and structure your code?",
                            lines=4,
                            info="Think about function signatures, algorithm steps, and implementation strategy"
                        )
                        code_output = gr.Markdown("*Set a challenge first to receive intelligent guidance*")
                        code_btn = gr.Button("👩‍💻 Get AI Implementation Guidance")
        
        # Status and Progress
        with gr.Row():
            status_display = gr.Markdown(
                """**Status:** Ready to learn with any coding challenge! 🚀  
                **System:** AI-Powered Professor Al Gorithm
                
                💡 **How it works:**
                1. Enter any coding challenge title and description
                2. The AI professor analyzes patterns and provides context-aware guidance  
                3. Work through the 4-phase Canvas: **Constraints → Ideas → Tests → Code**
                4. Get intelligent, personalized help at each step!
                
                🧠 **AI Features:** Pattern detection, complexity analysis, approach suggestions, and phase-specific tips
                """
            )
        
        # Event handlers
        def set_challenge_handler(title, description):
            try:
                return professor.set_challenge(title, description)
            except Exception as e:
                print(f"Error in set_challenge_handler: {e}")
                return f"❌ Error setting challenge: {str(e)}"

        def guide_phase(phase, user_input):
            try:
                if not user_input or not user_input.strip():
                    return f"Please provide some input for the {phase} phase to get AI guidance.", phase
                    
                if len(user_input.strip()) < 10:
                    return f"Please provide more detailed input for the {phase} phase (at least 10 characters).", phase
                    
                return professor.guide_canvas_phase(phase, user_input.strip())
            except Exception as e:
                print(f"Error in guide_phase: {e}")
                return f"❌ Error processing your input: {str(e)}\n\nPlease try again with your {phase} phase input.", phase
        
        # Connect buttons to functions
        set_challenge_btn.click(
            fn=set_challenge_handler,
            inputs=[challenge_title, challenge_description],
            outputs=[challenge_status],
            show_progress="minimal",
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