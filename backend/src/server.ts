import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { queryMCP, getChallenges, getSkills, processUserQuery } from "./mcpService";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get("/", (req, res) => {
  res.json({
    message: "Professor Al Gorithm API is running!",
    version: "1.0.0",
    status: "healthy"
  });
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "healthy", timestamp: new Date().toISOString() });
});

// Chat endpoint - main conversation interface
app.post("/api/chat", async (req, res) => {
  try {
    const { message, conversationId } = req.body;

    if (!message || typeof message !== "string") {
      return res.status(400).json({
        error: "Message is required and must be a string"
      });
    }

    const response = await processUserQuery(message, conversationId);
    
    res.json({
      response,
      conversationId: conversationId || Date.now().toString(),
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error("Error in chat endpoint:", error);
    res.status(500).json({
      error: "Internal server error",
      message: "Failed to process your request. Please try again."
    });
  }
});

// Get available challenges
app.get("/api/challenges", async (req, res) => {
  try {
    const { limit = 5, difficulty = "easy" } = req.query;
    
    const challenges = await getChallenges({
      limit: parseInt(limit as string),
      difficulty: difficulty as string
    });
    
    res.json({
      challenges,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error("Error fetching challenges:", error);
    res.status(500).json({
      error: "Failed to fetch challenges",
      challenges: []
    });
  }
});

// Get available skills
app.get("/api/skills", async (req, res) => {
  try {
    const { limit = 10, category = "algorithms" } = req.query;
    
    const skills = await getSkills({
      limit: parseInt(limit as string),
      category: category as string
    });
    
    res.json({
      skills,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error("Error fetching skills:", error);
    res.status(500).json({
      error: "Failed to fetch skills",
      skills: []
    });
  }
});

// Algorithm Design Canvas endpoint
app.post("/api/canvas", async (req, res) => {
  try {
    const { phase, content, challengeId } = req.body;
    
    if (!phase || !content) {
      return res.status(400).json({
        error: "Phase and content are required"
      });
    }

    const validPhases = ["constraints", "ideas", "test-cases", "code"];
    if (!validPhases.includes(phase)) {
      return res.status(400).json({
        error: "Invalid phase. Must be one of: constraints, ideas, test-cases, code"
      });
    }

    // Process the canvas submission
    const feedback = await processCanvasPhase(phase, content, challengeId);
    
    res.json({
      phase,
      feedback,
      nextPhase: getNextPhase(phase),
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error("Error processing canvas:", error);
    res.status(500).json({
      error: "Failed to process canvas submission"
    });
  }
});

// Helper function to process canvas phases
async function processCanvasPhase(phase: string, content: string, challengeId?: string): Promise<string> {
  const prompt = `As Professor Al Gorithm, provide feedback on this ${phase} phase submission: ${content}`;
  return await queryMCP(prompt);
}

// Helper function to get next phase
function getNextPhase(currentPhase: string): string | null {
  const phases = ["constraints", "ideas", "test-cases", "code"];
  const currentIndex = phases.indexOf(currentPhase);
  return currentIndex < phases.length - 1 ? phases[currentIndex + 1] : null;
}

// Error handling middleware
app.use((error: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error("Unhandled error:", error);
  res.status(500).json({
    error: "Internal server error",
    message: process.env.NODE_ENV === "development" ? error.message : "Something went wrong"
  });
});

// 404 handler
app.use("*", (req, res) => {
  res.status(404).json({
    error: "Endpoint not found",
    message: `Cannot ${req.method} ${req.originalUrl}`
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Professor Al Gorithm API server running on port ${PORT}`);
  console.log(`📚 Health check: http://localhost:${PORT}/health`);
  console.log(`💬 Chat API: http://localhost:${PORT}/api/chat`);
});

export default app;