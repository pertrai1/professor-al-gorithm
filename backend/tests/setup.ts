/**
 * Jest test setup configuration
 * Module 7: Testing & Debugging Implementation
 */

// Extend Jest timeout for E2E tests
jest.setTimeout(30000);

// Mock console methods to reduce noise during testing
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;
const originalConsoleLog = console.log;

beforeAll(() => {
  // Only show console output in verbose mode
  if (!process.env.JEST_VERBOSE) {
    console.error = jest.fn();
    console.warn = jest.fn();
    console.log = jest.fn();
  }
});

afterAll(async () => {
  // Restore original console methods
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
  console.log = originalConsoleLog;

  // Clean up any remaining timers and handles
  await new Promise((resolve) => setTimeout(resolve, 100));
});

// Global cleanup for better test isolation
global.afterAll(async () => {
  // Force cleanup of any remaining handles
  if (global.gc) {
    global.gc();
  }

  // Additional cleanup time
  await new Promise((resolve) => setTimeout(resolve, 200));
});

// Global test configuration
process.env.NODE_ENV = "test";
process.env.MCP_TIMEOUT = "2000"; // Much shorter timeout for tests (2 seconds)
process.env.API_TIMEOUT = "3000";
process.env.REQUEST_TIMEOUT = "5000";
