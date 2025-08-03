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
export function validateLimit(limit: string | number | undefined): number {
  if (limit === undefined) {
    return 10; // Default value
  }

  let parsedLimit: number;
  if (typeof limit === "string") {
    // Check for decimal numbers
    if (limit.includes(".")) {
      throw new Error("Limit must be a valid number");
    }
    parsedLimit = parseInt(limit, 10);
  } else {
    parsedLimit = limit;
  }

  if (isNaN(parsedLimit)) {
    throw new Error("Limit must be a valid number");
  }
  if (parsedLimit < 1 || parsedLimit > 100) {
    throw new Error("Limit must be between 1 and 100");
  }
  return parsedLimit;
}

/**
 * Validate difficulty parameter
 */
export function validateDifficulty(difficulty: string | undefined): string {
  if (difficulty === undefined) {
    return "easy"; // Default value
  }

  const validDifficulties = ["easy", "medium", "hard"];
  if (!validDifficulties.includes(difficulty)) {
    throw new Error("Difficulty must be easy, medium, or hard");
  }
  return difficulty;
}

/**
 * Validate phase parameter
 */
export function validatePhase(phase: string): string {
  const validPhases = ["constraints", "ideas", "tests", "code"];
  if (!validPhases.includes(phase)) {
    throw new Error("Invalid phase");
  }
  return phase;
}

/**
 * Validate category parameter
 */
export function validateCategory(category: string | undefined): string {
  if (category === undefined) {
    return "algorithms"; // Default value
  }

  const validCategories = [
    "algorithms",
    "data-structures",
    "mathematics",
    "implementation",
    "geometry",
    "string-processing",
  ];
  if (!validCategories.includes(category)) {
    throw new Error("Invalid category");
  }
  return category;
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
  timestamp: string;
  originalError?: string;
} {
  const isTimeout = isTimeoutError(error);
  const isFetchError =
    error.message.includes("fetch") || error.message.includes("MCP");

  let errorMessage: string;
  let errorCode: string;

  if (isTimeout) {
    errorMessage = "Request timed out";
    errorCode = "TIMEOUT";
  } else if (isFetchError) {
    errorMessage = "Unable to fetch data from MCP server";
    errorCode = "FETCH_ERROR";
  } else {
    errorMessage = "An error occurred while processing your request";
    errorCode = "PROCESSING_ERROR";
  }

  const response: {
    error: string;
    code: string;
    processingTime: number;
    timestamp: string;
    originalError?: string;
  } = {
    error: errorMessage,
    code: errorCode,
    processingTime,
    timestamp: new Date().toISOString(),
  };

  // Include original error in development
  if (process.env.NODE_ENV === "development") {
    response.originalError = error.message;
  }

  return response;
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
  const phases = ["constraints", "ideas", "tests", "code"];
  const currentIndex = phases.indexOf(currentPhase);
  if (currentIndex === -1) {
    return null;
  }
  return currentIndex < phases.length - 1 ? phases[currentIndex + 1] : null;
}
