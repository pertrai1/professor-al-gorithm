import { queryMCP } from "./mcpService";

async function main() {
  const userInput = "What is a good first step to solve the two sum problem?";
  const response = await queryMCP(userInput);

  console.log("MCP Response: ", response);
}

main();
