# Professor Al Gorithm - Virtual Data Structure and Algorithm Tutor 🎓

**An AI agent that guides you through solving coding problems using the Algorithm Design Canvas methodology.**

## About This Space

This Hugging Face Space contains a full-stack AI application that teaches algorithms through interactive problem-solving. The system integrates with Topcoder's MCP (Model Context Protocol) server to fetch real coding challenges and provide educational guidance.

### Key Features

✅ **Interactive Algorithm Design Canvas**: 4-phase structured approach (Constraints → Ideas → Tests → Code)  
✅ **Real Coding Challenges**: Live integration with Topcoder challenge database  
✅ **Socratic Teaching Method**: Guides thinking without giving away solutions  
✅ **Full-Stack Architecture**: Node.js backend + Python/Gradio frontend  
✅ **CPU-Optimized**: Runs efficiently on Hugging Face CPU Basic (free tier)

### How to Use

1. **Start with a Challenge**: Click "Get Random Challenge" to fetch a problem from Topcoder
2. **Follow the Canvas**: Progress through each phase:
   - **Constraints**: Define input/output and performance requirements
   - **Ideas**: Brainstorm and evaluate solution approaches
   - **Test Cases**: Create comprehensive test scenarios
   - **Code**: Structure your solution step-by-step
3. **Get Guidance**: The AI professor provides hints and questions to guide your thinking
4. **Learn by Discovery**: No code is provided - you develop solutions through guided reasoning

### Educational Approach

This tool implements a **Socratic questioning approach** where:

- Questions guide your thinking process
- No complete solutions are provided
- Focus is on understanding problem-solving methodology
- Progression is sequential through canvas phases
- Learning happens through discovery and reasoning

### Technical Architecture

- **Frontend**: Gradio web interface with tabbed canvas layout
- **Backend**: Express.js API server with comprehensive error handling
- **Integration**: MCP protocol connection to Topcoder challenge database
- **Deployment**: Multi-service Docker container optimized for Hugging Face Spaces
- **Performance**: Real-time monitoring with health checks and performance metrics

### Use Cases

Perfect for:

- **Coding Interview Preparation**: Practice whiteboard problem-solving methodology
- **Algorithm Learning**: Structured approach to understanding algorithmic thinking
- **Educational Settings**: Teaching problem-solving frameworks in CS courses
- **Self-Study**: Independent learning with guided discovery approach

---

_Built for the Topcoder "Learn AI – Build and Deploy an AI Agent" challenge. Optimized for Hugging Face Spaces CPU Basic hardware._
