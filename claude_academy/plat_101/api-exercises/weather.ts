import Anthropic from "@anthropic-ai/sdk";

 
const client = new Anthropic();

const tools: Anthropic.Tool[] = [
  {
    name: "get_weather",
    description: "Get the current weather for a city.",
    input_schema: {
      type: "object",
      properties: {
        city: {
          type: "string",
          description: "The city to get weather for",
        },
      },
      required: ["city"],
    },
  },
];

const systemPrompt = `You are a helpful travel and weather assistant.
For weather or clothing questions, use the get_weather tool.
If the user seems to want a pub or bar recommendation, suggest one notable
place in the city they mention and briefly explain what that city is famous for.
Do not claim to have checked current opening hours or availability.`;

function runTool(name: string, toolInput: unknown): string {
  if (name !== "get_weather") {
    throw new Error(`Unknown tool: ${name}`);
  }

  if (
    typeof toolInput !== "object" ||
    toolInput === null ||
    !("city" in toolInput) ||
    typeof toolInput.city !== "string"
  ) {
    throw new Error("get_weather requires a string city.");
  }

  return `Weather in ${toolInput.city}: 95F, sunny`;
}

const messages: Anthropic.MessageParam[] = [
  {
    role: "user",
    content: "What should I wear in Austin today? Also suggest a pub or bar there and tell me what Austin is famous for.",
  },
];

while (true) {
  const response = await client.messages.create({
    model: "claude-sonnet-5-5",
    max_tokens: 1024,
    system: systemPrompt,
    tools,
    messages,
  });

  console.log(`Stop reason: ${response.stop_reason}`);

  if (response.stop_reason === "end_turn") {
    for (const block of response.content) {
      if (block.type === "text") {
        console.log(block.text);
      }
    }
    break;
  }

  if (response.stop_reason === "tool_use") {
    const toolResults: Anthropic.ToolResultBlockParam[] = [];

    for (const block of response.content) {
      if (block.type === "tool_use") {
        const result = runTool(block.name, block.input);
        console.log(`Tool call: ${block.name} ${JSON.stringify(block.input)} -> ${result}`);
        toolResults.push({
          type: "tool_result",
          tool_use_id: block.id,
          content: result,
        });
      }
    }

    if (toolResults.length === 0) {
      throw new Error("Claude requested a tool but provided no tool calls.");
    }

    messages.push({ role: "assistant", content: response.content });
    messages.push({ role: "user", content: toolResults });
    continue;
  }

  console.log(`Stopped early: ${response.stop_reason}`);
  break;
}
