# Professor Al Gorithm - Virtual Data Structure and Algorithm Tutor

This is based off of the Topcoder challenge - [Learn AI – Build and Deploy an AI Agent with Topcoder MCP on Hugging Face](https://www.topcoder.com/challenges/355a5497-71c3-4e3a-b200-f53d62564667?tab=details) and [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course/unit0/introduction#welcome-to-the--model-context-protocol-mcp-course)

AI agent that helps guide you through solving a coding problem following the [Algorithm Design Canvas](https://www.hiredintech.com/algorithms/algorithm-design-canvas/what-is-the-canvas/). The professor will guide you through the steps to solve the problem as if you were doing a whiteboard coding interview. The steps taken will be based on:

- Constraints
- Ideas
- Test Cases
- Code

The professor will not supply you any code throughout the process. No matter what language you are using, the professor will guide you through the steps to solve the problem. The professor will not write any code for you, but will help you think through the problem and come up with a solution. Rather than give you the code, you will be taught how to write it yourself.

## The Model Context Protocol

What the professor needs to perform:

- Maintain **step-by-step structure** (Constraints -> Ideas -> Test Cases -> Code).
- Enforce a **teaching style** (e.g., Socratic questioning, no code-writing).
- Remember **prior answers**, like constraints already gathered or test cases discussed.
- Adapt to **user skill level or struggle** (e.g., repeat steps, prompt hints).

### Key MCP Elements

#### System Instructions (Agent Persona)

The tone, rules, and scope of the professor's responses. This includes:

```yaml
system_instruction:
  - You are a professor teaching algorithms for whiteboard interviews.
  - Your role is to guide students through problem solving using the Algorithm Design Canvas.
  - You never write code; instead, ask questions, guide thinking, and help the student formulate their own solution.
  - You are structured and Socratic. Always ask follow-up questions before revealing too much.
  - You follow the steps: Constraints → Ideas → Test Cases → Code Structure.
```

#### Structured Workflow via Steps

The MCP stages based on the canvas:

```yaml
context_stages:
  - name: constraints
    goal: Help the user define all important input/output constraints, performance needs, and edge cases.

  - name: ideas
    goal: Brainstorm candidate strategies based on constraints. Ask guided questions about brute force, optimizations, etc.

  - name: test_cases
    goal: Help the user construct meaningful test cases to validate their ideas, including edge cases and big inputs.

  - name: code
    goal: Prompt the user to sketch code structure in pseudocode. Ask if they need help validating flow or logic.
```

MCP keeps the model **anchored in each phase** and allows transitions only when the current step is complete. This prevents skipping steps or jumping ahead.

#### Dynamic Memory Management/Context

Capture and reuse user answers:

```yaml
dynamic_context:
  - constraints_summary: "Input is a list of integers. Output is the max sum of any contiguous subarray."
  - ideas_discussed: ["brute-force with nested loops", "Kadane's algorithm"]
  - test_cases_created: ["[1, 2, 3, -2, 5]", "[-1, -2, -3]", "[5]"]
```

This memory allows the professor to reference past discussions, ensuring continuity and relevance in guidance.

### Implementation Details

Current ideas for the architecture:

1. Frontend
   - A simple web interface where users can interact with the professor.
   - Input fields for problem statements, constraints, ideas, and test cases.
   - Display area for the professor's responses and guidance based on The Algorithm Design Canvas.
   - WYSIWYG editor for code sketching.
2. Backend
   - Agent orchestration that loads the MCP and manages the conversation flow.
   - Claude AI model that processes user inputs and generates responses based on the MCP.
   - Context includes static prompt + dynamic memory management to maintain continuity.
3. Storage Layer
   - Store user sessions, problem statements, constraints, ideas, test cases, and code sketches.
   - Use PostgreSQL to persist user progress and allow resuming sessions.

### Future Enhancements

- **Personalized hints**: Track when a user struggles and provide tailored hints or examples without giving away the solution.
- **Feedback summaries**: Let the professor summarize key takeaways after each session.
- **Reflection questions**: Ask users to reflect on their learning after completing a problem.
