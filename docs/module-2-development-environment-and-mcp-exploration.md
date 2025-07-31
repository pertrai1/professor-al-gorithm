# Module 2: Development Environment Setup & MCP Exploration

## Learning Objectives Achieved

By the end of this module, we have successfully:

- ✅ Set up a complete TypeScript/Node.js development environment
- ✅ Established working connection to Topcoder MCP server
- ✅ Understood MCP authentication and session management
- ✅ Explored available MCP tools and their capabilities
- ✅ Implemented proper project structure and version control

## What We Learned Today

### 1. Model Context Protocol (MCP) Fundamentals

#### Key Concepts

- **MCP is a standardized protocol** for AI agents to interact with external services
- **JSON-RPC 2.0** is the underlying communication protocol
- **Server-Sent Events (SSE)** transport mechanism for real-time data streaming
- **Session-based authentication** for maintaining context across requests

#### Topcoder MCP Server Details

- **Endpoint**: `https://api.topcoder-dev.com/v6/mcp/mcp`
- **Authentication**: Uses `X-MCP-Session` header with session tokens
- **Protocol Version**: `2024-11-05`
- **Transport**: Streamable HTTP with SSE responses

### 2. Authentication Journey & Problem Solving

#### Initial Challenges

We encountered several authentication roadblocks:

- ❌ `"Bad Request: No valid session ID provided"`
- ❌ `"Invalid or expired JWT"`
- ❌ `"Invalid credentials in Authorization header"`

#### Solution Discovery Process

1. **Tried multiple approaches**: Hugging Face tokens, username/password auth, JWT tokens
2. **Found working solution**: Session tokens from challenge discussion
3. **Reverse-engineered from Python client**: Discovered proper authentication flow
4. **Implemented TypeScript equivalent**: Created working session management

#### Final Working Authentication

```typescript
const headers = {
  Accept: "application/json, text/event-stream",
  "Content-Type": "application/json",
  "X-MCP-Session": MCP_SESSION_TOKEN, // 64-character hex token
};
```

### 3. MCP Protocol Implementation

#### Session Initialization

```typescript
const initPayload = {
  jsonrpc: "2.0",
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: { tools: {} },
    clientInfo: {
      name: "professor-al-gorithm",
      version: "1.0.0",
    },
  },
  id: 1,
};
```

#### SSE Response Parsing

We learned that MCP responses come as Server-Sent Events:

```
event: message
data: {"result":{"protocolVersion":"2024-11-05",...},"jsonrpc":"2.0","id":1}
```

Key parsing strategy:

- Split by newlines
- Look for lines starting with `"data: "`
- Parse the JSON content after the prefix

### 4. Available MCP Tools Discovery

#### Tools Found

1. **`query-tc-challenges`**
   - Purpose: Returns Topcoder challenges based on query parameters
   - Inputs: status, type, track, tags, search terms, date ranges, pagination
   - Outputs: Paginated list of challenges with full metadata

2. **`query-tc-skills`**
   - Purpose: Returns standardized skills from Topcoder platform
   - Inputs: skill names, IDs, sorting options, pagination
   - Outputs: Skills with categories and descriptions

#### What We Discovered

- ❌ No generic `"ask"` method exists (returns "Method not found")
- ✅ Specific tools for querying Topcoder data
- ✅ Rich schemas with detailed input/output specifications
- ✅ Proper pagination and filtering capabilities

### 5. Project Architecture Lessons

#### File Structure Evolution

```
professor-al-gorithm/
├── backend/
│   ├── src/
│   │   ├── index.ts              # Main application
│   │   ├── mcpService.ts         # Production MCP service
│   │   └── testMCPWorkflow.ts    # Working test/demo
│   ├── package.json
│   └── .env                      # Environment variables
├── docs/                         # Learning documentation
├── README.md
└── .gitignore
```

#### Code Organization Principles

- **Separation of concerns**: Test files vs production code
- **Environment configuration**: Secure token management
- **Clean architecture**: Service layer abstraction
- **Documentation**: Comprehensive learning tracking

