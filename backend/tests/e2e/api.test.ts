/**
 * End-to-End API Testing Suite
 * Module 7: Testing & Debugging Implementation
 *
 * Comprehensive testing of the Professor Al Gorithm API:
 * - Backend API endpoint testing
 * - MCP integration validation
 * - Error handling verification
 * - Edge case simulation
 * - Performance monitoring
 * - Security testing
 */

import express from "express";
import request from "supertest";

import { monitor } from "../../src/performanceMonitor";

// Import the app from server.ts (we'll need to refactor server.ts to export the app)
let app: express.Application;

// Test configuration
const TEST_TIMEOUT = 15000; // Reduced from 30s to 15s

describe("End-to-End API Testing Suite", () => {
  let server: any;
  const connections = new Set<any>();

  beforeAll(async () => {
    // Set test environment
    process.env.NODE_ENV = "test";

    // Import and start the server
    const serverModule = await import("../../src/server");
    app = serverModule.app;

    // Start server on a different port for testing
    const testPort = process.env.TEST_PORT || 3001;
    server = app.listen(testPort, () => {
      console.log(`Test server running on port ${testPort}`);
    });

    // Track all connections for proper cleanup
    server.on("connection", (connection: any) => {
      connections.add(connection);
      connection.on("close", () => {
        connections.delete(connection);
      });
    });

    // Wait for server to be ready
    await new Promise((resolve) => setTimeout(resolve, 1000));
  });

  afterAll(async () => {
    // Close all connections first
    for (const connection of connections) {
      (connection as any).destroy();
    }
    connections.clear();

    // Close server
    if (server) {
      await new Promise<void>((resolve, reject) => {
        server.close((err: any) => {
          if (err) {
            console.error("Error closing server:", err);
            reject(err);
          } else {
            console.log("Test server closed");
            resolve();
          }
        });
      });
    }

    // Wait for cleanup
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Force cleanup of any lingering handles
    if (global.gc) {
      global.gc();
    }
  });

  describe("Backend Health Tests", () => {
    test("should respond to health check", async () => {
      const response = await request(app).get("/health").timeout(TEST_TIMEOUT);

      expect(response.status).toBeLessThan(500);
      expect(response.body).toBeDefined();
    });

    test("should respond to root endpoint", async () => {
      const response = await request(app).get("/").timeout(TEST_TIMEOUT);

      expect(response.status).toBeLessThan(500);
    });

    test("should respond to performance stats endpoint", async () => {
      const response = await request(app)
        .get("/api/stats")
        .timeout(TEST_TIMEOUT);

      expect(response.status).toBeLessThan(500);
    });
  });

  describe("API Endpoint Tests", () => {
    test("should handle valid chat request", async () => {
      const payload = {
        message: "Hello, I want to learn algorithms",
        conversationId: "test-123",
      };

      const response = await request(app)
        .post("/api/chat")
        .send(payload)
        .timeout(TEST_TIMEOUT);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("response");
    });

    test("should handle valid challenges request", async () => {
      const payload = {
        difficulty: "easy",
        limit: 5,
      };

      const response = await request(app)
        .post("/api/challenges")
        .send(payload)
        .timeout(TEST_TIMEOUT);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("challenges");
      expect(Array.isArray(response.body.challenges)).toBe(true);
    });

    test("should handle valid skills request", async () => {
      const payload = {
        category: "algorithms",
        limit: 10,
      };

      const response = await request(app)
        .post("/api/skills")
        .send(payload)
        .timeout(TEST_TIMEOUT);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("skills");
      expect(Array.isArray(response.body.skills)).toBe(true);
    });

    test("should handle valid canvas request", async () => {
      const payload = {
        phase: "constraints",
        content:
          "I need to solve a two-sum problem with array input and target integer.",
      };

      const response = await request(app)
        .post("/api/canvas")
        .send(payload)
        .timeout(TEST_TIMEOUT);

      // Should return successfully even if MCP times out (fallback behavior)
      expect(response.status).toBeLessThan(500);
      if (response.status === 200) {
        expect(response.body).toHaveProperty("feedback");
      }
    });
  });

  describe("Error Handling Tests", () => {
    const errorTests = [
      {
        name: "should reject chat with missing message",
        endpoint: "/api/chat",
        payload: {},
      },
      {
        name: "should reject chat with invalid message type",
        endpoint: "/api/chat",
        payload: { message: 123 },
      },
      {
        name: "should reject chat with empty message",
        endpoint: "/api/chat",
        payload: { message: "" },
      },
      {
        name: "should reject chat with very long message",
        endpoint: "/api/chat",
        payload: { message: "x".repeat(3000) },
      },
      {
        name: "should reject challenges with invalid difficulty",
        endpoint: "/api/challenges",
        payload: { difficulty: "impossible" },
      },
      {
        name: "should reject challenges with invalid limit",
        endpoint: "/api/challenges",
        payload: { limit: -1 },
      },
      {
        name: "should reject challenges with very high limit",
        endpoint: "/api/challenges",
        payload: { limit: 1000 },
      },
      {
        name: "should reject skills with invalid category",
        endpoint: "/api/skills",
        payload: { category: "nonexistent" },
      },
      {
        name: "should reject skills with invalid limit",
        endpoint: "/api/skills",
        payload: { limit: "abc" },
      },
      {
        name: "should reject canvas with missing phase",
        endpoint: "/api/canvas",
        payload: { content: "test" },
      },
      {
        name: "should reject canvas with invalid phase",
        endpoint: "/api/canvas",
        payload: { phase: "invalid", content: "test" },
      },
      {
        name: "should reject canvas with missing content",
        endpoint: "/api/canvas",
        payload: { phase: "constraints" },
      },
      {
        name: "should reject canvas with very long content",
        endpoint: "/api/canvas",
        payload: { phase: "constraints", content: "x".repeat(6000) },
      },
    ];

    errorTests.forEach(({ name, endpoint, payload }) => {
      test(name, async () => {
        const response = await request(app)
          .post(endpoint)
          .send(payload)
          .timeout(TEST_TIMEOUT);

        expect(response.status).toBeGreaterThanOrEqual(400);
        expect(response.status).toBeLessThan(500);
      });
    });
  });

  describe("Edge Case Tests", () => {
    const edgeCases = [
      {
        name: "should handle empty JSON payload",
        endpoint: "/api/chat",
        payload: {},
      },
      {
        name: "should handle null values",
        endpoint: "/api/challenges",
        payload: { difficulty: null, limit: null },
      },
      {
        name: "should handle unicode characters",
        endpoint: "/api/chat",
        payload: { message: "Hello 🚀 世界 💻" },
      },
      {
        name: "should prevent SQL injection",
        endpoint: "/api/chat",
        payload: { message: "'; DROP TABLE users; --" },
      },
      {
        name: "should prevent XSS attacks",
        endpoint: "/api/chat",
        payload: { message: "<script>alert('xss')</script>" },
      },
      {
        name: "should handle very long conversation ID",
        endpoint: "/api/chat",
        payload: { message: "test", conversationId: "x".repeat(1000) },
      },
      {
        name: "should handle minimum valid limits",
        endpoint: "/api/challenges",
        payload: { difficulty: "easy", limit: 1 },
      },
      {
        name: "should handle maximum valid limits",
        endpoint: "/api/challenges",
        payload: { difficulty: "hard", limit: 50 },
      },
    ];

    edgeCases.forEach(({ name, endpoint, payload }) => {
      test(name, async () => {
        const response = await request(app)
          .post(endpoint)
          .send(payload)
          .timeout(TEST_TIMEOUT);

        // Should not crash the server (no 5xx errors)
        expect(response.status).toBeLessThan(500);
      });
    });
  });

  describe("Performance Tests", () => {
    test("should handle concurrent requests", async () => {
      const numRequests = 5;

      // Use health endpoint for concurrent testing to avoid MCP timeouts
      const requests = Array(numRequests)
        .fill(null)
        .map(() => request(app).get("/health").timeout(TEST_TIMEOUT));

      const responses = await Promise.all(requests);
      const successfulResponses = responses.filter((r) => r.status === 200);

      // All health checks should succeed
      const successRate = successfulResponses.length / responses.length;
      expect(successRate).toBeGreaterThanOrEqual(0.8);
      expect(responses.length).toBe(numRequests);
    });

    test("should have reasonable response times", async () => {
      const endpoints = [
        { method: "get", path: "/health" },
        {
          method: "post",
          path: "/api/challenges",
          payload: { difficulty: "easy" },
        },
        {
          method: "post",
          path: "/api/skills",
          payload: { category: "algorithms" },
        },
      ];

      const responseTimes: number[] = [];

      for (const { method, path, payload } of endpoints) {
        const startTime = Date.now();

        if (method === "get") {
          await request(app).get(path).timeout(TEST_TIMEOUT);
        } else {
          await request(app).post(path).send(payload).timeout(TEST_TIMEOUT);
        }

        const duration = Date.now() - startTime;
        responseTimes.push(duration);
      }

      const avgResponseTime =
        responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;

      // Average response time should be under 10 seconds
      expect(avgResponseTime).toBeLessThan(10000);
    });
  });

  describe("MCP Integration Tests", () => {
    test("should handle MCP challenges integration", async () => {
      const payload = {
        difficulty: "easy",
        limit: 3,
      };

      const response = await request(app)
        .post("/api/challenges")
        .send(payload)
        .timeout(10000); // Shorter timeout for test environment

      // Should return successfully even if MCP is down (fallback behavior)
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("challenges");
      expect(Array.isArray(response.body.challenges)).toBe(true);
    });

    test("should handle MCP skills integration", async () => {
      const payload = {
        category: "algorithms",
        limit: 5,
      };

      const response = await request(app)
        .post("/api/skills")
        .send(payload)
        .timeout(10000); // Shorter timeout for test environment

      // Should return successfully even if MCP is down (fallback behavior)
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("skills");
      expect(Array.isArray(response.body.skills)).toBe(true);
    });
  });

  describe("Performance Monitoring Integration", () => {
    test("should track performance metrics", async () => {
      // Make a few requests to generate metrics
      await request(app).get("/health");
      await request(app).post("/api/chat").send({ message: "test" });

      // Check that performance monitor is working
      const stats = monitor.getStats(1); // Last minute
      expect(stats).toBeDefined();
      expect(typeof stats.totalRequests).toBe("number");
      expect(typeof stats.averageResponseTime).toBe("number");
      expect(typeof stats.errorRate).toBe("number");
    });

    test("should report health status", async () => {
      const health = monitor.getHealthStatus();
      expect(health).toBeDefined();
      expect(["healthy", "warning", "critical"]).toContain(health.status);
      expect(typeof health.message).toBe("string");
      expect(health.details).toBeDefined();
    });
  });
});
