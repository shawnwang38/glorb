const http = require("http");

const OLLAMA_HOST = "localhost";
const OLLAMA_PORT = 11434;
const MODEL = "qwen3:1.7b";

function buildPrompt(task, apps) {
  return `You are a strict focus assistant. Your job is to determine which open apps are directly required for the user's task.

Rules:
- Only include an app if it is CLEARLY and DIRECTLY needed for the exact task described.
- Do NOT include apps just because they are generally useful or productive.
- Do NOT include coding tools (Terminal, VS Code, Xcode) unless the task explicitly involves writing or running code.
- Do NOT include communication apps (Slack, Discord, Messages) unless the task explicitly involves communicating.
- If the task is vague, recreational, or non-work, return an empty array [].
- Prefer returning fewer apps over more apps. When in doubt, leave it out.
- Only use names that appear exactly in the provided list.
- Reply with ONLY a JSON array. No explanation, no markdown, no extra text.

User task: "${task}"

Open applications:
${JSON.stringify(apps)}

Examples of correct behavior:
- Task "coding my backend project" with [VS Code, Terminal, Chrome, Slack] → ["Visual Studio Code", "Terminal"]
- Task "writing an essay" with [VS Code, Notes, Chrome, Terminal] → ["Notes", "Google Chrome"]
- Task "organizing my calendar" with [VS Code, Terminal, Chrome, Calendar] → ["Calendar"]
- Task "doing nothing important" with [VS Code, Terminal, Chrome] → []

Your answer (JSON array only):`;
}

// Posts to Ollama and returns the raw response text.
function ollamaGenerate(prompt) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ model: MODEL, prompt, stream: false });

    const req = http.request(
      { hostname: OLLAMA_HOST, port: OLLAMA_PORT, path: "/api/generate", method: "POST",
        headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) } },
      (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          if (res.statusCode !== 200) {
            if (res.statusCode === 404) {
              reject(new Error(`Model "${MODEL}" not found — run: ollama pull ${MODEL}`));
            } else {
              reject(new Error(`Ollama returned HTTP ${res.statusCode}: ${data}`));
            }
            return;
          }
          try {
            const parsed = JSON.parse(data);
            resolve(parsed.response ?? "");
          } catch {
            reject(new Error(`Failed to parse Ollama response envelope: ${data}`));
          }
        });
      }
    );

    req.on("error", (err) => {
      if (err.code === "ECONNREFUSED") {
        reject(new Error("Ollama is not running — start it with: ollama serve"));
      } else {
        reject(new Error(`Ollama connection error: ${err.message}`));
      }
    });

    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error("Ollama request timed out after 30s"));
    });

    req.write(body);
    req.end();
  });
}

// Extracts a JSON array from the model's raw text output.
// Handles cases where the model wraps the array in markdown or adds extra text.
function parseAppArray(raw) {
  if (!raw || raw.trim() === "") {
    throw new Error("Model returned an empty response");
  }

  // Strip <think>...</think> blocks (qwen3 chain-of-thought output)
  const withoutThink = raw.replace(/<think>[\s\S]*?<\/think>/gi, "").trim();

  // Find the first [...] block
  const match = withoutThink.match(/\[[\s\S]*?\]/);
  if (!match) {
    throw new Error(`Model response contained no JSON array. Raw: ${raw}`);
  }

  let arr;
  try {
    arr = JSON.parse(match[0]);
  } catch {
    throw new Error(`Model JSON array was malformed: ${match[0]}`);
  }

  if (!Array.isArray(arr)) {
    throw new Error("Model response parsed but was not an array");
  }

  return arr.filter((x) => typeof x === "string");
}

async function classifyApps(task, apps) {
  const prompt = buildPrompt(task, apps);
  console.log("\n[ollama] Prompt sent:\n" + prompt);

  const raw = await ollamaGenerate(prompt);
  console.log("\n[ollama] Raw response:\n" + raw);

  const parsed = parseAppArray(raw);
  console.log("[ollama] Parsed app list:", parsed);

  return parsed;
}

module.exports = { classifyApps };
