/**
 * Core MCP functionality - session management and tool calls
 */

import axios from "axios";
import dotenv from "dotenv";

import { delay } from "./mcpHelpers";
import { MCPToolParams, MCPResponse } from "./mcpTypes";
import {
  createMCPHeaders,
  createMCPInitPayload,
  extractSessionId,
  createMCPSessionHeaders,
} from "./mcpUtils";

dotenv.config();

const MCP_ENDPOINT = process.env.MCP_ENDPOINT;
const MCP_SESSION_TOKEN = process.env.MCP_SESSION_TOKEN;

let sessionId: string | null = null;

/**
 * Handle MCP tool response
 */
function handleMCPResponse(
  response: { status: number; data: unknown },
  toolName: string
): MCPResponse | null {
  console.log(
    `Raw MCP response for ${toolName}:`,
    JSON.stringify(response.data, null, 2)
  );

  if (response.status >= 400) {
    console.warn(`MCP server returned ${response.status} for ${toolName}`);
    return null;
  }

  if (
    response.data &&
    typeof response.data === "object" &&
    response.data !== null
  ) {
    const data = response.data as { result?: unknown; error?: unknown };
    if (data.result) {
      return response.data as MCPResponse;
    }

    if (data.error) {
      console.error(`MCP tool error for ${toolName}:`, data.error);
      return null;
    }
  }

  return response.data as MCPResponse;
}

/**
 * Handle MCP tool errors
 */
function handleMCPError(
  error: { code?: string; response?: { data?: unknown }; message?: string },
  toolName: string
): void {
  if (error.code === "ECONNABORTED") {
    console.error(`Timeout calling MCP tool ${toolName}`);
  } else if (error.code === "ECONNREFUSED") {
    console.error(`Connection refused to MCP server for ${toolName}`);
  } else {
    console.error(
      `Error calling MCP tool ${toolName}:`,
      error.response?.data || error.message
    );
  }
}

/**
 * Check if should retry MCP call
 */
function shouldRetry(error: { code?: string }, retryCount: number): boolean {
  return retryCount < 1 && error.code !== "ECONNABORTED";
}

/**
 * Handle session reinitialization
 */
async function handleSessionReinitialization(
  toolName: string,
  params: MCPToolParams,
  retryCount: number
): Promise<MCPResponse | null> {
  console.log("Attempting to reinitialize MCP session...");
  sessionId = null;
  const initialized = await initializeMCPSession();
  if (initialized) {
    return await callMCPTool(toolName, params, retryCount + 1);
  }
  return null;
}

/**
 * Call a specific MCP tool with parameters
 */
export async function callMCPTool(
  toolName: string,
  params: MCPToolParams,
  retryCount: number = 0
): Promise<MCPResponse | null> {
  if (!MCP_ENDPOINT || !MCP_SESSION_TOKEN || !sessionId) {
    throw new Error("MCP session not properly initialized");
  }

  const payload = {
    jsonrpc: "2.0",
    id: Date.now(),
    method: "tools/call",
    params: {
      name: toolName,
      arguments: params,
    },
  };

  const headers = createMCPSessionHeaders(MCP_SESSION_TOKEN, sessionId);

  try {
    const response = await axios.post(`${MCP_ENDPOINT}/mcp`, payload, {
      headers,
      timeout: 30000,
      validateStatus: (status) => status < 500,
    });

    const result = handleMCPResponse(response, toolName);

    // Handle session expiry
    if (response.status === 401 && retryCount < 1) {
      return await handleSessionReinitialization(toolName, params, retryCount);
    }

    return result;
  } catch (error: unknown) {
    const axiosError = error as {
      code?: string;
      response?: { data?: unknown; status?: number };
      message?: string;
    };

    handleMCPError(axiosError, toolName);

    if (shouldRetry(axiosError, retryCount)) {
      console.log(`Retrying MCP tool ${toolName}...`);
      await delay(1000);
      return await callMCPTool(toolName, params, retryCount + 1);
    }

    return null;
  }
}

/**
 * Initialize MCP session and get session ID
 */
export async function initializeMCPSession(): Promise<boolean> {
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

    sessionId = extractSessionId(response.headers, MCP_SESSION_TOKEN);

    console.log(
      `MCP session initialized with ID: ${sessionId?.slice(0, 20)}...`
    );
    return true;
  } catch (error: unknown) {
    const axiosError = error as {
      response?: { data?: unknown };
      message?: string;
    };
    console.error(
      "Failed to initialize MCP session:",
      axiosError.response?.data || axiosError.message
    );
    return false;
  }
}

/**
 * Get current session ID
 */
export function getSessionId(): string | null {
  return sessionId;
}
