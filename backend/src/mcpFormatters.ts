/**
 * Formatting utilities for MCP responses
 */

import { MCPResponse, Challenge, Skill } from "./mcpTypes";

/**
 * Parse SSE format data and extract the structured data array
 */
export function parseSSEData(sseData: unknown): Challenge[] | Skill[] | null {
  if (!sseData || typeof sseData !== "string") {
    return null;
  }

  try {
    const lines = sseData.split("\n");
    const dataLine = lines.find((line) => line.startsWith("data: "));
    if (!dataLine) return null;

    const jsonData = JSON.parse(dataLine.substring(6));
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
export function formatChallengesForLearning(
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
export function formatSkillsForLearning(
  skillsData: MCPResponse | null
): string {
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
