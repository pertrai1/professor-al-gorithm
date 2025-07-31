# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Backend Development (TypeScript/Node.js)
```bash
cd backend
npm install                 # Install dependencies
npm run dev                 # Run development server with ts-node
npm run start               # Run production server with ts-node
npm run build               # Compile TypeScript to JavaScript
```

### Testing
Currently no test framework is configured - tests need to be implemented.

## Architecture Overview

This is an educational AI agent project called "Professor Al Gorithm" that teaches coding problem-solving using the Algorithm Design Canvas methodology. The system integrates with Topcoder's MCP (Model Context Protocol) server to fetch real coding challenges and skills data.

### Core Components

1. **MCP Integration Layer** (`backend/src/mcpService.ts`)
   - Handles JSON-RPC 2.0 communication with Topcoder MCP server
   - Manages session-based authentication using `X-MCP-Session` headers
   - Parses Server-Sent Events (SSE) responses with double-encoded JSON
   - Provides two main tools: `query-tc-challenges` and `query-tc-skills`

2. **MCP Utilities** (`backend/src/mcpUtils.ts`)
   - Reusable functions for headers, SSE parsing, and session management
   - Session token extraction and management utilities

3. **Main Entry Point** (`backend/src/index.ts`)
   - Simple testing interface for MCP functionality

### Algorithm Design Canvas Methodology

The project follows a structured 4-phase approach for teaching problem-solving:
1. **Constraints** - Define problem space, input/output formats, performance requirements
2. **Ideas** - Brainstorm and evaluate solution approaches  
3. **Test Cases** - Create comprehensive test scenarios
4. **Code** - Implement solution structure step-by-step

### MCP Integration Specifics

- **Authentication**: Uses 64-character hex session tokens from environment variables
- **Protocol**: JSON-RPC 2.0 over Server-Sent Events
- **Response Format**: SSE with nested JSON requiring double parsing
- **Session Management**: Single global session, auto-initialized on first use
- **Tool Parameters**: Use `difficulty="easy"` for beginners, `category="algorithms"` for skills

### TypeScript Configuration

- Uses CommonJS modules with ES2016 target
- Strict type checking enabled
- Development uses ts-node for direct TypeScript execution
- All types properly defined - avoid `any` types

### Environment Requirements

Create `.env` file in backend directory:
```
MCP_ENDPOINT=<topcoder-mcp-endpoint>
MCP_SESSION_TOKEN=<64-char-hex-token>
```

### Educational Approach

- Never provide complete code solutions - guide thinking process only
- Use Socratic questioning to lead students to discoveries
- Format Topcoder data for learning with `formatChallengesForLearning()` and `formatSkillsForLearning()`
- Maintain sequential progression through Canvas phases - no skipping allowed

### Key Implementation Patterns

- Comprehensive error handling with typed error objects
- SSE response parsing using `parseSSEData()` utility
- Fallback educational responses when MCP fails
- Console logging for debugging MCP interactions
- Session initialization happens automatically on first tool call

### Dependencies

- **axios**: HTTP client for MCP server communication
- **dotenv**: Environment variable management
- **ts-node**: Development TypeScript execution
- **typescript**: TypeScript compiler

### Future Frontend Integration

The backend is designed to support a web interface with:
- Canvas phase enforcement at UI level
- Progress tracking across 4-phase methodology
- Real-time challenge selection from MCP data
- Deployment target: Hugging Face Spaces