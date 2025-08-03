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

# Production monitoring (optional)
export NODE_ENV=production  # Hides sensitive error details
```

#### Environment Variables

```bash
# Performance monitoring
export ENABLE_PERFORMANCE_MONITORING=true

# Timeout configurations (milliseconds)
# Production defaults:
export MCP_TIMEOUT=30000      # MCP server request timeout
export API_TIMEOUT=30000      # API endpoint timeout
export REQUEST_TIMEOUT=45000  # Overall request timeout

# Test environment (automatically set in tests):
export MCP_TIMEOUT=2000       # Faster test execution
export API_TIMEOUT=3000
export REQUEST_TIMEOUT=5000
```

### Testing

#### Backend Testing (Node.js/Jest)

```bash
# Run all tests (optimized for performance)
cd backend && npm test

# Run with memory leak detection (for debugging)
npm run test:debug

# Run fast tests (single worker, force exit)
npm run test:fast

# Run only E2E tests
npm run test:e2e

# Run tests in watch mode (development)
npm run test:watch

# Generate test coverage report
npm run test:coverage
```

**Backend Test Features:**

- **71 comprehensive tests** covering all API endpoints
- **Unit tests** for validation functions and utilities
- **E2E tests** for complete API workflow validation
- **Performance tests** for concurrent request handling
- **Security tests** for XSS, SQL injection prevention
- **MCP integration tests** with fallback scenarios
- **Memory leak prevention** with proper server lifecycle management
- **Optimized runtime**: ~13 seconds (down from 40+ seconds)

**Test Configuration:**

- Jest with TypeScript support (`ts-jest`)
- Supertest for HTTP endpoint testing
- Automatic server cleanup and connection management
- Environment-specific timeout configurations
- Force exit for CI/CD compatibility

#### Legacy Python E2E Testing

```bash
# Run Python E2E tests (legacy)
python test-e2e.py

# Test with custom backend URL
python test-e2e.py --backend-url http://localhost:3000

# Install test dependencies
pip install aiohttp  # Already in requirements.txt
```

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

#### MCP Integration Enhancements

- **Environment-based Timeouts**: Configurable timeouts (30s production, 2s test)
- **Session Recovery**: Automatic session reinitialization on 401 errors
- **Fallback Behavior**: Educational content when MCP server is unavailable
- **Error Classification**: Network errors, timeouts, and server errors handled differently
- **Input Validation**: Parameter validation and sanitization before MCP calls
- **Performance Monitoring**: Response time tracking and slow request detection
- **Category Validation**: Skills endpoint validates category parameters

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

#### Enhanced Implementation Patterns

- **Environment-based Configuration**: Timeouts adapt to production vs test environments
- **Input Sanitization**: All user inputs validated and sanitized with proper TypeScript types
- **Performance Monitoring**: Built-in metrics collection and analysis
- **Graceful Degradation**: System continues operating when MCP is unavailable
- **Timeout Management**: Configurable request-level timeouts with fallback responses
- **Error Classification**: Structured error responses with timestamps and processing times
- **Security Hardening**: Protection against XSS, SQL injection, and other attacks
- **Memory Management**: Proper server lifecycle management prevents resource leaks

### Dependencies

#### Backend Dependencies

- **axios**: HTTP client for MCP server communication
- **dotenv**: Environment variable management
- **ts-node**: Development TypeScript execution
- **typescript**: TypeScript compiler
- **express**: Web framework for API server
- **cors**: Cross-origin resource sharing middleware

#### Enhanced Backend Components

- **performanceMonitor.ts**: Performance tracking and health monitoring
- **serverHelpers.ts**: Validation functions with TypeScript types and fallback handling
- **Enhanced error handling**: Comprehensive error classification with timestamps
- **Timeout management**: Environment-based timeout configuration
- **Input validation**: Parameter validation with category, difficulty, and limit checks
- **Test infrastructure**: Jest configuration with memory leak prevention

#### Frontend Dependencies

- **gradio**: Web interface framework for AI applications
- **aiohttp**: Async HTTP client for backend communication
- **requests**: HTTP library for synchronous requests

### API Endpoints

The Express.js server provides RESTful endpoints for the Gradio frontend:

#### Enhanced API Features

- **Performance Monitoring**: All endpoints include response time tracking
- **Environment-based Timeouts**: Configurable timeouts for production vs test
- **Enhanced Error Handling**: Structured error responses with timestamps and processing times
- **Input Validation**: Comprehensive validation for all request parameters including categories
- **Health Monitoring**: Extended health checks with performance metrics and system status
- **Memory Management**: Proper connection lifecycle management

#### Core Endpoints

- `GET /` - Health check and API info
- `GET /health` - Enhanced health check with performance metrics and system status
- `GET /api/stats` - Performance statistics and monitoring data
- `POST /api/chat` - Main conversation interface with Professor Al Gorithm
- `GET /api/challenges` - Fetch Topcoder challenges (query parameters)
- `POST /api/challenges` - Fetch Topcoder challenges (JSON body, for Gradio frontend)
- `GET /api/skills` - Fetch available skills (query parameters)
- `POST /api/skills` - Fetch available skills (JSON body, for Gradio frontend)
- `POST /api/canvas` - Algorithm Design Canvas phase processing

#### Enhanced Error Responses

All endpoints return structured error responses with comprehensive information:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-08-03T00:00:00.000Z",
  "processingTime": 1234
}
```

