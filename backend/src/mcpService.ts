import axios from "axios";
import dotenv from "dotenv";
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
 * Call a specific MCP tool with parameters
 */
async function callMCPTool(toolName: string, params: any): Promise<any> {
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
      return response.data.result;
    } else if (response.data && response.data.error) {
      console.error(`MCP tool error for ${toolName}:`, response.data.error);
      return null;
    }
    return response.data;
  } catch (error: any) {
    console.error(
      `Error calling MCP tool ${toolName}:`,
      error.response?.data || error.message
    );
    return null;
  }
}

/**
 * Format challenge data for educational presentation
 */
function formatChallengesForLearning(challengeData: any): string {
  if (!challengeData || typeof challengeData !== "string") {
    return "• Real Topcoder challenges available - processing data...";
  }

  try {
    // Parse SSE format: "event: message\ndata: {json data}"
    const lines = challengeData.split("\n");
    const dataLine = lines.find((line) => line.startsWith("data: "));
    if (!dataLine) return "• Challenge data processing...";

    const jsonData = JSON.parse(dataLine.substring(6)); // Remove "data: "
    const result = JSON.parse(jsonData.result.content[0].text);

    if (result.data && Array.isArray(result.data)) {
      return result.data
        .slice(0, 3)
        .map((challenge: any) => {
          const track = challenge.track || "Development";
          const status = challenge.status || "Active";
          return `• **${challenge.name}** (${track} - ${status})`;
        })
        .join("\n");
    }

    return "• Real Topcoder challenges found - formatting...";
  } catch (error) {
    console.error("Error parsing challenge data:", error);
    return "• Live Topcoder challenges available for practice";
  }
}

/**
 * Format skills data for educational presentation
 */
function formatSkillsForLearning(skillsData: any): string {
  if (!skillsData || typeof skillsData !== "string") {
    return "• Programming fundamentals, algorithmic thinking, problem solving";
  }

  try {
    // Parse SSE format: "event: message\ndata: {json data}"
    const lines = skillsData.split("\n");
    const dataLine = lines.find((line) => line.startsWith("data: "));
    if (!dataLine) return "• Skill data processing...";

    const jsonData = JSON.parse(dataLine.substring(6)); // Remove "data: "
    const result = JSON.parse(jsonData.result.content[0].text);

    if (result.data && Array.isArray(result.data)) {
      return result.data
        .slice(0, 5)
        .map((skill: any) => {
          const category = skill.category?.name || "General";
          return `• **${skill.name}** (${category})`;
        })
        .join("\n");
    }

    return "• Real skill categories from Topcoder database";
  } catch (error) {
    console.error("Error parsing skills data:", error);
    return "• Algorithm Design, Data Structures, Problem Solving, Code Optimization, System Design";
  }
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
  } catch (error: any) {
    console.error("Error querying MCP:", error.response?.data || error.message);
    return "I'm having trouble connecting to the tutoring system right now, but let's work through your problem step by step using the Algorithm Design Canvas approach! What coding problem would you like to tackle?";
  }
}
