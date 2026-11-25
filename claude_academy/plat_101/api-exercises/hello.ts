import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const msg = await client.messages.create({
  model: "claude-haiku-5-5",
  max_tokens: 2048,
  messages: [{
    role: "user",
    content: "Hello, Claude",
  }],
});

for (const block of msg.content) {
  if (block.type === "text") {
    console.log(block.text);
  }
}