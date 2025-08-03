/**
 * Performance monitoring utility for Professor Al Gorithm
 * Tracks response times, error rates, and system health metrics
 */

import express from "express";

interface PerformanceMetric {
  endpoint: string;
  method: string;
  responseTime: number;
  statusCode: number;
  timestamp: Date;
  error?: string;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private readonly maxMetrics = 1000; // Keep last 1000 metrics

  /**
   * Record a performance metric
   */
  recordMetric(metric: PerformanceMetric): void {
    this.metrics.push(metric);

    // Keep only the most recent metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }

    // Log slow requests
    if (metric.responseTime > 10000) {
      // 10 seconds
      console.warn(
        `Slow request detected: ${metric.method} ${metric.endpoint} took ${metric.responseTime}ms`
      );
    }

    // Log errors
    if (metric.statusCode >= 400) {
      console.error(
        `Error request: ${metric.method} ${metric.endpoint} returned ${metric.statusCode}${metric.error ? ": " + metric.error : ""}`
      );
    }
  }

  /**
   * Get performance statistics for the last N minutes
   */
  getStats(minutesBack: number = 5): {
    totalRequests: number;
    averageResponseTime: number;
    errorRate: number;
    slowRequestRate: number;
    endpointStats: Record<
      string,
      {
        count: number;
        avgResponseTime: number;
        errorCount: number;
      }
    >;
  } {
    const cutoffTime = new Date(Date.now() - minutesBack * 60 * 1000);
    const recentMetrics = this.metrics.filter((m) => m.timestamp >= cutoffTime);

    if (recentMetrics.length === 0) {
      return {
        totalRequests: 0,
        averageResponseTime: 0,
        errorRate: 0,
        slowRequestRate: 0,
        endpointStats: {},
      };
    }

    const errorCount = recentMetrics.filter((m) => m.statusCode >= 400).length;
    const slowRequestCount = recentMetrics.filter(
      (m) => m.responseTime > 5000
    ).length;
    const totalResponseTime = recentMetrics.reduce(
      (sum, m) => sum + m.responseTime,
      0
    );

    // Group by endpoint
    const endpointStats: Record<
      string,
      {
        count: number;
        avgResponseTime: number;
        errorCount: number;
      }
    > = {};

    recentMetrics.forEach((metric) => {
      const key = `${metric.method} ${metric.endpoint}`;
      if (!endpointStats[key]) {
        endpointStats[key] = { count: 0, avgResponseTime: 0, errorCount: 0 };
      }
      endpointStats[key].count++;
      endpointStats[key].avgResponseTime += metric.responseTime;
      if (metric.statusCode >= 400) {
        endpointStats[key].errorCount++;
      }
    });

    // Calculate averages
    Object.keys(endpointStats).forEach((key) => {
      endpointStats[key].avgResponseTime = Math.round(
        endpointStats[key].avgResponseTime / endpointStats[key].count
      );
    });

    return {
      totalRequests: recentMetrics.length,
      averageResponseTime: Math.round(totalResponseTime / recentMetrics.length),
      errorRate:
        Math.round((errorCount / recentMetrics.length) * 100 * 100) / 100, // Round to 2 decimal places
      slowRequestRate:
        Math.round((slowRequestCount / recentMetrics.length) * 100 * 100) / 100,
      endpointStats,
    };
  }

  /**
   * Get health status based on recent performance
   */
  getHealthStatus(): {
    status: "healthy" | "warning" | "critical";
    message: string;
    details: ReturnType<typeof this.getStats>;
  } {
    const stats = this.getStats(5); // Last 5 minutes

    if (stats.totalRequests === 0) {
      return {
        status: "healthy",
        message: "No recent activity",
        details: stats,
      };
    }

    let status: "healthy" | "warning" | "critical" = "healthy";
    let message = "System operating normally";

    if (stats.errorRate > 20) {
      status = "critical";
      message = `High error rate: ${stats.errorRate}%`;
    } else if (stats.errorRate > 10) {
      status = "warning";
      message = `Elevated error rate: ${stats.errorRate}%`;
    } else if (stats.averageResponseTime > 10000) {
      status = "critical";
      message = `Very slow response times: ${stats.averageResponseTime}ms average`;
    } else if (stats.averageResponseTime > 5000) {
      status = "warning";
      message = `Slow response times: ${stats.averageResponseTime}ms average`;
    } else if (stats.slowRequestRate > 30) {
      status = "warning";
      message = `High rate of slow requests: ${stats.slowRequestRate}%`;
    }

    return {
      status,
      message,
      details: stats,
    };
  }

  /**
   * Create Express middleware for automatic performance monitoring
   */
  middleware() {
    return (
      req: express.Request,
      res: express.Response,
      next: express.NextFunction
    ) => {
      const startTime = Date.now();

      // Capture the original end function
      const originalEnd = res.end;

      // Override the end function to capture metrics
      res.end = function (...args: Parameters<typeof originalEnd>) {
        const responseTime = Date.now() - startTime;

        monitor.recordMetric({
          endpoint: req.path || req.url,
          method: req.method,
          responseTime,
          statusCode: res.statusCode,
          timestamp: new Date(),
          error:
            res.statusCode >= 400
              ? `${res.statusCode} ${res.statusMessage}`
              : undefined,
        });

        // Call the original end function
        originalEnd.apply(this, args);
      };

      next();
    };
  }
}

// Singleton instance
export const monitor = new PerformanceMonitor();

export default PerformanceMonitor;
