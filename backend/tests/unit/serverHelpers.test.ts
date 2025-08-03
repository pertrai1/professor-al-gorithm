/**
 * Unit Tests for Server Helper Functions
 * Module 7: Testing & Debugging Implementation
 */

import {
  validateLimit,
  validateDifficulty,
  validatePhase,
  createErrorResponse,
  getNextPhase,
} from "../../src/serverHelpers";

describe("Server Helper Functions", () => {
  describe("validateLimit", () => {
    test("should accept valid numeric strings", () => {
      expect(validateLimit("5")).toBe(5);
      expect(validateLimit("10")).toBe(10);
      expect(validateLimit("50")).toBe(50);
    });

    test("should accept valid numbers", () => {
      expect(validateLimit(5)).toBe(5);
      expect(validateLimit(10)).toBe(10);
    });

    test("should reject negative numbers", () => {
      expect(() => validateLimit("-1")).toThrow(
        "Limit must be between 1 and 100"
      );
      expect(() => validateLimit(-5)).toThrow(
        "Limit must be between 1 and 100"
      );
    });

    test("should reject numbers over 100", () => {
      expect(() => validateLimit("101")).toThrow(
        "Limit must be between 1 and 100"
      );
      expect(() => validateLimit(500)).toThrow(
        "Limit must be between 1 and 100"
      );
    });

    test("should reject zero", () => {
      expect(() => validateLimit("0")).toThrow(
        "Limit must be between 1 and 100"
      );
      expect(() => validateLimit(0)).toThrow("Limit must be between 1 and 100");
    });

    test("should reject non-numeric strings", () => {
      expect(() => validateLimit("abc")).toThrow(
        "Limit must be a valid number"
      );
      expect(() => validateLimit("5.5")).toThrow(
        "Limit must be a valid number"
      );
    });

    test("should handle undefined with default", () => {
      expect(validateLimit(undefined)).toBe(10);
    });
  });

  describe("validateDifficulty", () => {
    test("should accept valid difficulties", () => {
      expect(validateDifficulty("easy")).toBe("easy");
      expect(validateDifficulty("medium")).toBe("medium");
      expect(validateDifficulty("hard")).toBe("hard");
    });

    test("should reject invalid difficulties", () => {
      expect(() => validateDifficulty("impossible")).toThrow(
        "Difficulty must be easy, medium, or hard"
      );
      expect(() => validateDifficulty("beginner")).toThrow(
        "Difficulty must be easy, medium, or hard"
      );
    });

    test("should handle undefined with default", () => {
      expect(validateDifficulty(undefined)).toBe("easy");
    });

    test("should be case sensitive", () => {
      expect(() => validateDifficulty("Easy")).toThrow(
        "Difficulty must be easy, medium, or hard"
      );
      expect(() => validateDifficulty("EASY")).toThrow(
        "Difficulty must be easy, medium, or hard"
      );
    });
  });

  describe("validatePhase", () => {
    test("should accept valid phases", () => {
      expect(validatePhase("constraints")).toBe("constraints");
      expect(validatePhase("ideas")).toBe("ideas");
      expect(validatePhase("tests")).toBe("tests");
      expect(validatePhase("code")).toBe("code");
    });

    test("should reject invalid phases", () => {
      expect(() => validatePhase("invalid")).toThrow("Invalid phase");
      expect(() => validatePhase("planning")).toThrow("Invalid phase");
    });

    test("should be case sensitive", () => {
      expect(() => validatePhase("Constraints")).toThrow("Invalid phase");
      expect(() => validatePhase("IDEAS")).toThrow("Invalid phase");
    });
  });

  describe("getNextPhase", () => {
    test("should return correct next phases", () => {
      expect(getNextPhase("constraints")).toBe("ideas");
      expect(getNextPhase("ideas")).toBe("tests");
      expect(getNextPhase("tests")).toBe("code");
      expect(getNextPhase("code")).toBeNull();
    });

    test("should handle invalid phases", () => {
      expect(getNextPhase("invalid" as any)).toBeNull();
    });
  });

  describe("createErrorResponse", () => {
    test("should create timeout error response", () => {
      const timeoutError = new Error("Request timeout");
      const response = createErrorResponse(timeoutError, 30000);

      expect(response.error).toBe("Request timed out");
      expect(response.code).toBe("TIMEOUT");
      expect(response.processingTime).toBe(30000);
      expect(response.timestamp).toBeDefined();
    });

    test("should create fetch error response", () => {
      const fetchError = new Error("Failed to fetch from MCP server");
      const response = createErrorResponse(fetchError, 1000);

      expect(response.error).toBe("Unable to fetch data from MCP server");
      expect(response.code).toBe("FETCH_ERROR");
      expect(response.processingTime).toBe(1000);
      expect(response.timestamp).toBeDefined();
    });

    test("should create generic error response", () => {
      const genericError = new Error("Something went wrong");
      const response = createErrorResponse(genericError, 500);

      expect(response.error).toBe(
        "An error occurred while processing your request"
      );
      expect(response.code).toBe("PROCESSING_ERROR");
      expect(response.processingTime).toBe(500);
      expect(response.timestamp).toBeDefined();
    });

    test("should include original error message in development", () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = "development";

      const error = new Error("Detailed error message");
      const response = createErrorResponse(error, 100);

      expect(response).toHaveProperty(
        "originalError",
        "Detailed error message"
      );

      process.env.NODE_ENV = originalEnv;
    });

    test("should not include original error message in production", () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = "production";

      const error = new Error("Detailed error message");
      const response = createErrorResponse(error, 100);

      expect(response).not.toHaveProperty("originalError");

      process.env.NODE_ENV = originalEnv;
    });
  });
});
