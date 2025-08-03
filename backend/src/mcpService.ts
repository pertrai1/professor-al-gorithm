/**
 * Main MCP service with educational functionality
 */

import { callMCPTool, initializeMCPSession, getSessionId } from "./mcpCore";
import {
  parseSSEData,
  formatChallengesForLearning,
  formatSkillsForLearning,
} from "./mcpFormatters";
import {
  validateMCPParams,
  hasValidData,
  filterValidItems,
  createFallbackContent,
} from "./mcpHelpers";
import { Challenge, Skill, MCPResponse } from "./mcpTypes";

/**
 * Process user query with MCP integration
 */
async function processUserQuery(userPrompt: string): Promise<string> {
  if (!userPrompt || typeof userPrompt !== "string") {
    return "I need a question or problem to help you with. What would you like to learn about algorithms?";
  }

  const sanitizedPrompt = userPrompt.trim().slice(0, 1000);
  if (sanitizedPrompt.length === 0) {
    return "Please provide a specific question or problem you'd like help with!";
  }

  if (!getSessionId()) {
    const initialized = await initializeMCPSession();
    if (!initialized) {
      return createFallbackResponse(sanitizedPrompt);
    }
  }

  const [challengeResponse, skillsResponse] = await Promise.all([
    callMCPTool("query-tc-challenges", { limit: 3, difficulty: "easy" }),
    callMCPTool("query-tc-skills", { category: "algorithms", limit: 5 }),
  ]);

  if (
    !hasValidData(challengeResponse, parseSSEData) &&
    !hasValidData(skillsResponse, parseSSEData)
  ) {
    return createFallbackResponse(sanitizedPrompt);
  }

  return createSuccessResponse(challengeResponse, skillsResponse);
}

/**
 * Create fallback educational response
 */
function createFallbackResponse(userPrompt: string): string {
  const challenges = createFallbackContent("challenges");
  const skills = createFallbackContent("skills");

  return `I'm Professor Al Gorithm! While I'm having connection issues with the live database, I can still help you learn algorithms using the Design Canvas approach.

🎯 **Sample Practice Challenges:**
${challenges.join("\n")}

📚 **Core Skills to Master:**
${skills.join("\n")}

Let's work through your problem: "${userPrompt.slice(0, 100)}${userPrompt.length > 100 ? "..." : ""}"

Using the Algorithm Design Canvas:
1. **Constraints** - What are the input/output requirements?
2. **Ideas** - What approaches can we consider?
3. **Test Cases** - What scenarios should we test?
4. **Code** - How do we structure the solution?

What specific aspect would you like to start with?`;
}

/**
 * Create success response with MCP data
 */
function createSuccessResponse(
  challengeResponse: MCPResponse | null,
  skillsResponse: MCPResponse | null
): string {
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
}

// Enhanced API functions for Express endpoints
export async function processQuery(
  userPrompt: string,
  _conversationId?: string
): Promise<string> {
  try {
    return await processUserQuery(userPrompt);
  } catch (error: unknown) {
    const axiosError = error as {
      response?: { data?: unknown };
      message?: string;
    };
    console.error(
      "Error querying MCP:",
      axiosError.response?.data || axiosError.message
    );
    return createFallbackResponse(userPrompt);
  }
}

export async function getChallenges(params: {
  limit: number;
  difficulty: string;
}): Promise<Challenge[]> {
  try {
    const validatedParams = validateMCPParams(params);

    if (!getSessionId()) {
      const initialized = await initializeMCPSession();
      if (!initialized) {
        console.error("Failed to initialize MCP session for challenges");
        return [];
      }
    }

    const response = await callMCPTool("query-tc-challenges", validatedParams);

    if (!response) {
      console.warn("No response from MCP server for challenges");
      return [];
    }

    const parsedData = parseSSEData(response);
    const challenges = (parsedData as Challenge[]) || [];

    return filterValidItems(challenges);
  } catch (error) {
    console.error("Error fetching challenges:", error);
    return [];
  }
}

export async function getSkills(params: {
  limit: number;
  category: string;
}): Promise<Skill[]> {
  try {
    const validatedParams = validateMCPParams(params);

    if (!getSessionId()) {
      const initialized = await initializeMCPSession();
      if (!initialized) {
        console.error("Failed to initialize MCP session for skills");
        return [];
      }
    }

    const response = await callMCPTool("query-tc-skills", validatedParams);

    if (!response) {
      console.warn("No response from MCP server for skills");
      return [];
    }

    const parsedData = parseSSEData(response);
    const skills = (parsedData as Skill[]) || [];

    return filterValidItems(skills);
  } catch (error) {
    console.error("Error fetching skills:", error);
    return [];
  }
}

export { processUserQuery as queryMCP };