**Error Codes:**

- `INVALID_MESSAGE` - Message validation failed
- `MESSAGE_TOO_LONG` - Message exceeds length limit
- `INVALID_CATEGORY` - Invalid skills category parameter
- `INVALID_LIMIT` - Invalid limit parameter (must be 1-100)
- `TIMEOUT` - Request timed out (environment-specific timeouts)
- `FETCH_ERROR` - MCP server communication failed
- `PROCESSING_ERROR` - Canvas processing failed

**Error Response Features:**

- Timestamps for debugging and monitoring
- Processing time tracking for performance analysis
- Environment-aware error messages (detailed in dev, generic in production)
- Fallback educational responses when MCP services are unavailable

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

#### Hugging Face Spaces Deployment (Module 8)

- **Multi-service container**: Both Node.js backend and Python frontend in single Docker image
- **Service orchestration**: Backend starts first, frontend connects after startup delay
- **Environment variables**: MCP credentials configured via Hugging Face Spaces secrets
- **Port configuration**: Backend on 3000, Gradio frontend on 7860 (Spaces standard)
- **CPU Basic optimized**: Runs efficiently on free tier hardware (no GPU required)
- **Health checks**: Container health monitoring and startup validation
- **Deployment ready**: Complete deployment instructions in README.md Module 8 section

### Project Structure

```
.
├── app.py                 # Gradio frontend application
├── requirements.txt       # Python dependencies
├── start.sh              # Development startup script
├── Dockerfile            # Multi-stage build for Hugging Face Spaces
├── backend/
│   ├── src/
│   │   ├── server.ts          # Express API server with environment-based timeouts
│   │   ├── serverHelpers.ts   # Validation functions and error handling
│   │   ├── mcpService.ts      # MCP integration & education logic
│   │   ├── mcpUtils.ts        # MCP utilities (headers, parsing)
│   │   ├── performanceMonitor.ts # Performance tracking and health monitoring
│   │   └── index.ts           # Console testing interface
│   ├── tests/
│   │   ├── setup.ts           # Jest test configuration and cleanup
│   │   ├── unit/              # Unit tests for individual functions
│   │   │   ├── serverHelpers.test.ts
│   │   │   └── performanceMonitor.test.ts
│   │   └── e2e/               # End-to-end API tests
│   │       └── api.test.ts    # Comprehensive API testing suite
│   ├── jest.config.js     # Jest configuration with memory leak prevention
│   ├── package.json       # Node.js dependencies and test scripts
│   ├── tsconfig.json      # TypeScript configuration
│   └── .env               # Environment variables (not committed)
├── docs/
│   └── topcoder-challenge-details.md  # Challenge documentation
├── CLAUDE.md              # This file - development guidelines
└── README.md              # Project overview and documentation
```
