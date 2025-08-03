/**
 * Additional server utilities to keep functions simple
 */

import { processQuery } from "./mcpService";

/**
 * Validate canvas input fields
 */
export function validateCanvasInput(
  phase: string,
  content: string,
  challengeId?: string
): string {
  if (!phase || typeof phase !== "string") {
    throw new Error("Phase is required and must be a string");
  }

  if (!content || typeof content !== "string") {
    throw new Error("Content is required and must be a string");
  }

  if (content.length > 5000) {
    throw new Error("Content too long. Please limit to 5000 characters.");
  }

  if (challengeId && typeof challengeId !== "string") {
    throw new Error("Challenge ID must be a string");
  }

  const validPhases = ["constraints", "ideas", "test-cases", "code"];
  if (!validPhases.includes(phase)) {
    throw new Error(`Invalid phase. Must be one of: ${validPhases.join(", ")}`);
  }

  return phase;
}

/**
 * Simple canvas phase processor
 */
export async function simpleProcessCanvasPhase(
  phase: string,
  content: string,
  challengeId?: string
): Promise<string> {
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
}
