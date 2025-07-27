import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

const MCP_ENDPOINT = process.env.MCP_ENDPOINT;
const MCP_SESSION_TOKEN = process.env.MCP_SESSION_TOKEN;

let sessionId: string | null = null;

/**
 * Parse SSE (Server-Sent Events) response
 */
function parseSSEResponse(sseText: string): any {
  const lines = sseText.trim().split("\n");
  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const dataStr = line.substring(6);
      if (dataStr.trim()) {
        try {
          return JSON.parse(dataStr);
        } catch (e) {
          console.log("Failed to parse JSON:", dataStr);
        }
      }
    }
  }
  return null;
}

/**
 * Initialize MCP session and get session ID
 */
async function initializeMCPSession(): Promise<boolean> {
  if (!MCP_ENDPOINT || !MCP_SESSION_TOKEN) {
    console.error("Missing MCP_ENDPOINT or MCP_SESSION_TOKEN");
    return false;
  }

  try {
    const headers = {
      Accept: "application/json, text/event-stream",
      "Content-Type": "application/json",
      "X-MCP-Session": MCP_SESSION_TOKEN,
    };

    const initPayload = {
      jsonrpc: "2.0",
      method: "initialize",
      params: {
        protocolVersion: "2024-11-05",
        capabilities: {
          tools: {},
        },
        clientInfo: {
          name: "professor-al-gorithm",
          version: "1.0.0",
        },
      },
      id: 1,
    };

    const response = await axios.post(`${MCP_ENDPOINT}/mcp`, initPayload, {
      headers,
    });

    // Get session ID from headers
    sessionId =
      response.headers["mcp-session-id"] ||
      response.headers["x-mcp-session-id"];

    if (!sessionId) {
      // Fallback to using session token as session ID
      sessionId = MCP_SESSION_TOKEN;
    }

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
