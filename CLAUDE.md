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
# Optional: Create .env file with MCP credentials (when server becomes available):
echo "MCP_SESSION_TOKEN=your-64-character-hex-token" > .env

# Optional Gradio configuration
export GRADIO_SERVER_PORT=7860
export GRADIO_SERVER_NAME=0.0.0.0
```

#### Environment Variables

```bash
# Optional (for MCP integration when server is available)
MCP_SESSION_TOKEN=your-64-character-hex-token

# Optional Gradio settings
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
```

**Note:** The application works perfectly without any environment variables, using rich educational fallback content.

### Testing

The application includes built-in error handling and validation:

```bash
# Test the application manually
python3 app.py

# Test MCP connection
python3 -c "from dotenv import load_dotenv; import os; load_dotenv('.env'); print('Token loaded:', '✅' if os.getenv('MCP_SESSION_TOKEN') else '❌')"
```

**Application Test Features:**

- **Rich Educational Content**: 10+ coding challenges across Easy/Medium/Hard difficulties with comprehensive skills guides
- **Built-in Error Handling**: Comprehensive error handling with user-friendly messages
- **Educational Fallback System**: Robust educational content ensures platform works immediately
- **Input Validation**: Validation for all user inputs with appropriate error messages
- **MCP Integration Ready**: Built-in MCP client ready for when Topcoder server issues are resolved
- **Graceful Degradation**: System continues operating without external dependencies

## Architecture Overview

This is an educational AI agent project called "Professor Al Gorithm" that teaches coding problem-solving using the Algorithm Design Canvas methodology. The application is built as a single Python/Gradio web interface that works immediately with rich educational content, and includes MCP integration ready for when Topcoder server issues are resolved.

### Core Components

1. **Gradio Web Application** (`app.py`)
   - Complete web-based user interface built with Gradio
   - Interactive Algorithm Design Canvas with 4-phase tabs
   - Rich educational content with 10+ coding challenges and comprehensive skills guides
   - Context-aware educational guidance system with Socratic questioning approach
   - Session management and progress tracking
   - Built-in MCP client ready for future integration

2. **Educational Content System** (within `app.py`)
   - Structured challenge library across Easy/Medium/Hard difficulties
   - Comprehensive skills guides for algorithms, data structures, dynamic programming, and graphs
   - Context-aware guidance tailored to selected challenges
   - Phase-specific hints and Socratic questioning prompts
   - Fallback system ensuring platform works without external dependencies

3. **MCP Client (Ready for Integration)** (within `app.py`)
   - Direct JSON-RPC 2.0 communication with Topcoder MCP server (when available)
   - Session-based authentication using session tokens
   - Automatic fallback to educational content during server issues
   - Built-in error handling and retry logic
   - Ready for activation when Topcoder server becomes stable

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

**Optional:** Create `.env` file in root directory for MCP integration when server becomes available:

```
MCP_SESSION_TOKEN=<64-char-hex-token>
```

**Note:** The application works perfectly without any environment file, using rich educational content.

### Educational Approach

- Never provide complete code solutions - guide thinking process only
- Use Socratic questioning to lead students to discoveries
- Rich educational content structured for optimal learning progression
- Context-aware guidance that adapts to selected challenges and user input
- Maintain sequential progression through Canvas phases with appropriate guidance
- Educational fallback content ensures continuous learning experience

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

- **Rich Educational Platform**: Immediate access to 10+ coding challenges and comprehensive skills guides
- **MCP Integration Ready**: Built-in MCP client ready for when Topcoder server is available
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Input Validation**: All inputs validated before processing
- **Robust Fallback System**: Educational content ensures platform works without external dependencies
- **Session Management**: Progress tracking and challenge selection management
- **Async Operations**: Non-blocking UI with loading indicators

#### User Interface Components

- **Challenge Selection**: Dropdown for difficulty levels with immediate educational content
- **Skills Browser**: Category-based skills exploration with comprehensive guides
- **Algorithm Design Canvas**: 4-phase tabbed interface (Constraints → Ideas → Tests → Code)
- **Educational Guidance**: Context-aware hints and Socratic questioning tailored to selected challenges
- **Challenge Details**: Rich challenge descriptions with examples and skills focus
- **Error Messages**: Clear, actionable error messages for all failure scenarios
- **Loading States**: Visual feedback during operations

### Application Architecture

The Gradio application (`app.py`) provides:

- **Interactive Canvas Interface**: 4-phase tabbed interface (Constraints → Ideas → Tests → Code)
- **Rich Educational Content**: 10+ challenges and comprehensive skills guides available immediately
- **Educational Guidance**: Context-aware Socratic questioning approach with phase-specific guidance
- **Responsive Design**: Clean, accessible interface optimized for learning
- **MCP Integration Ready**: Built-in client ready for when Topcoder server becomes available
- **Robust Architecture**: Works perfectly without external dependencies

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
