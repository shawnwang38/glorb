# Glorbus MVP — App-Based Task Classifier

Given a task description and macOS open apps, returns which apps are valid for that task.

## Setup

### 1. Install Node dependencies
```bash
npm install
```

### 2. Install and start Ollama
```bash
# Install from https://ollama.com — or via brew:
brew install ollama
ollama serve
```

### 3. Pull the model
```bash
ollama pull qwen3:1.7b
```

### 4. Start the server
```bash
npm start
# or with live reload:
npm run dev
```

### 5. Test it
```bash
bash test.sh
```

Or manually:
```bash
curl "http://localhost:3000/predict?task=writing+code"
curl "http://localhost:3000/distracted?task=writing+code&app=Visual+Studio+Code"
```

## Configuration

Edit `config/overrides.json` to adjust:

- **alwaysAllowedApps** — always included regardless of LLM output
- **manualAllowedApps** — force-include specific apps for all tasks
- **manualBlockedApps** — always exclude specific apps

## Final app logic

```
finalAllowed = (llmSuggested ∪ alwaysAllowed ∪ manualAllowed) - manualBlocked
```

## API

### `GET /predict?task=<description>`

Returns which open apps are allowed for the given task (LLM + overrides applied).

**Response:**
```json
{ "apps": ["Finder", "Google Chrome", "Visual Studio Code"] }
```

---

### `GET /distracted?task=<description>&app=<activeApp>`

Given the user's current task and their active app, returns whether they are distracted.

**Response:**
```json
{
  "activeApp": "Spotify",
  "allowedApps": ["Visual Studio Code", "Terminal", "Finder", "Google Chrome", "Safari"],
  "distracted": true
}
```

---

**Error response (both endpoints):**
```json
{ "error": "Ollama is not running — start it with: ollama serve" }
```

## Adding app aliases

Edit `src/normalize.js` → `ALIASES` map to handle new process name variants.
