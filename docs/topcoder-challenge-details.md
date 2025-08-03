# Learn AI – Build and Deploy an AI Agent with Topcoder MCP on Hugging Face

## Challenge Details

**Technology Focus:** Development of AI Agents using the Model Context Protocol (MCP)
**Submission Duration:** 21 days
**Agent Type:** Any form of intelligent application is allowed—such as chatbots, virtual assistants, research tools, code generators, or data visualization agents.
Creativity: Participants are encouraged to push boundaries and design original, inventive AI applications.
**Functionality:** The AI agent must address a clearly defined problem or purpose and deliver impactful, practical results.
**Implementation Requirements:**

- The AI agent must be designed to run within a [Hugging Face Space](https://huggingface.co/docs/hub/spaces-overview).
- You can use any SDK or programming language, as long as it functions correctly in the Hugging Face Space environment.
- The agent must run smoothly on the default free-tier hardware (CPU Basic) provided by Hugging Face—no GPU usage required.
- It must connect to and interact with the Topcoder MCP server and deliver clear, purposeful results through an intuitive and user-friendly interface.

## Submission Requirements

- A fully functional AI Agent application, either as a downloadable codebase (zip file) or a publicly accessible Hugging Face Space link—or both.
- The submission must be based on a clearly defined use case that addresses a specific problem. Participants should also include a simple, clear document (as part of the submission) that outlines the problem being solved, the rationale behind the chosen use case, and how the AI agent addresses it. This clarity should also be reflected in the agent’s implementation and user experience.
- Accompanying documentation that clearly explains how to deploy, configure, and run the AI agent on Hugging Face Spaces.
- An optional demo video (up to 5 minutes) showcasing the agent’s core functionality and how it addresses the defined use case.

### Module 5: Building Agent Logic & MCP Integration (Days 2–3)

**Objective**: Implement the core logic of your agent to communicate effectively with the Topcoder MCP server, retrieve data, and generate intelligent outputs.

- Set up your project structure using a preferred language (Python, TypeScript, etc.)
- Choose your connection method (SSE or Streamable HTTP) and implement a request handler for MCP
- Integrate the MCP endpoint(s) you selected in Module 3
- Process incoming data and prepare meaningful responses
- Apply prompt engineering principles to enhance agent output quality
- Ensure your logic runs efficiently on Hugging Face CPU Basic (no GPU dependencies)

**Recommended Resources:**

- [Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
- Example backend agent using Python with SSE + Hugging Face: [MCP Agent Boilerplate (Python)](https://github.com/lastmile-ai/mcp-agent)
  - Demonstrates how to:
    - Connect to Topcoder MCP using SSE
    - Build an async backend agent using FastAPI
    - Deploy to Hugging Face with CPU basic config
  - This is ideal if you're building a backend-only agent with no frontend SDK involved.
- EventSource API Reference: MDN Docs Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
- Example SSE integration (React or Node): [MDN EventSource Docs](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

**Deliverable:**

- A backend agent logic module that:
  - Successfully connects to and queries the MCP server
  - Returns usable responses to the frontend
  - Demonstrates use of at least one real MCP tool or endpoint
- A brief explanation (in your README) of how the MCP connection is implemented and which tools it uses

### Module 6: UI/UX Development (Days 2–3)

**Objective:** Create an accessible, intuitive interface to showcase your AI agent’s capabilities.

- Choose a simple UI framework such as Gradio, Streamlit, or a minimal HTML/JS frontend (Gradio recommended for ease of Hugging Face integration)
- Link the UI to your backend logic (built in Module 5)
- Focus on making input fields and output displays clear and accessible
- Provide contextual labels, input placeholders, and output formatting where helpful
- Consider adding a loading indicator or progress feedback if MCP requests take time

**Deliverable:** A lightweight, working UI prototype that allows users to interact with your agent and see live responses from the MCP server

### Module 7: End-to-End Testing & Debugging (Days 1–2)

**Objective:** Ensure your agent is production-ready through comprehensive testing and optimization.

- Perform full end-to-end testing: UI → backend → MCP → backend → UI
- Simulate real user interactions and input variations
- Identify and handle edge cases, unexpected input, and communication errors (e.g., timeouts, SSE disconnects)
- Add fallback behavior or helpful messages for errors
- Profile and optimize response time, agent feedback, and loading states

**Deliverable:** A stable, polished, and bug-free agent that reliably handles diverse inputs and edge scenarios

### Module 8: Deployment on Hugging Face Spaces (Days 1–2)

**Objective:** Deploy your agent to a live environment and ensure it's accessible and stable.

- Prepare `requirements.txt`
- Prepare `README.md` with necessary dependencies and setup instructions
- Push your project to a new or existing Hugging Face Space
- Confirm successful deployment on the default CPU Basic hardware (no GPU)
- Perform smoke testing to validate end-to-end functionality

**Deliverable:** A fully deployed Hugging Face Space (public link) or a repository that’s ready to be deployed without additional changes
