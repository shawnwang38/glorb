const { getOpenApps } = require("./appDetection");
const { normalizeAppList } = require("./normalize");
const { classifyApps } = require("./ollama");
const overrides = require("../config/overrides.json");

const { alwaysAllowedApps, manualAllowedApps, manualBlockedApps } = overrides;

// Keywords that signal a vague, idle, or non-work task.
// If matched, skip the LLM and return [] so only always-allowed apps remain.
const LOW_INTENT_PATTERNS = [
  /\bnothing\b/i,
  /\bidle\b/i,
  /\bbreak\b/i,
  /\brelax\b/i,
  /\brest\b/i,
  /\bbrowsing\b.*\brandomly\b/i,
  /\bjust\b.*\bsitting\b/i,
  /\bkilling time\b/i,
  /\bnot (doing|working)\b/i,
];

function isLowIntentTask(task) {
  return LOW_INTENT_PATTERNS.some((re) => re.test(task));
}

async function predict(task) {
  if (!task || task.trim() === "") {
    throw new Error("Task description is required");
  }

  // Step 1: detect open apps
  const rawApps = getOpenApps();
  console.log("[detect] Raw open apps:", rawApps);

  // Step 2: normalize
  const normalizedApps = normalizeAppList(rawApps);
  console.log("[normalize] Normalized apps:", normalizedApps);

  // Step 3: skip LLM for clearly vague/idle tasks
  let llmApps;
  if (isLowIntentTask(task)) {
    console.log("[predict] Low-intent task detected — skipping LLM, returning []");
    llmApps = [];
  } else {
    try {
      llmApps = await classifyApps(task.trim(), normalizedApps);
    } catch (err) {
      console.error("[ollama] Error:", err.message);
      throw err;
    }
  }

  // Step 4: filter LLM output to only names that actually appeared in normalized list
  const normalizedSet = new Set(normalizedApps);
  const validLlmApps = llmApps.filter((app) => normalizedSet.has(app));

  // Step 5: apply override formula
  //   finalAllowed = (llmApps ∪ alwaysAllowed ∪ manualAllowed) - manualBlocked
  const allowed = new Set([...validLlmApps, ...alwaysAllowedApps, ...manualAllowedApps]);
  const blockedSet = new Set(manualBlockedApps);
  const finalApps = [...allowed].filter((app) => !blockedSet.has(app));

  console.log("[predict] Final allowed apps:", finalApps);

  return finalApps;
}

module.exports = { predict };
