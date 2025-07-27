/**
 * Shared utilities for MCP (Model Context Protocol) operations
 */

/**
 * Parse SSE (Server-Sent Events) response from MCP server
 * @param sseText - Raw SSE response text
 * @returns Parsed JSON object or null if parsing fails
 */
export function parseSSEResponse(sseText: string): any {
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
 * Create standard MCP headers for requests
 * @param sessionToken - MCP session token
 * @returns Headers object for axios requests
 */
export function createMCPHeaders(sessionToken: string) {
  return {
    Accept: "application/json, text/event-stream",
    "Content-Type": "application/json",
    "X-MCP-Session": sessionToken,
  };
}

/**
 * Create MCP session headers (includes session ID)
 * @param sessionToken - MCP session token
 * @param sessionId - MCP session ID (optional)
 * @returns Headers object for axios requests
 */
export function createMCPSessionHeaders(
  sessionToken: string,
  sessionId?: string
) {
  const headers = createMCPHeaders(sessionToken);
  if (sessionId) {
    return {
      ...headers,
      "mcp-session-id": sessionId,
    };
  }
  return headers;
}

/**
 * Standard MCP initialization payload
 * @param clientName - Name of the MCP client
 * @param clientVersion - Version of the MCP client
 * @returns MCP initialize payload
 */
export function createMCPInitPayload(
  clientName: string = "professor-al-gorithm",
  clientVersion: string = "1.0.0"
) {
  return {
    jsonrpc: "2.0" as const,
    method: "initialize",
    params: {
      protocolVersion: "2024-11-05",
      capabilities: {
        tools: {},
      },
      clientInfo: {
        name: clientName,
        version: clientVersion,
      },
    },
    id: 1,
  };
}

/**
 * Extract session ID from response headers
 * @param headers - Response headers
 * @param fallbackToken - Fallback session token to use as session ID
 * @returns Session ID or fallback token
 */
export function extractSessionId(headers: any, fallbackToken: string): string {
  return (
    headers["mcp-session-id"] || headers["x-mcp-session-id"] || fallbackToken
  );
}
