import cors from "cors";
import dotenv from "dotenv";
import express from "express";

import { processQuery, getChallenges, getSkills } from "./mcpService";
import { monitor } from "./performanceMonitor";
import {
  createTimeoutPromise,
  validateLimit,
  validateDifficulty,
  validatePhase,
  createErrorResponse,
  processCanvasPhase,
  getNextPhase,
} from "./serverHelpers";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Performance monitoring middleware
app.use(monitor.middleware());

// Health check endpoint
app.get("/", (req, res) => {
  res.json({
    message: "Professor Al Gorithm API is running!",
    version: "1.0.0",
    status: "healthy",
  });
});

// Health check endpoint with performance monitoring
app.get("/health", (req, res) => {
  const healthStatus = monitor.getHealthStatus();
  res.json({
    status: healthStatus.status,
    message: healthStatus.message,
    timestamp: new Date().toISOString(),
    performance: healthStatus.details,
  });
});

// Performance stats endpoint (for debugging/monitoring)
app.get("/api/stats", (req, res) => {
  const minutesBack = parseInt(req.query.minutes as string) || 5;
  const stats = monitor.getStats(minutesBack);
  res.json({
    stats,
    timeRange: `${minutesBack} minutes`,
    timestamp: new Date().toISOString(),
  });
});

// Chat endpoint - main conversation interface
app.post("/api/chat", async (req, res) => {
  const startTime = Date.now();

  try {
    const { message, conversationId } = req.body;

    // Enhanced input validation
    if (!message || typeof message !== "string") {
      return res.status(400).json({
        error: "Message is required and must be a string",
        code: "INVALID_MESSAGE",
      });
    }

    if (message.length > 2000) {
      return res.status(400).json({
        error: "Message too long. Please limit to 2000 characters.",
        code: "MESSAGE_TOO_LONG",
      });
    }

    if (conversationId && typeof conversationId !== "string") {
      return res.status(400).json({
        error: "Conversation ID must be a string",
        code: "INVALID_CONVERSATION_ID",
      });
    }

    const response = await Promise.race([
      processQuery(message.trim(), conversationId),
      createTimeoutPromise(45000),
    ]);

    const processingTime = Date.now() - startTime;
    console.log(`Chat request processed in ${processingTime}ms`);

    res.json({
      response,
      conversationId: conversationId || Date.now().toString(),
      timestamp: new Date().toISOString(),
      processingTime,
    });
  } catch (error) {
    const processingTime = Date.now() - startTime;
    console.error(`Error in chat endpoint (${processingTime}ms):`, error);

    const errorResponse = createErrorResponse(error as Error, processingTime);
    res
      .status(errorResponse.code === "TIMEOUT" ? 408 : 500)
      .json(errorResponse);
  }
});

// Get available challenges - GET endpoint
app.get("/api/challenges", async (req, res) => {
  const startTime = Date.now();

  try {
    const { limit = 5, difficulty = "easy" } = req.query;

    const parsedLimit = validateLimit(limit as string);
    const validDifficulty = validateDifficulty(difficulty as string);

    const challenges = await Promise.race([
      getChallenges({ limit: parsedLimit, difficulty: validDifficulty }),
      createTimeoutPromise(30000),
    ]);

    const processingTime = Date.now() - startTime;
    console.log(`Challenges request processed in ${processingTime}ms`);

    res.json({
      challenges,
      count: challenges.length,
      timestamp: new Date().toISOString(),
      processingTime,
    });
  } catch (error) {
    const processingTime = Date.now() - startTime;
    console.error(`Error fetching challenges (${processingTime}ms):`, error);

    if (error instanceof Error && error.message.includes("must be")) {
      return res.status(400).json({
        error: error.message,
        code: error.message.includes("Limit")
          ? "INVALID_LIMIT"
          : "INVALID_DIFFICULTY",
      });
    }

    const errorResponse = createErrorResponse(error as Error, processingTime);
    res.status(errorResponse.code === "TIMEOUT" ? 408 : 500).json({
      ...errorResponse,
      challenges: [],
    });
  }
});

// Get available challenges - POST endpoint for Gradio
app.post("/api/challenges", async (req, res) => {
  const startTime = Date.now();

  try {
    const { limit = 5, difficulty = "easy" } = req.body;

    const parsedLimit = validateLimit(limit as string);
    const validDifficulty = validateDifficulty(difficulty as string);

    const challenges = await Promise.race([
      getChallenges({ limit: parsedLimit, difficulty: validDifficulty }),
      createTimeoutPromise(30000),
    ]);

    const processingTime = Date.now() - startTime;
    console.log(`Challenges request processed in ${processingTime}ms`);

    res.json({
      challenges,
      count: challenges.length,
      timestamp: new Date().toISOString(),
      processingTime,
    });
  } catch (error) {
    const processingTime = Date.now() - startTime;
    console.error(`Error fetching challenges (${processingTime}ms):`, error);

    if (error instanceof Error && error.message.includes("must be")) {
      return res.status(400).json({
        error: error.message,
        code: error.message.includes("Limit")
          ? "INVALID_LIMIT"
          : "INVALID_DIFFICULTY",
      });
    }

    const errorResponse = createErrorResponse(error as Error, processingTime);
    res.status(errorResponse.code === "TIMEOUT" ? 408 : 500).json({
      ...errorResponse,
      challenges: [],
    });
  }
});

