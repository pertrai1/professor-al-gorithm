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

afterAll(() => {
  // Restore original console methods
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
  console.log = originalConsoleLog;
});

// Global test configuration
process.env.NODE_ENV = "test";
process.env.MCP_TIMEOUT = "10000"; // Shorter timeout for tests
process.env.API_TIMEOUT = "15000";
process.env.REQUEST_TIMEOUT = "20000";
