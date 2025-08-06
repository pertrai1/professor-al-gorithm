# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Application Development (Python/Gradio)

```bash
pip install -r requirements.txt  # Install Python dependencies
python3 app.py                   # Run Gradio application
```

### Development with Docker

```bash
# Docker development
docker build -t professor-al-gorithm .
docker run -p 7860:7860 --env-file .env professor-al-gorithm
```

### Environment Setup

```bash
# Create .env file with your MCP credentials:
echo "MCP_ENDPOINT=https://api.topcoder-dev.com/v6/mcp/mcp" > .env
echo "MCP_SESSION_TOKEN=your-64-character-hex-token" >> .env

# Optional Gradio configuration
export GRADIO_SERVER_PORT=7860
export GRADIO_SERVER_NAME=0.0.0.0
```

#### Environment Variables

```bash
# Required
MCP_ENDPOINT=https://api.topcoder-dev.com/v6/mcp/mcp
MCP_SESSION_TOKEN=your-64-character-hex-token

# Optional Gradio settings
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
```

### Testing

The application includes built-in error handling and validation:

```bash
# Test the application manually
python3 app.py

# Test MCP connection
python3 -c "from dotenv import load_dotenv; import os; load_dotenv('.env'); print('Token loaded:', '✅' if os.getenv('MCP_SESSION_TOKEN') else '❌')"
```

**Application Test Features:**

- **Built-in Error Handling**: Comprehensive error handling with user-friendly messages
- **MCP Integration Testing**: Automatic fallback to educational content when MCP server is unavailable
- **Input Validation**: Validation for all user inputs with appropriate error messages
- **Connection Management**: Automatic retry logic and session management for MCP connectivity
- **Graceful Degradation**: System continues operating when external services are unavailable

## Architecture Overview

This is an educational AI agent project called "Professor Al Gorithm" that teaches coding problem-solving using the Algorithm Design Canvas methodology. The application is built as a single Python/Gradio web interface with direct MCP integration to fetch real coding challenges and skills data from Topcoder.

### Core Components

1. **Gradio Web Application** (`app.py`)
   - Complete web-based user interface built with Gradio
   - Interactive Algorithm Design Canvas with 4-phase tabs
   - Built-in MCP client for direct Topcoder integration
   - Real-time challenge fetching and skills recommendations
   - Educational guidance system with Socratic questioning approach
   - Session management and connection handling

2. **Built-in MCP Client** (within `app.py`)
   - Direct JSON-RPC 2.0 communication with Topcoder MCP server
   - Session-based authentication using `X-MCP-Session` headers
   - Parses Server-Sent Events (SSE) responses with double-encoded JSON
   - Provides two main tools: `query-tc-challenges` and `query-tc-skills`
   - Automatic connection management and retry logic

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

#### MCP Integration Features

- **Connection Management**: Automatic session establishment and management
- **Session Recovery**: Automatic session reinitialization on authentication errors
- **Fallback Behavior**: Educational content when MCP server is unavailable
- **Error Classification**: Network errors, timeouts, and server errors handled differently
- **Input Validation**: Parameter validation and sanitization before MCP calls
- **Response Parsing**: Handles Server-Sent Events and double-encoded JSON responses
- **Category Validation**: Skills endpoint validates category parameters

### Python Configuration

- Uses Python 3.9+ with type hints
- Asyncio for non-blocking MCP operations
- Environment variable loading with python-dotenv
- Comprehensive error handling throughout

### Environment Requirements

Create `.env` file in root directory:

```
MCP_ENDPOINT=https://api.topcoder-dev.com/v6/mcp/mcp
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

#### Implementation Patterns

- **Async Operations**: All MCP operations are asynchronous to prevent UI blocking
- **Input Sanitization**: All user inputs validated and sanitized
- **Graceful Degradation**: System continues operating when MCP is unavailable
- **Connection Management**: Automatic connection establishment and retry logic
- **Error Classification**: Structured error handling with user-friendly messages
- **Session Management**: Proper MCP session lifecycle management

### Dependencies

#### Python Dependencies

- **gradio**: Web interface framework for AI applications
- **aiohttp**: Async HTTP client for MCP server communication
- **python-dotenv**: Environment variable management
- **asyncio**: Asynchronous programming support (built-in)
- **json**: JSON parsing and handling (built-in)
- **os**: Operating system interface (built-in)
- **time**: Time-related functions (built-in)
- **typing**: Type hints support (built-in)

### Application Interface

The Gradio application provides a complete web interface with:

#### Application Features

- **Built-in MCP Integration**: Direct connection to Topcoder MCP server
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Input Validation**: All inputs validated before processing
- **Fallback Content**: Educational content when MCP server is unavailable
- **Session Management**: Automatic MCP session management
- **Async Operations**: Non-blocking UI with loading indicators

#### User Interface Components

- **Challenge Selection**: Dropdown for difficulty levels with real-time fetching
- **Skills Browser**: Category-based skills exploration with Topcoder data
- **Algorithm Design Canvas**: 4-phase tabbed interface (Constraints → Ideas → Tests → Code)
- **Educational Guidance**: Context-aware hints and Socratic questioning
- **Error Messages**: Clear, actionable error messages for all failure scenarios
- **Loading States**: Visual feedback during MCP operations

### Application Architecture

The Gradio application (`app.py`) provides:

- **Interactive Canvas Interface**: 4-phase tabbed interface (Constraints → Ideas → Tests → Code)
- **Direct MCP Integration**: Built-in MCP client for real-time Topcoder data fetching
- **Educational Guidance**: Socratic questioning approach with phase-specific guidance
- **Responsive Design**: Clean, accessible interface optimized for learning
- **Error Handling**: Graceful fallbacks when MCP server is unavailable
- **Async Operations**: Non-blocking MCP calls with loading indicators

### Deployment Architecture

#### Hugging Face Spaces Deployment

- **Single-service container**: Streamlined Python/Gradio application in Docker image
- **Simple startup**: Direct application launch with environment variable loading
- **Environment variables**: MCP credentials configured via Hugging Face Spaces secrets
- **Port configuration**: Gradio application on 7860 (Spaces standard)
- **CPU Basic optimized**: Runs efficiently on free tier hardware (no GPU required)
- **Health checks**: Built-in connection validation and startup checks
- **Deployment ready**: Complete deployment instructions in README.md

### Project Structure

```
.
├── app.py                 # Complete Gradio web application with built-in MCP client
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container build for Hugging Face Spaces
├── .env                  # Environment variables (not committed)
├── docs/
│   └── topcoder-challenge-details.md  # Challenge documentation
├── CLAUDE.md              # This file - development guidelines
└── README.md              # Project overview and documentation
```
