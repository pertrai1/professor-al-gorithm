# AI Agent Instructions for Professor Al Gorithm

## Project Overview

Educational AI agent that guides students through coding problems using the Algorithm Design Canvas methodology (Constraints → Ideas → Test Cases → Code Structure). Integrates with Topcoder's MCP server for real-world challenges and skills data.

## Architecture & Core Components

### MCP Integration Pattern

- **Authentication**: Session-based with `X-MCP-Session` header (64-char hex token)
- **Protocol**: JSON-RPC 2.0 over Server-Sent Events (SSE)
- **Tools**: `query-tc-challenges` and `query-tc-skills` only - no generic "ask" method
- **SSE Parsing**: Look for `data: ` lines, parse nested JSON: `JSON.parse(line.substring(6))`

### Key Files & Responsibilities

- `backend/src/mcpService.ts`: Production MCP integration with comprehensive TypeScript interfaces
- `backend/src/mcpUtils.ts`: Reusable MCP utilities (headers, SSE parsing, session management)
- `backend/src/index.ts`: Simple entry point for testing
- `USE-CASE-DOCUMENT.md`: Complete product vision and technical specifications

### Data Structures

```typescript
// Core MCP types - these are already defined in mcpService.ts
interface Challenge {
  id: string;
  name: string;
  track?: string;
  status?: string;
  skills?: ChallengeSkill[];
  description?: string;
}

interface Skill {
  id: string;
  name: string;
  description?: string;
  category?: SkillCategory;
}
```

## Development Workflows

### Environment Setup

```bash
cd backend
npm install
# Create .env with MCP_ENDPOINT and MCP_SESSION_TOKEN
npm run dev  # Uses ts-node for development
npm run build  # TypeScript compilation
```

### MCP Testing

- Use `npm run dev` to test real MCP connections
- Check console for detailed response logging
- Session initialization happens automatically on first call

### Key Patterns

- **Error handling**: Always use typed error objects, never `any`
- **SSE responses**: Use `parseSSEData()` from mcpUtils for consistent parsing
- **Fallback responses**: Provide educational value even when MCP fails
- **Type safety**: Comprehensive interfaces avoid `any` types

## Project-Specific Conventions

### Educational Focus

- Never provide code solutions - guide thinking process only
- Use Algorithm Design Canvas phases: Constraints → Ideas → Test Cases → Code
- Format Topcoder data for learning (see `formatChallengesForLearning()`)
- Maintain Socratic questioning approach

### MCP Integration Specifics

- **Session management**: Single global session, auto-initialize on first use
- **Tool parameters**: Use difficulty="easy" for beginners, category="algorithms" for skills
- **Response format**: MCP returns SSE with double-encoded JSON
- **Authentication flow**: Initialize → Extract session ID → Use for subsequent calls

### Future Frontend Integration

- Canvas phases should be enforced UI states
- Progress tracking across 4-phase methodology
- Real-time challenge selection from MCP data
- Hugging Face Spaces deployment target

## Common Pitfalls

- Don't attempt generic MCP queries - use specific tools only
- SSE responses need double JSON parsing
- Session tokens are environment-specific (64-char hex)
- TypeScript strict mode - all types must be properly defined
- Algorithm Canvas phases must be sequential - no skipping allowed

## Testing & Debugging

- Console logging is comprehensive - check full MCP responses
- Test MCP connection with simple challenge query first
- Verify `.env` file has correct endpoint and token format
- Use MCP Inspector at `localhost:6274` for interactive exploration