### 6. TypeScript & Node.js Best Practices

#### Environment Management

```typescript
import dotenv from "dotenv";
dotenv.config();

const MCP_ENDPOINT = process.env.MCP_ENDPOINT;
const MCP_SESSION_TOKEN = process.env.MCP_SESSION_TOKEN;
```

#### Error Handling

```typescript
try {
  const response = await axios.post(endpoint, payload, { headers });
  // Success handling
} catch (error: any) {
  console.error("Error:", error.response?.data || error.message);
  // Graceful failure
}
```

#### Type Safety

- Used TypeScript for better development experience
- Proper type annotations for API responses
- Interface definitions for structured data

### 7. Debugging Methodology

#### Systematic Approach

1. **Understand the problem**: Authentication failure analysis
2. **Research solutions**: Study working examples (Python client)
3. **Implement incrementally**: Test each component separately
4. **Validate thoroughly**: Verify with actual API calls
5. **Document learnings**: Capture working solutions

#### Tools Used

- **axios**: HTTP client for API requests
- **dotenv**: Environment variable management
- **console logging**: Detailed debugging output
- **npm scripts**: Task automation

### 8. Version Control & Project Management

#### Git Best Practices

- Comprehensive `.gitignore` for Node.js projects
- Secure handling of environment variables
- Clean repository structure
- Documentation-driven development

#### Cleanup Process

- Removed debugging/test files after finding solutions
- Consolidated working code into production services
- Maintained test workflow for future reference

## Key Takeaways

### Technical Insights

1. **MCP is powerful but specific**: Not a generic chat interface, but tool-based interactions
2. **Authentication matters**: Proper session management is critical
3. **SSE parsing required**: MCP responses need specialized handling
4. **Documentation is key**: Well-documented APIs make integration easier

### Development Insights

1. **Iterative problem solving**: Break complex problems into smaller parts
2. **Learn from working examples**: Reverse-engineering can reveal solutions
3. **Clean as you go**: Remove temporary code once solutions are found
4. **Document the journey**: Capture both failures and successes

### AI Agent Architecture Insights

1. **Layer your services**: Separate MCP integration from business logic
2. **Handle failures gracefully**: Provide fallback responses
3. **Design for extensibility**: Structure for future enhancements
4. **User experience first**: Think about how humans will interact

## Next Steps (Module 3 & Beyond)

### Immediate Priorities

1. **Explore MCP tools in depth**: Test `query-tc-challenges` and `query-tc-skills`
2. **Design user interactions**: How will Professor Al Gorithm use these tools?
3. **Implement Algorithm Design Canvas**: Integrate MCP data with teaching methodology
4. **Build frontend interface**: Create user-friendly interaction layer

### Future Enhancements

1. **Advanced MCP integration**: Use multiple tools in concert
2. **State management**: Track user progress through algorithm learning
3. **Personalization**: Adapt to user skill level and preferences
4. **Deployment preparation**: Ready for Hugging Face Spaces

## Resources & References

### Documentation

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Topcoder Challenge Details](https://www.topcoder.com/challenges/355a5497-71c3-4e3a-b200-f53d62564667)
- [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course/unit0/introduction)

### Working Code Examples

- `testMCPWorkflow.ts`: Complete working MCP connection example
- `mcpService.ts`: Production-ready MCP service integration
- Python client reference: Available in challenge discussion

### Environment Setup

```bash
# Install dependencies
npm install axios dotenv typescript ts-node @types/node

# Environment variables (.env)
MCP_ENDPOINT=https://api.topcoder-dev.com/v6/mcp
MCP_SESSION_TOKEN=your_64_character_hex_token_here

# Test connection
npm run test-mcp-workflow
```

## Reflection Questions

1. **What surprised you most about MCP?** The specificity of tools vs generic chat interface
2. **What was the biggest challenge?** Authentication - required reverse-engineering from Python
3. **What would you do differently?** Start with working examples before attempting custom implementations
4. **How does this change your AI agent vision?** More structured, tool-based interactions rather than free-form chat

---
