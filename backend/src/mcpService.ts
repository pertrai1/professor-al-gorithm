import axios from "axios";
import dotenv from "dotenv";
import {
  parseSSEResponse,
  createMCPHeaders,
  createMCPInitPayload,
  extractSessionId,
} from "./mcpUtils";

dotenv.config();

const MCP_ENDPOINT = process.env.MCP_ENDPOINT;
const MCP_SESSION_TOKEN = process.env.MCP_SESSION_TOKEN;

let sessionId: string | null = null;

/**
 * Initialize MCP session and get session ID
 */
async function initializeMCPSession(): Promise<boolean> {
  if (!MCP_ENDPOINT || !MCP_SESSION_TOKEN) {
    console.error("Missing MCP_ENDPOINT or MCP_SESSION_TOKEN");
    return false;
  }

  try {
    const headers = createMCPHeaders(MCP_SESSION_TOKEN);
    const initPayload = createMCPInitPayload();

    const response = await axios.post(`${MCP_ENDPOINT}/mcp`, initPayload, {
      headers,
    });

    // Get session ID from headers
    sessionId = extractSessionId(response.headers, MCP_SESSION_TOKEN);

    console.log(
      `MCP session initialized with ID: ${sessionId?.slice(0, 20)}...`
    );
    return true;
  } catch (error: any) {
    console.error(
      "Failed to initialize MCP session:",
      error.response?.data || error.message
    );
    return false;
  }
}

export async function queryMCP(userPrompt: string): Promise<string> {
  try {
    // Initialize session if not already done
    if (!sessionId) {
      const initialized = await initializeMCPSession();
      if (!initialized) {
        return "Failed to connect to MCP server. Please check your session token.";
      }
    }

    // For now, since the MCP server only has Topcoder-specific tools,
    // we'll provide a fallback response for the educational use case
    return `I'm Professor Al Gorithm! I'd love to help you solve coding problems using the Algorithm Design Canvas.

The MCP server is connected and has these available tools:
- query-tc-challenges: To find relevant Topcoder challenges for practice
- query-tc-skills: To explore required skills for challenges

Let's start with the Algorithm Design Canvas approach:

1. **Constraints**: What are the input/output requirements and constraints?
2. **Ideas**: What solution approaches can we brainstorm?
3. **Test Cases**: What test cases should we create to validate our approach?
4. **Code**: How do we implement and structure our solution?

What coding problem would you like to work on today?`;
  } catch (error: any) {
    console.error("Error querying MCP:", error.response?.data || error.message);
    return "I'm having trouble connecting to the tutoring system. Let's work through your problem step by step manually using the Algorithm Design Canvas approach!";
  }
}
