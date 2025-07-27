# Module 3: MCP Server Exploration & Tool Analysis

## Learning Objectives

By the end of this module, we will:

- ✅ Configure and use the MCP Inspector with Topcoder MCP server
- ✅ Thoroughly explore available MCP tools and their capabilities
- ✅ Understand the data structures and schemas provided by the server
- ✅ Design how Professor Al Gorithm will integrate with MCP tools
- ✅ Document real examples of challenges and skills data

## MCP Inspector Configuration

### Setup Process

The official MCP Inspector is a powerful tool for exploring MCP servers interactively. Here's how we configured it for the Topcoder MCP server:

#### Inspector Architecture

- **MCP Inspector Client (MCPI)**: React web UI at `http://localhost:6274`
- **MCP Proxy (MCPP)**: Node.js server at `http://localhost:6277`
- **Authentication**: Bearer token or custom headers support

#### Connection Configuration

```
Transport: SSE (Server-Sent Events)
URL: https://api.topcoder-dev.com/v6/mcp/sse
Authentication Header: X-MCP-Session: <64-char-session-token>
```

#### Direct Access Links

```
# Pre-configured for SSE transport
http://localhost:6274/?transport=sse&serverUrl=https://api.topcoder-dev.com/v6/mcp/sse

# Alternative HTTP transport
http://localhost:6274/?transport=streamable-http&serverUrl=https://api.topcoder-dev.com/v6/mcp/mcp
```

## Tool Exploration Results

### Available MCP Tools

#### 1. query-tc-challenges

**Purpose**: Retrieve Topcoder challenges based on query parameters

**Key Parameters**:

- `status`: Filter by challenge status (Active, Completed, Draft, etc.)
- `track`: Filter by track (Development, Design, Data Science)
- `tags`: Filter by skill tags (arrays supported)
- `search`: Text search across name, description, and tags
- `totalPrizesFrom/To`: Filter by prize amounts
- `page/perPage`: Pagination controls (max 100 per page)

**Output Structure**:

```typescript
interface Challenge {
  id: string;
  name: string;
  track: string;
  status: string;
  description: string;
  skills: Array<{
    id: string;
    name: string;
    category: { id: string; name: string };
  }>;
  overview: { totalPrizes: number; types: string };
  phases: Array<{ name: string; isOpen: boolean; scheduledStartDate: string }>;
  tags: string[];
  startDate: string;
  endDate: string;
}
```

#### 2. query-tc-skills

**Purpose**: Retrieve standardized skills from Topcoder platform

**Key Parameters**:

- `name`: Filter by skill names (array)
- `skillId`: Filter by skill IDs (array)
- `sortBy`: Sort by name, description, created_at, updated_at
- `page/perPage`: Pagination controls

**Output Structure**:

```typescript
interface Skill {
  id: string;
  name: string;
  description: string;
  category: {
    id: string;
    name: string;
    description?: string;
  };
}
```

## Professor Al Gorithm Integration Design

### Use Case 1: Finding Appropriate Practice Problems

```
Student Input: "I want to practice dynamic programming"
Professor Al Gorithm Process:
1. Use query-tc-skills to find DP-related skills
2. Use query-tc-challenges with tags=["Dynamic Programming"]
3. Filter by difficulty/prize amount as proxy for complexity
4. Present 2-3 challenges and guide through Algorithm Design Canvas
```

### Use Case 2: Skill Development Pathway

```
Student Input: "What skills do I need for algorithms?"
Professor Al Gorithm Process:
1. Use query-tc-skills to get algorithm-related skills
2. Group by category (Data Structures, Algorithms, etc.)
3. Use query-tc-challenges to find practice problems for each skill
4. Create learning pathway with progressive difficulty
```

### Use Case 3: Algorithm Design Canvas Workflow

```
For any selected challenge:
1. Constraints: Extract from challenge description and constraints
2. Ideas: Guide student through algorithmic approaches
3. Test Cases: Use challenge examples, create edge cases
4. Code: Help structure solution without writing code
```

## Integration Architecture

### MCP Service Layer

```typescript
interface ProfessorMCPService {
  findChallengesBySkill(skill: string): Promise<Challenge[]>;
  findChallengesByDifficulty(
    level: "beginner" | "intermediate" | "advanced"
  ): Promise<Challenge[]>;
  getSkillCategories(): Promise<SkillCategory[]>;
  getSkillsByCategory(category: string): Promise<Skill[]>;
}
```

### Teaching Flow Integration

```typescript
interface AlgorithmCanvasSession {
  currentPhase: "constraints" | "ideas" | "test_cases" | "code";
  selectedChallenge: Challenge;
  skillsBeingPracticed: Skill[];
  studentProgress: CanvasProgress;
}
```

## Next Steps for Module 4

### Immediate Priorities

1. **Run comprehensive data exploration** using both MCP Inspector and custom tool
2. **Document real challenge and skill examples** for integration planning
3. **Design specific user interaction flows** for each Algorithm Design Canvas phase
4. **Create mockups or wireframes** for the Professor Al Gorithm interface
5. **Plan state management** for tracking student progress through problems

### Technical Implementation

1. **Enhance mcpService.ts** with specific methods for educational use cases
2. **Create type definitions** for Challenge and Skill interfaces
3. **Design caching strategy** for MCP data to improve performance
4. **Plan error handling** for MCP connection issues and fallback responses

## Learning Insights

### MCP Inspector Capabilities

- **Interactive exploration**: Visual interface for understanding tool schemas
- **Real-time testing**: Immediate feedback on parameter combinations
- **Export functionality**: Generate configuration files for other MCP clients
- **Authentication support**: Flexible header and token management

### Data Quality Assessment

[To be completed after exploration]

### Educational Value Mapping

[To be completed after analyzing real challenges and skills]

---

_Module 3 in progress - to be completed after MCP Inspector exploration and data analysis._
