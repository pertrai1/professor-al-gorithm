/**
 * Type definitions for MCP responses
 */

export interface MCPToolParams {
  [key: string]: string | number | boolean;
}

export interface MCPResponse {
  result?: MCPResult;
  error?: MCPError;
  jsonrpc: string;
  id: number;
}

export interface MCPResult {
  content?: MCPContent[];
  structuredContent?: StructuredContent;
}

export interface MCPContent {
  type: string;
  text: string;
}

export interface MCPError {
  code: number;
  message: string;
}

export interface StructuredContent {
  page: number;
  pageSize: number;
  total: number;
  data: Challenge[] | Skill[];
}

export interface Challenge {
  id: string;
  name: string;
  track?: string;
  status?: string;
  description?: string;
  typeId?: string;
  trackId?: string;
  skills?: ChallengeSkill[];
}

export interface Skill {
  id: string;
  name: string;
  description?: string;
  category?: SkillCategory;
}

export interface SkillCategory {
  id: string;
  name: string;
  description?: string;
}

export interface ChallengeSkill {
  name: string;
  id: string;
  category: SkillCategory;
}
