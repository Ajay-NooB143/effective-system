const OpenAI = require("openai");

const SYSTEM_PROMPT =
  "You are a professional trading coach helping users understand trading concepts. " +
  "Keep answers concise and educational.";

async function chat(req, res) {
  const { message, context } = req.body;

  if (!message) {
    return res.status(400).json({ error: "message is required" });
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: "OPENAI_API_KEY is not configured" });
  }

  try {
    const openai = new OpenAI({ apiKey });

    const userContent = context
      ? `[Context: ${context}]\n\n${message}`
      : message;

    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userContent },
      ],
    });

    const reply = completion.choices[0].message.content;
    return res.json({ reply });
  } catch (err) {
    console.error("OpenAI error:", err.message);
    return res.status(500).json({ error: "Failed to get response from AI" });
  }
}

module.exports = { chat };
