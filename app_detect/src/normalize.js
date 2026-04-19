// Maps known macOS process names to canonical display names.
// Add entries here as you encounter new aliases.
const ALIASES = {
  "Code": "Visual Studio Code",
  "VSCode": "Visual Studio Code",
  "Google Chrome": "Google Chrome",
  "Chrome": "Google Chrome",
  "Safari": "Safari",
  "Terminal": "Terminal",
  "iTerm2": "iTerm2",
  "iTerm": "iTerm2",
  "Finder": "Finder",
  "System Preferences": "System Settings",
  "System Settings": "System Settings",
  "Slack": "Slack",
  "Discord": "Discord",
  "Notion": "Notion",
  "Figma": "Figma",
  "Xcode": "Xcode",
  "Notes": "Notes",
  "Mail": "Mail",
  "Messages": "Messages",
  "Calendar": "Calendar",
  "Spotify": "Spotify",
  "zoom.us": "Zoom",
  "Zoom": "Zoom",
};

function normalizeAppName(name) {
  return ALIASES[name] ?? name;
}

function normalizeAppList(apps) {
  return [...new Set(apps.map(normalizeAppName))];
}

module.exports = { normalizeAppName, normalizeAppList };
