import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

const MCP_ENDPOINT = process.env.MCP_ENDPOINT;
const MCP_SESSION_TOKEN = process.env.MCP_SESSION_TOKEN;

/**
 * Parse SSE (Server-Sent Events) response
 */
function parseSSEResponse(sseText: string): any {
  const lines = sseText.trim().split("\n");
  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const dataStr = line.substring(6); // Remove 'data: ' prefix
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
 * Complete MCP workflow
 */
export async function testMCPWorkflow(): Promise<void> {
  if (!MCP_ENDPOINT || !MCP_SESSION_TOKEN) {
    console.error("Missing MCP_ENDPOINT or MCP_SESSION_TOKEN");
    return;
  }

  console.log(
    `🔗 Starting MCP workflow with token: ${MCP_SESSION_TOKEN.slice(0, 20)}...`
  );

  let sessionId: string | null = null;

  // Step 1: Initialize session
  try {
    console.log("\n=== Step 1: Initialize Session ===");

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
    console.log("✅ Initialize response:", response.data);

    // Parse SSE response
    const parsedData = parseSSEResponse(response.data);
    if (parsedData) {
      console.log(
        "✅ Parsed initialize data:",
        JSON.stringify(parsedData, null, 2)
      );

      // Look for session ID in response headers
      sessionId =
        response.headers["mcp-session-id"] ||
        response.headers["x-mcp-session-id"];
      if (sessionId) {
        console.log(`✅ Got session ID from headers: ${sessionId}`);
      } else {
        // Fallback to using the session token as session ID
        sessionId = MCP_SESSION_TOKEN;
        console.log(
          `✅ Using session token as session ID: ${sessionId.slice(0, 20)}...`
        );
      }
    }
  } catch (error: any) {
    console.log("❌ Initialize failed:", error.response?.data || error.message);
    return;
  }

  // Step 2: Use session ID for subsequent requests
  if (sessionId) {
    const sessionHeaders = {
      Accept: "application/json, text/event-stream",
      "Content-Type": "application/json",
      "X-MCP-Session": MCP_SESSION_TOKEN,
      "mcp-session-id": sessionId,
    };

    console.log(
      `\n📋 Using session ID: ${sessionId.slice(
        0,
        20
      )}... for subsequent requests`
    );

    // Test: List tools
    try {
      console.log("\n=== Step 2: List Tools ===");

      const toolsPayload = {
        jsonrpc: "2.0",
        method: "tools/list",
        params: {},
        id: 2,
      };

      const response = await axios.post(`${MCP_ENDPOINT}/mcp`, toolsPayload, {
        headers: sessionHeaders,
      });
      console.log("✅ Tools raw response:", response.data);

      const parsedData = parseSSEResponse(response.data);
      if (parsedData) {
        console.log("✅ Tools parsed:", JSON.stringify(parsedData, null, 2));
      }
    } catch (error: any) {
      console.log("❌ Tools failed:", error.response?.data || error.message);
    }

    // Test: Ask method
    try {
      console.log("\n=== Step 3: Ask Method ===");

      const askPayload = {
        jsonrpc: "2.0",
        method: "ask", // This might need to be different
        params: {
          message: "Hello! Can you help me solve a coding problem?",
        },
        id: 3,
      };

      const response = await axios.post(`${MCP_ENDPOINT}/mcp`, askPayload, {
        headers: sessionHeaders,
      });
      console.log("✅ Ask raw response:", response.data);

      const parsedData = parseSSEResponse(response.data);
      if (parsedData) {
        console.log("✅ Ask parsed:", JSON.stringify(parsedData, null, 2));
      }
    } catch (error: any) {
      console.log("❌ Ask failed:", error.response?.data || error.message);
    }
  }

  console.log("\n🎯 Next steps:");
  console.log("1. Get your own session token from the challenge discussion");
  console.log("2. Replace the token in .env file");
  console.log("3. The session workflow is now working!");
}

// Run if executed directly
if (require.main === module) {
  testMCPWorkflow().catch(console.error);
}