// Get available skills - GET endpoint
app.get("/api/skills", async (req, res) => {
  const startTime = Date.now();

  try {
    const { limit = 10, category = "algorithms" } = req.query;

    const parsedLimit = validateLimit(limit as string);

    const skills = await Promise.race([
      getSkills({ limit: parsedLimit, category: category as string }),
      createTimeoutPromise(30000),
    ]);

    const processingTime = Date.now() - startTime;
    console.log(`Skills request processed in ${processingTime}ms`);

    res.json({
      skills,
      count: skills.length,
      timestamp: new Date().toISOString(),
      processingTime,
    });
  } catch (error) {
    const processingTime = Date.now() - startTime;
    console.error(`Error fetching skills (${processingTime}ms):`, error);

    if (error instanceof Error && error.message.includes("must be")) {
      return res.status(400).json({
        error: error.message,
        code: "INVALID_LIMIT",
      });
    }

    const errorResponse = createErrorResponse(error as Error, processingTime);
    res.status(errorResponse.code === "TIMEOUT" ? 408 : 500).json({
      ...errorResponse,
      skills: [],
    });
  }
});

// Get available skills - POST endpoint for Gradio
app.post("/api/skills", async (req, res) => {
  const startTime = Date.now();

  try {
    const { limit = 10, category = "algorithms" } = req.body;

    const parsedLimit = validateLimit(limit as string);

    const skills = await Promise.race([
      getSkills({ limit: parsedLimit, category: category as string }),
      createTimeoutPromise(30000),
    ]);

    const processingTime = Date.now() - startTime;
    console.log(`Skills request processed in ${processingTime}ms`);

    res.json({
      skills,
      count: skills.length,
      timestamp: new Date().toISOString(),
      processingTime,
    });
  } catch (error) {
    const processingTime = Date.now() - startTime;
    console.error(`Error fetching skills (${processingTime}ms):`, error);

    if (error instanceof Error && error.message.includes("must be")) {
      return res.status(400).json({
        error: error.message,
        code: "INVALID_LIMIT",
      });
    }

    const errorResponse = createErrorResponse(error as Error, processingTime);
    res.status(errorResponse.code === "TIMEOUT" ? 408 : 500).json({
      ...errorResponse,
      skills: [],
    });
  }
});

// Algorithm Design Canvas endpoint
app.post("/api/canvas", async (req, res) => {
  const startTime = Date.now();

  try {
    const { phase, content, challengeId } = req.body;

    // Enhanced input validation
    if (!phase || typeof phase !== "string") {
      return res.status(400).json({
        error: "Phase is required and must be a string",
        code: "INVALID_PHASE",
      });
    }

    if (!content || typeof content !== "string") {
      return res.status(400).json({
        error: "Content is required and must be a string",
        code: "INVALID_CONTENT",
      });
    }

    if (content.length > 5000) {
      return res.status(400).json({
        error: "Content too long. Please limit to 5000 characters.",
        code: "CONTENT_TOO_LONG",
      });
    }

    const validPhase = validatePhase(phase);

    if (challengeId && typeof challengeId !== "string") {
      return res.status(400).json({
        error: "Challenge ID must be a string",
        code: "INVALID_CHALLENGE_ID",
      });
    }

    const feedback = await Promise.race([
      processCanvasPhase(validPhase, content.trim(), challengeId),
      createTimeoutPromise(30000),
    ]);

    const processingTime = Date.now() - startTime;
    console.log(`Canvas request processed in ${processingTime}ms`);

    res.json({
      phase: validPhase,
      feedback,
      nextPhase: getNextPhase(validPhase),
      timestamp: new Date().toISOString(),
      processingTime,
    });
  } catch (error) {
    const processingTime = Date.now() - startTime;
    console.error(`Error processing canvas (${processingTime}ms):`, error);

    if (error instanceof Error && error.message.includes("Invalid phase")) {
      return res.status(400).json({
        error: error.message,
        code: "INVALID_PHASE_VALUE",
      });
    }

    const errorResponse = createErrorResponse(error as Error, processingTime);
    res
      .status(errorResponse.code === "TIMEOUT" ? 408 : 500)
      .json(errorResponse);
  }
});

// Error handling middleware
function logError(error: Error, req: express.Request): void {
  console.error("Unhandled error:", {
    error: error.message,
    stack: error.stack,
    url: req.url,
    method: req.method,
    timestamp: new Date().toISOString(),
  });
}

function createErrorJson(error: Error): object {
  const isDevelopment = process.env.NODE_ENV === "development";

  return {
    error: "Internal server error",
    message: isDevelopment ? error.message : "Something went wrong",
    code: "UNHANDLED_ERROR",
    timestamp: new Date().toISOString(),
    ...(isDevelopment && { stack: error.stack }),
  };
}

app.use(
  (
    error: Error,
    req: express.Request,
    res: express.Response,
    _next: express.NextFunction
  ) => {
    logError(error, req);
    res.status(500).json(createErrorJson(error));
  }
);

// 404 handler
app.use("*", (req, res) => {
  res.status(404).json({
    error: "Endpoint not found",
    message: `Cannot ${req.method} ${req.originalUrl}`,
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Professor Al Gorithm API server running on port ${PORT}`);
  console.log(`📚 Health check: http://localhost:${PORT}/health`);
  console.log(`💬 Chat API: http://localhost:${PORT}/api/chat`);
});

export default app;
