/* eslint-env node */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src", "<rootDir>/tests"],
  testMatch: ["**/__tests__/**/*.ts", "**/?(*.)+(spec|test).ts"],
  transform: {
    "^.+\\.ts$": "ts-jest",
  },
  collectCoverageFrom: [
    "src/**/*.ts",
    "!src/**/*.d.ts",
    "!src/index.ts", // Exclude console interface
  ],
  coverageDirectory: "coverage",
  coverageReporters: ["text", "lcov", "html"],
  testTimeout: 30000, // 30 second timeout for E2E tests
  setupFilesAfterEnv: ["<rootDir>/tests/setup.ts"],
  verbose: true,
  forceExit: true, // Force exit after tests complete
  detectOpenHandles: false, // Disable open handles detection by default
  maxWorkers: 1, // Run tests sequentially to avoid port conflicts
};
