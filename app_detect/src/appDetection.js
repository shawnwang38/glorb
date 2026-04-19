const { execSync } = require("child_process");

// Returns raw list of visible application names on macOS.
function getOpenApps() {
  const script = `tell application "System Events" to get name of every process where background only is false`;

  let raw;
  try {
    raw = execSync(`osascript -e '${script}'`, { encoding: "utf8", timeout: 5000 });
  } catch (err) {
    if (err.message.includes("osascript")) {
      throw new Error("osascript unavailable — this feature requires macOS");
    }
    throw new Error(`App detection failed: ${err.message}`);
  }

  // osascript returns comma-separated names: "Finder, Terminal, Code"
  const apps = raw
    .trim()
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (apps.length === 0) {
    throw new Error("No open applications detected");
  }

  return apps;
}

function getActiveApp() {
  const script = `tell application "System Events" to get name of first application process whose frontmost is true`;
  try {
    const raw = execSync(`osascript -e '${script}'`, { encoding: "utf8", timeout: 3000 });
    return raw.trim();
  } catch (err) {
    throw new Error(`Active app detection failed: ${err.message}`);
  }
}

module.exports = { getOpenApps, getActiveApp };
