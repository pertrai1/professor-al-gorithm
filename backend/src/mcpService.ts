import axios from "axios";
import dotenv from "dotenv";
import {
  createMCPHeaders,
  createMCPInitPayload,
  extractSessionId,
  createMCPSessionHeaders,
} from "./mcpUtils";

dotenv.config();

// Type definitions for MCP responses
interface MCPToolParams {
  [key: string]: string | number | boolean;
}

interface MCPResponse {
  result?: MCPResult;
  error?: MCPError;
  jsonrpc: string;
  id: number;
}

interface MCPResult {
  content?: MCPContent[];
  structuredContent?: StructuredContent;
}

interface MCPContent {
  type: string;
  text: string;
}

interface MCPError {
  code: number;
  message: string;
}

interface StructuredContent {
  page: number;
  pageSize: number;
  total: number;
  data: Challenge[] | Skill[];
}

interface Challenge {
  id: string;
  name: string;
  track?: string;
  status?: string;
  description?: string;
  typeId?: string;
  trackId?: string;
  skills?: ChallengeSkill[];
  // Add other challenge properties as needed
}

interface Skill {
  id: string;
  name: string;
  description?: string;
  category?: SkillCategory;
}

interface SkillCategory {
  id: string;
  name: string;
  description?: string;
}

interface ChallengeSkill {
  name: string;
  id: string;
  category: SkillCategory;
}

const MCP_ENDPOINT = process.env.MCP_ENDPOINT;
const MCP_SESSION_TOKEN = process.env.MCP_SESSION_TOKEN;

let sessionId: string | null = null;

/**
 * Call a specific MCP tool with parameters
 */
async function callMCPTool(
  toolName: string,
  params: MCPToolParams
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
    });
    console.log(
      `Raw MCP response for ${toolName}:`,
      JSON.stringify(response.data, null, 2)
    );

    if (response.data && response.data.result) {
      return response.data;
    } else if (response.data && response.data.error) {
      console.error(`MCP tool error for ${toolName}:`, response.data.error);
      return null;
    }
    return response.data;
  } catch (error: unknown) {
    const axiosError = error as {
      response?: { data?: unknown };
      message?: string;
    };
    console.error(
      `Error calling MCP tool ${toolName}:`,
      axiosError.response?.data || axiosError.message
    );
    return null;
  }
}

/**
 * Parse SSE format data and extract the structured data array
 */
function parseSSEData(sseData: unknown): Challenge[] | Skill[] | null {
  if (!sseData || typeof sseData !== "string") {
    return null;
  }

  try {
    // Parse SSE format: "event: message\ndata: {json data}"
    const lines = sseData.split("\n");
    const dataLine = lines.find((line) => line.startsWith("data: "));
    if (!dataLine) return null;

    const jsonData = JSON.parse(dataLine.substring(6)); // Remove "data: "
    const result = JSON.parse(jsonData.result.content[0].text);

    if (result.data && Array.isArray(result.data)) {
      return result.data;
    }

    return null;
  } catch (error) {
    console.error("Error parsing SSE data:", error);
    return null;
  }
}

/**
 * Format challenge data for educational presentation
 */
function formatChallengesForLearning(
  challengeData: MCPResponse | null
): string {
  const parsedData = parseSSEData(challengeData);

  if (!parsedData) {
    return "• Real Topcoder challenges available - processing data...";
  }

  return (parsedData as Challenge[])
    .slice(0, 3)
    .map((challenge: Challenge) => {
      const track = challenge.track || "Development";
      const status = challenge.status || "Active";
      return `• **${challenge.name}** (${track} - ${status})`;
    })
    .join("\n");
}

/**
 * Format skills data for educational presentation
 */
function formatSkillsForLearning(skillsData: MCPResponse | null): string {
  const parsedData = parseSSEData(skillsData);

  if (!parsedData) {
    return "• Algorithm Design\n• Data Structures\n• Problem Solving\n• Code Optimization\n• System Design";
  }

  return (parsedData as Skill[])
    .slice(0, 5)
    .map((skill: Skill) => {
      const category = skill.category?.name || "General";
      return `• **${skill.name}** (${category})`;
    })
    .join("\n");
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

// Enhanced API functions for Express endpoints
export async function processUserQuery(userPrompt: string, conversationId?: string): Promise<string> {
  // Add conversation context logic here in future
  return await queryMCP(userPrompt);
}

export async function getChallenges(params: { limit: number; difficulty: string }): Promise<Challenge[]> {
  try {
    if (!sessionId) {
      const initialized = await initializeMCPSession();
      if (!initialized) {
        return [];
      }
    }

    const response = await callMCPTool("query-tc-challenges", {
      limit: params.limit,
      difficulty: params.difficulty,
    });

    const parsedData = parseSSEData(response);
    return (parsedData as Challenge[]) || [];
  } catch (error) {
    console.error("Error fetching challenges:", error);
    return [];
  }
}

export async function getSkills(params: { limit: number; category: string }): Promise<Skill[]> {
  try {
    if (!sessionId) {
      const initialized = await initializeMCPSession();
      if (!initialized) {
        return [];
      }
    }

    const response = await callMCPTool("query-tc-skills", {
      limit: params.limit,
      category: params.category,
    });

    const parsedData = parseSSEData(response);
    return (parsedData as Skill[]) || [];
  } catch (error) {
    console.error("Error fetching skills:", error);
    return [];
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

    // Query Topcoder challenges to get real problems for the student
    console.log("Fetching challenges...");
    const challengeResponse = await callMCPTool("query-tc-challenges", {
      limit: 3,
      difficulty: "easy",
    });
    console.log(
      "Challenge response:",
      JSON.stringify(challengeResponse, null, 2)
    );

    // Query skills to understand what we can teach
    console.log("Fetching skills...");
    const skillsResponse = await callMCPTool("query-tc-skills", {
      category: "algorithms",
      limit: 5,
    });
    console.log("Skills response:", JSON.stringify(skillsResponse, null, 2));

    return `I'm Professor Al Gorithm! I've connected to the Topcoder database and found some excellent problems for you.

🎯 **Available Practice Challenges:**
${formatChallengesForLearning(challengeResponse)}

📚 **Skills We Can Focus On:**
${formatSkillsForLearning(skillsResponse)}

Let's use the Algorithm Design Canvas approach to tackle one of these:

1. **Constraints**: Define input/output requirements and performance needs
2. **Ideas**: Brainstorm multiple solution approaches
3. **Test Cases**: Create comprehensive test scenarios
4. **Code**: Structure the implementation step-by-step

Which challenge interests you, or would you prefer me to select one based on your current skill level?`;
  } catch (error: unknown) {
    const axiosError = error as {
      response?: { data?: unknown };
      message?: string;
    };
    console.error(
      "Error querying MCP:",
      axiosError.response?.data || axiosError.message
    );
    return "I'm having trouble connecting to the tutoring system right now, but let's work through your problem step by step using the Algorithm Design Canvas approach! What coding problem would you like to tackle?";
  }
}
