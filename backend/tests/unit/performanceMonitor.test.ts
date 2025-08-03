/**
 * Unit Tests for Performance Monitor
 * Module 7: Testing & Debugging Implementation
 */

import { monitor } from "../../src/performanceMonitor";

describe("Performance Monitor", () => {
  beforeEach(() => {
    // Clear metrics before each test
    (monitor as any).metrics = [];
  });

  describe("recordMetric", () => {
    test("should record a metric correctly", () => {
      const metric = {
        endpoint: "/api/test",
        method: "POST",
        responseTime: 1000,
        statusCode: 200,
        timestamp: new Date(),
      };

      monitor.recordMetric(metric);
      const stats = monitor.getStats(1);

      expect(stats.totalRequests).toBe(1);
      expect(stats.averageResponseTime).toBe(1000);
      expect(stats.errorRate).toBe(0);
    });

    test("should record error metrics", () => {
      const errorMetric = {
        endpoint: "/api/test",
        method: "POST",
        responseTime: 500,
        statusCode: 400,
        timestamp: new Date(),
        error: "400 Bad Request",
      };

      monitor.recordMetric(errorMetric);
      const stats = monitor.getStats(1);

      expect(stats.totalRequests).toBe(1);
      expect(stats.errorRate).toBe(100);
    });

    test("should identify slow requests", () => {
      const slowMetric = {
        endpoint: "/api/slow",
        method: "GET",
        responseTime: 6000, // 6 seconds
        statusCode: 200,
        timestamp: new Date(),
      };

      monitor.recordMetric(slowMetric);
      const stats = monitor.getStats(1);

      expect(stats.slowRequestRate).toBe(100);
    });

    test("should limit stored metrics", () => {
      // Add more than maxMetrics (1000)
      for (let i = 0; i < 1005; i++) {
        monitor.recordMetric({
          endpoint: `/api/test${i}`,
          method: "GET",
          responseTime: 100,
          statusCode: 200,
          timestamp: new Date(),
        });
      }

      const metricsCount = (monitor as any).metrics.length;
      expect(metricsCount).toBeLessThanOrEqual(1000);
    });
  });

  describe("getStats", () => {
    test("should return empty stats when no metrics", () => {
      const stats = monitor.getStats(5);

      expect(stats.totalRequests).toBe(0);
      expect(stats.averageResponseTime).toBe(0);
      expect(stats.errorRate).toBe(0);
      expect(stats.slowRequestRate).toBe(0);
      expect(Object.keys(stats.endpointStats)).toHaveLength(0);
    });

    test("should calculate correct statistics", () => {
      const baseTime = new Date();

      // Add metrics: 2 success, 1 error, 1 slow
      const metrics = [
        {
          endpoint: "/api/test1",
          method: "GET",
          responseTime: 1000,
          statusCode: 200,
          timestamp: baseTime,
        },
        {
          endpoint: "/api/test2",
          method: "POST",
          responseTime: 2000,
          statusCode: 200,
          timestamp: baseTime,
        },
        {
          endpoint: "/api/test3",
          method: "GET",
          responseTime: 3000,
          statusCode: 400,
          timestamp: baseTime,
        },
        {
          endpoint: "/api/test4",
          method: "GET",
          responseTime: 6000, // Slow request
          statusCode: 200,
          timestamp: baseTime,
        },
      ];

      metrics.forEach((metric) => monitor.recordMetric(metric));
      const stats = monitor.getStats(1);

      expect(stats.totalRequests).toBe(4);
      expect(stats.averageResponseTime).toBe(3000); // (1000+2000+3000+6000)/4
      expect(stats.errorRate).toBe(25); // 1 error out of 4 requests
      expect(stats.slowRequestRate).toBe(25); // 1 slow request out of 4
    });

    test("should group endpoint statistics correctly", () => {
      const baseTime = new Date();

      const metrics = [
        {
          endpoint: "/api/test",
          method: "GET",
          responseTime: 1000,
          statusCode: 200,
          timestamp: baseTime,
        },
        {
          endpoint: "/api/test",
          method: "GET",
          responseTime: 2000,
          statusCode: 200,
          timestamp: baseTime,
        },
        {
          endpoint: "/api/test",
          method: "POST",
          responseTime: 1500,
          statusCode: 400,
          timestamp: baseTime,
        },
      ];

      metrics.forEach((metric) => monitor.recordMetric(metric));
      const stats = monitor.getStats(1);

      expect(stats.endpointStats["GET /api/test"]).toEqual({
        count: 2,
        avgResponseTime: 1500, // (1000+2000)/2
        errorCount: 0,
      });

      expect(stats.endpointStats["POST /api/test"]).toEqual({
        count: 1,
        avgResponseTime: 1500,
        errorCount: 1,
      });
    });

    test("should filter by time window", () => {
      const oldTime = new Date(Date.now() - 10 * 60 * 1000); // 10 minutes ago
      const recentTime = new Date();

      // Add old metric
      monitor.recordMetric({
        endpoint: "/api/old",
        method: "GET",
        responseTime: 1000,
        statusCode: 200,
        timestamp: oldTime,
      });

      // Add recent metric
      monitor.recordMetric({
        endpoint: "/api/recent",
        method: "GET",
        responseTime: 2000,
        statusCode: 200,
        timestamp: recentTime,
      });

      const stats = monitor.getStats(5); // Last 5 minutes

      expect(stats.totalRequests).toBe(1); // Only recent metric
      expect(stats.averageResponseTime).toBe(2000);
    });
  });

  describe("getHealthStatus", () => {
    test("should return healthy status with no requests", () => {
      const health = monitor.getHealthStatus();

      expect(health.status).toBe("healthy");
      expect(health.message).toBe("No recent activity");
    });

    test("should return healthy status with good metrics", () => {
      monitor.recordMetric({
        endpoint: "/api/test",
        method: "GET",
        responseTime: 1000,
        statusCode: 200,
        timestamp: new Date(),
      });

      const health = monitor.getHealthStatus();

      expect(health.status).toBe("healthy");
      expect(health.message).toBe("System operating normally");
    });

    test("should return warning status with elevated error rate", () => {
      // Add metrics with 15% error rate (warning threshold is 10%)
      for (let i = 0; i < 85; i++) {
        monitor.recordMetric({
          endpoint: "/api/test",
          method: "GET",
          responseTime: 1000,
          statusCode: 200,
          timestamp: new Date(),
        });
      }

      for (let i = 0; i < 15; i++) {
        monitor.recordMetric({
          endpoint: "/api/test",
          method: "GET",
          responseTime: 1000,
          statusCode: 400,
          timestamp: new Date(),
        });
      }

      const health = monitor.getHealthStatus();

      expect(health.status).toBe("warning");
      expect(health.message).toContain("Elevated error rate: 15%");
    });

    test("should return critical status with high error rate", () => {
      // Add metrics with 25% error rate (critical threshold is 20%)
      for (let i = 0; i < 75; i++) {
        monitor.recordMetric({
          endpoint: "/api/test",
          method: "GET",
          responseTime: 1000,
          statusCode: 200,
          timestamp: new Date(),
        });
      }

      for (let i = 0; i < 25; i++) {
        monitor.recordMetric({
          endpoint: "/api/test",
          method: "GET",
          responseTime: 1000,
          statusCode: 500,
          timestamp: new Date(),
        });
      }

      const health = monitor.getHealthStatus();

      expect(health.status).toBe("critical");
      expect(health.message).toContain("High error rate: 25%");
    });

    test("should return warning status with slow response times", () => {
      monitor.recordMetric({
        endpoint: "/api/slow",
        method: "GET",
        responseTime: 7000, // 7 seconds (warning threshold is 5 seconds)
        statusCode: 200,
        timestamp: new Date(),
      });

      const health = monitor.getHealthStatus();

      expect(health.status).toBe("warning");
      expect(health.message).toContain("Slow response times: 7000ms average");
    });

    test("should return critical status with very slow response times", () => {
      monitor.recordMetric({
        endpoint: "/api/veryslow",
        method: "GET",
        responseTime: 12000, // 12 seconds (critical threshold is 10 seconds)
        statusCode: 200,
        timestamp: new Date(),
      });

      const health = monitor.getHealthStatus();

      expect(health.status).toBe("critical");
      expect(health.message).toContain(
        "Very slow response times: 12000ms average"
      );
    });
  });

  describe("middleware", () => {
    test("should create middleware function", () => {
      const middleware = monitor.middleware();
      expect(typeof middleware).toBe("function");
      expect(middleware.length).toBe(3); // req, res, next
    });

    test("should record metrics when response finishes", (done) => {
      const middleware = monitor.middleware();

      const mockReq = {
        path: "/api/test",
        method: "GET",
      };

      const mockRes = {
        statusCode: 200,
        statusMessage: "OK",
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === "finish") {
            setTimeout(callback, 10); // Simulate response time
          }
        }),
      };

      const mockNext = jest.fn();

      middleware(mockReq as any, mockRes as any, mockNext);

      setTimeout(() => {
        expect(mockNext).toHaveBeenCalled();
        expect(mockRes.on).toHaveBeenCalledWith("finish", expect.any(Function));

        const stats = monitor.getStats(1);
        expect(stats.totalRequests).toBe(1);
        done();
      }, 50);
    });
  });
});
