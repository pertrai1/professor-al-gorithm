/**
 * Helper functions for server endpoints to reduce complexity
 */

import { processQuery } from "./mcpService";

/**
 * Create timeout promise
 */
export function createTimeoutPromise(timeoutMs: number): Promise<never> {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error("Request timeout")), timeoutMs);
  });
}

/**
 * Validate input parameters
 */
export function validateLimit(limit: string | number): number {
  const parsedLimit = typeof limit === "string" ? parseInt(limit) : limit;
  if (isNaN(parsedLimit) || parsedLimit < 1 || parsedLimit > 50) {
    throw new Error("Limit must be a number between 1 and 50");
  }
  return parsedLimit;
}

/**
 * Validate difficulty parameter
 */
export function validateDifficulty(difficulty: string): string {
  const validDifficulties = ["easy", "medium", "hard"];
  if (!validDifficulties.includes(difficulty)) {
    throw new Error(
      `Difficulty must be one of: ${validDifficulties.join(", ")}`
    );
  }
  return difficulty;
}

/**
 * Validate phase parameter
 */
export function validatePhase(phase: string): string {
  const validPhases = ["constraints", "ideas", "test-cases", "code"];
  if (!validPhases.includes(phase)) {
    throw new Error(`Invalid phase. Must be one of: ${validPhases.join(", ")}`);
  }
  return phase;
}

/**
 * Check if error is timeout
 */
export function isTimeoutError(error: Error): boolean {
  return error.message === "Request timeout";
}

/**
 * Create error response
 */
export function createErrorResponse(
  error: Error,
  processingTime: number
): {
  error: string;
  code: string;
  message?: string;
  processingTime: number;
} {
  const isTimeout = isTimeoutError(error);

  return {
    error: isTimeout ? "Request timed out" : "Internal server error",
    code: isTimeout ? "TIMEOUT" : "INTERNAL_ERROR",
    message: getErrorMessage(isTimeout),
    processingTime,
  };
}

/**
 * Get appropriate error message
 */
function getErrorMessage(isTimeout: boolean): string {
  return isTimeout
    ? "Request timed out. The system may be busy. Please try again."
    : "Failed to process your request. Please try again.";
}

/**
 * Phase-specific fallback responses
 */
export function getPhaseSpecificFallback(
  phase: string,
  content: string
): string {
  const fallbacks: Record<string, string> = {
    constraints: `Great start on defining constraints! For "${content.slice(0, 50)}...", consider these questions:

• What are the input data types and ranges?
• What should the output format be?
• Are there time/space complexity requirements?
• What edge cases need handling?`,
    ideas: `I can see you're thinking about approaches for "${content.slice(0, 50)}...". Let's explore:

• What's the brute force solution?
• Can we optimize using data structures?
• Are there algorithmic patterns that apply?
• What are the trade-offs between approaches?`,
    "test-cases": `Good work on test cases for "${content.slice(0, 50)}...". Consider adding:

• Basic valid inputs
• Edge cases (empty, single element, boundaries)
• Invalid inputs
• Performance test cases
• Corner cases specific to your problem`,
    code: `Nice implementation planning for "${content.slice(0, 50)}...". Think about:

• Function signature and return type
• Main algorithm steps
• Helper functions needed
• Error handling approach

Remember: I guide your thinking, you write the code!`,
  };

  return (
    fallbacks[phase] ||
    "I'm here to help guide your learning process. What specific aspect would you like to explore?"
  );
}

/**
 * Process canvas phase with error handling
 */
export async function processCanvasPhase(
  phase: string,
  content: string,
  challengeId?: string
): Promise<string> {
  try {
    const phaseInstructions: Record<string, string> = {
      constraints: "analyze the problem constraints and requirements",
      ideas: "evaluate the solution approaches and suggest improvements",
      "test-cases": "review the test cases for completeness and edge cases",
      code: "provide guidance on the implementation structure and approach",
    };

    const instruction =
      phaseInstructions[phase] || "provide educational feedback";
    const challengeContext = challengeId ? ` for challenge ${challengeId}` : "";

    const prompt = `As Professor Al Gorithm, ${instruction}${challengeContext}. Student submission: ${content}`;

    const response = await processQuery(prompt);

    // Ensure response is educational and doesn't provide complete solutions
    if (response.includes("```") && phase !== "code") {
      return (
        "I see you're thinking about implementation! Let's focus on the current phase first. " +
        response.replace(
          /```[\s\S]*?```/g,
          "[Code examples removed - focus on current phase]"
        )
      );
    }

    return response;
  } catch (error) {
    console.error("Error in processCanvasPhase:", error);
    return getPhaseSpecificFallback(phase, content);
  }
}

/**
 * Get next phase in canvas progression
 */
export function getNextPhase(currentPhase: string): string | null {
  const phases = ["constraints", "ideas", "test-cases", "code"];
  const currentIndex = phases.indexOf(currentPhase);
  return currentIndex < phases.length - 1 ? phases[currentIndex + 1] : null;
}
