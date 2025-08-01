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

### Frontend Development (Python/Gradio)

```bash
pip install -r requirements.txt  # Install Python dependencies
python app.py                     # Run Gradio frontend (requires backend running)
```

### Full Stack Development

```bash
# Option 1: Manual startup (recommended for development)
# Terminal 1 - Backend
cd backend && npm run dev

# Terminal 2 - Frontend (after backend is running)
python app.py

# Option 2: Automated startup script
chmod +x start.sh
./start.sh

# Option 3: Docker development
docker build -t professor-al-gorithm .
docker run -p 7860:7860 --env-file backend/.env professor-al-gorithm
```

### Environment Setup

```bash
# Backend environment
cd backend
cp .env.example .env
# Edit .env with your MCP credentials:
# MCP_ENDPOINT=https://your-topcoder-mcp-server.com
# MCP_SESSION_TOKEN=your-64-character-hex-token

# Frontend environment (optional)
export BACKEND_URL=http://localhost:3000  # Default value
```

### Testing

Currently no test framework is configured - tests need to be implemented.

## Architecture Overview

This is an educational AI agent project called "Professor Al Gorithm" that teaches coding problem-solving using the Algorithm Design Canvas methodology. The system integrates with Topcoder's MCP (Model Context Protocol) server to fetch real coding challenges and skills data.

### Core Components

1. **Gradio Frontend** (`app.py`)
   - Web-based user interface built with Gradio
   - Interactive Algorithm Design Canvas with 4-phase tabs
   - Real-time challenge fetching and skills recommendations
   - Educational guidance system with Socratic questioning approach
   - Connects to backend API for MCP integration

2. **Express.js API Server** (`backend/src/server.ts`)
   - RESTful API endpoints for frontend communication
   - CORS-enabled for cross-origin requests
   - Comprehensive error handling and logging
   - Health checks and status monitoring

3. **MCP Integration Layer** (`backend/src/mcpService.ts`)
   - Handles JSON-RPC 2.0 communication with Topcoder MCP server
   - Manages session-based authentication using `X-MCP-Session` headers
   - Parses Server-Sent Events (SSE) responses with double-encoded JSON
   - Provides two main tools: `query-tc-challenges` and `query-tc-skills`

4. **MCP Utilities** (`backend/src/mcpUtils.ts`)
   - Reusable functions for headers, SSE parsing, and session management
   - Session token extraction and management utilities

5. **Testing Interface** (`backend/src/index.ts`)
   - Console-based testing interface for MCP functionality
   - Useful for debugging and development

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

#### Backend Dependencies

- **axios**: HTTP client for MCP server communication
- **dotenv**: Environment variable management
- **ts-node**: Development TypeScript execution
- **typescript**: TypeScript compiler
- **express**: Web framework for API server
- **cors**: Cross-origin resource sharing middleware

#### Frontend Dependencies

- **gradio**: Web interface framework for AI applications
- **aiohttp**: Async HTTP client for backend communication
- **requests**: HTTP library for synchronous requests

### API Endpoints

The Express.js server provides RESTful endpoints for the Gradio frontend:

#### Core Endpoints

- `GET /` - Health check and API info
- `GET /health` - Health check with timestamp
- `POST /api/chat` - Main conversation interface with Professor Al Gorithm
- `GET /api/challenges` - Fetch Topcoder challenges (query parameters)
- `POST /api/challenges` - Fetch Topcoder challenges (JSON body, for Gradio frontend)
- `GET /api/skills` - Fetch available skills (query parameters)
- `POST /api/skills` - Fetch available skills (JSON body, for Gradio frontend)
- `POST /api/canvas` - Algorithm Design Canvas phase processing

#### Example Usage

```bash
# Health check
curl http://localhost:3000/health

# Start a conversation
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to learn about algorithms", "conversationId": "123"}'

# Get challenges (POST - JSON body, used by Gradio)
curl -X POST http://localhost:3000/api/challenges \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy", "limit": 5}'

# Get skills (POST - JSON body, used by Gradio)
curl -X POST http://localhost:3000/api/skills \
  -H "Content-Type: application/json" \
  -d '{"category": "algorithms", "limit": 10}'

# Submit canvas phase
curl -X POST http://localhost:3000/api/canvas \
  -H "Content-Type: application/json" \
  -d '{"phase": "constraints", "content": "Input: array of integers, Output: sorted array"}'
```

### Frontend Architecture

The Gradio frontend (`app.py`) provides:

- **Interactive Canvas Interface**: 4-phase tabbed interface (Constraints → Ideas → Tests → Code)
- **Real-time MCP Integration**: Fetches challenges and skills from Topcoder via backend API
- **Educational Guidance**: Socratic questioning approach with phase-specific guidance
- **Responsive Design**: Clean, accessible interface optimized for learning
- **Error Handling**: Graceful fallbacks when backend is unavailable
- **Async Operations**: Non-blocking API calls with loading indicators

### Deployment Architecture

#### Hugging Face Spaces Deployment

- **Multi-service container**: Both Node.js backend and Python frontend in single Docker image
- **Service orchestration**: Backend starts first, frontend connects after startup delay
- **Environment variables**: MCP credentials configured via Hugging Face Spaces secrets
- **Port configuration**: Backend on 3000, Gradio frontend on 7860 (Spaces standard)

### Project Structure

```
.
├── app.py                 # Gradio frontend application
├── requirements.txt       # Python dependencies
├── start.sh              # Development startup script
├── Dockerfile            # Multi-stage build for Hugging Face Spaces
├── backend/
│   ├── src/
│   │   ├── server.ts     # Express API server
│   │   ├── mcpService.ts # MCP integration & education logic
│   │   ├── mcpUtils.ts   # MCP utilities (headers, parsing)
│   │   └── index.ts      # Console testing interface
│   ├── package.json      # Node.js dependencies
│   ├── tsconfig.json     # TypeScript configuration
│   └── .env              # Environment variables (not committed)
├── docs/
│   └── topcoder-challenge-details.md  # Challenge documentation
├── CLAUDE.md             # This file - development guidelines
└── README.md             # Project overview and documentation
```
