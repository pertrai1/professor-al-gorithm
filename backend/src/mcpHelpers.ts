/**
 * Helper functions for MCP service to reduce complexity
 */

import { MCPResponse } from "./mcpTypes";

/**
 * Delay execution for specified milliseconds
 */
export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

/**
 * Validate MCP parameters
 */
export function validateMCPParams(params: {
  limit?: number;
  difficulty?: string;
  category?: string;
}): { limit: number; difficulty?: string; category?: string } {
  const validatedParams: {
    limit: number;
    difficulty?: string;
    category?: string;
  } = {
    limit: Math.max(1, Math.min(params.limit || 5, 50)),
  };

  if (params.difficulty) {
    validatedParams.difficulty = ["easy", "medium", "hard"].includes(
      params.difficulty
    )
      ? params.difficulty
      : "easy";
  }

  if (params.category) {
    validatedParams.category = params.category || "algorithms";
  }

  return validatedParams;
}

/**
 * Check if response has valid data
 */
export function hasValidData(
  response: MCPResponse | null,
  parseData: (data: MCPResponse | null) => unknown[] | null
): boolean {
  return response !== null && parseData(response) !== null;
}

/**
 * Filter and validate challenge/skill data
 */
export function filterValidItems<T extends { id: string; name: string }>(
  items: T[]
): T[] {
  return items.filter(
    (item) =>
      item && typeof item.id === "string" && typeof item.name === "string"
  );
}

/**
 * Create fallback educational content
 */
export function createFallbackContent(type: "challenges" | "skills"): string[] {
  const fallbacks = {
    challenges: [
      "**Two Sum Problem** - Find two numbers in an array that add up to a target",
      "**Valid Parentheses** - Check if parentheses are properly balanced",
      "**Maximum Subarray** - Find the contiguous subarray with largest sum",
    ],
    skills: [
      "**Array Manipulation** - Working with arrays and indices",
      "**Hash Tables** - Fast lookups and storage",
      "**Two Pointers** - Efficient array traversal technique",
      "**Dynamic Programming** - Breaking down complex problems",
      "**Recursion** - Solving problems by breaking them down",
    ],
  };

  return fallbacks[type];
}
