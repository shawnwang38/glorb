const fs = require("fs");
const path = require("path");

const OVERRIDES_PATH = path.join(__dirname, "../config/overrides.json");

function readOverrides() {
  return JSON.parse(fs.readFileSync(OVERRIDES_PATH, "utf8"));
}

function writeOverrides(data) {
  fs.writeFileSync(OVERRIDES_PATH, JSON.stringify(data, null, 2));
}

function addToList(listKey, app) {
  const data = readOverrides();
  if (!data[listKey].includes(app)) {
    data[listKey].push(app);
    writeOverrides(data);
  }
  return readOverrides();
}

function removeFromList(listKey, app) {
  const data = readOverrides();
  data[listKey] = data[listKey].filter((a) => a !== app);
  writeOverrides(data);
  return readOverrides();
}

module.exports = { readOverrides, addToList, removeFromList };
