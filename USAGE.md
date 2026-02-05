# MyceliumCortex Usage Guide

## Quick Start: Host Mode with Telegram

This guide walks you through setting up your PC as a host and controlling it via Telegram.

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi`, `uvicorn` — HTTP server
- `anthropic` or `openai` — LLM providers
- `httpx` — for Telegram API calls
- `pydantic` — data validation

### Step 2: Set Environment Variables (Windows PowerShell)

```powershell
# Your Telegram bot token (get from BotFather on Telegram)
$env:TELEGRAM_BOT_TOKEN = "123456:ABC-DEF-GHI..."

# Your LLM provider API key (pick one)
$env:ANTHROPIC_API_KEY = "sk-ant-..."
# OR
$env:OPENAI_API_KEY = "sk-..."

# Optional: API key to protect management endpoints
$env:ADMIN_API_KEY = "your-secret-key"
```

Or in Windows `cmd`:
```batch
set TELEGRAM_BOT_TOKEN=123456:ABC-DEF-GHI...
set ANTHROPIC_API_KEY=sk-ant-...
set ADMIN_API_KEY=your-secret-key
```

### Step 3: Start the Server

```bash
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```

This starts the FastAPI server on your PC at `http://localhost:8000`. The server will:
- Initialize ControlCenter (coordinates all agents)
- Initialize HostManager (manages agent registry)
- Spawn tactical supervisors (Conversation, Tool, Channel)
- Start MessageRouterAgent to process incoming messages

### Step 4: Expose Your PC to Telegram (ngrok)

Telegram needs to reach your server via webhooks. Use `ngrok` to create a public tunnel:

```bash
# Download and run ngrok (https://ngrok.com/download)
ngrok http 8000
```

You'll see output like:
```
Forwarding                    https://abc123def456.ngrok.io -> http://localhost:8000
```

### Step 5: Configure Telegram Webhook

Set up Telegram to send messages to your server:

```bash
# Replace YOUR_TOKEN and NGROK_URL
curl "https://api.telegram.org/botYOUR_TOKEN/setWebhook?url=https://abc123def456.ngrok.io/v1/webhook/telegram"
```

### Step 6: Send a Message to Your Bot

Open Telegram and message your bot. Here's what happens:

1. **Telegram sends webhook** → Your ngrok tunnel → `POST /v1/webhook/telegram` on your PC
2. **FastAPI endpoint** extracts `chat_id` and message text
3. **Message stored** in SQLite database (`./data/myceliumcortex.db`)
4. **Message published** to internal message bus
5. **MessageRouterAgent** subscribes to bus, routes message to ControlCenter
6. **ControlCenter** delegates to ConversationSupervisor
7. **ConversationSupervisor** calls LLMAgent with the message
8. **LLMAgent** calls Anthropic/OpenAI API, gets response
9. **Response stored** in memory via MemoryAgent
10. **ChannelSupervisor** sends response back via Telegram Bot API
11. **User receives reply** on their phone

### Step 7: Execute Host Commands (Direct Shell Access)

Send special commands to execute on your PC:

```
/run ls -la
/run echo "Hello from host"
/shell ipconfig
/exec python --version
```

The bot will execute the command and return the output.

**Example flow:**
- You send: `/run dir C:\Users\adoria\Desktop`
- ToolAgent executes the shell command on your PC
- Returns the directory listing to your Telegram

## Architecture Flow Diagram

```
┌─────────────────┐
│ Your Telegram   │
│  Mobile Phone   │
└────────┬────────┘
         │ (message)
         │
    ┌────▼─────────────────────────────┐
    │  Telegram Bot API                │
    │  (receives webhook)              │
    └────┬──────────────────────────────┘
         │
         │ (ngrok tunnel)
         │
    ┌────▼──────────────────────────────┐
    │  FastAPI Server (Your PC)         │
    │  /v1/webhook/telegram endpoint    │
    └────┬───────────────────────────────┘
         │
         │ (stored in SQLite)
         │
    ┌────▼───────────────────────────────┐
    │  PersistentMemory                 │
    │  ./data/myceliumcortex.db         │
    └────┬────────────────────────────────┘
         │
         │ (published to bus)
         │
    ┌────▼─────────────────────────────────┐
    │  Message Bus (in-memory pub/sub)    │
    └────┬──────────────────────────────────┘
         │
         │ (subscribed by)
         │
    ┌────▼──────────────────────────────────┐
    │  MessageRouterAgent                   │
    └────┬───────────────────────────────────┘
         │
    ┌────▼────────────────────────────────────┐
    │  ControlCenter (Strategic)              │
    │  - Coordinates all supervisors          │
    │  - Routes to ConversationSupervisor     │
    └────┬─────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────┐
    │  ConversationSupervisor (Tactical)       │
    │  - Retrieves history from MemoryAgent    │
    │  - Calls LLMAgent                        │
    │  - Routes response via ChannelSupervisor │
    └────┬───────────────────────────────────────┘
         │
    ┌────▼───────────────────────────────────────┐
    │  LLMAgent (Execution)                     │
    │  - Calls Anthropic/OpenAI API             │
    │  - Returns generated response             │
    └────┬────────────────────────────────────────┘
         │ (response stored)
         │
    ┌────▼───────────────────────────────────────┐
    │  MemoryAgent (Execution)                  │
    │  - Stores conversation history            │
    └────┬────────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────┐
    │  ChannelSupervisor (Tactical)            │
    │  - Routes to TelegramAgent               │
    └────┬─────────────────────────────────────┘
         │
    ┌────▼───────────────────────────────────────┐
    │  TelegramAgent (Execution)                │
    │  - Calls Telegram Bot API sendMessage     │
    │  - Sends reply to user's chat             │
    └────┬────────────────────────────────────────┘
         │
         │ (Telegram API)
         │
    ┌────▼─────────────────┐
    │ User's Phone          │
    │ (receives reply)      │
    └───────────────────────┘
```

## Examples

### Example 1: Chat with LLM

**You send:**
```
What is the capital of France?
```

**Bot responds:**
```
The capital of France is Paris. It's located in north-central France 
and is the country's largest city. Paris is known for its art, 
architecture, and culture.
```

### Example 2: Execute Shell Command

**You send:**
```
/run ipconfig
```

**Bot responds:**
```
Windows IP Configuration

Ethernet adapter Ethernet:
   Connection-specific DNS Suffix  . :
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
   ...
```

### Example 3: File Operations

**You send:**
```
/run python -c "import os; print(os.getcwd())"
```

**Bot responds:**
```
C:\Users\adoria\Desktop\miniclaw
```

## API Endpoints

### Incoming Messages

**POST /v1/message**
```bash
curl -X POST http://localhost:8000/v1/message \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user123",
    "channel": "telegram",
    "sender": "user123",
    "message": "Hello bot!"
  }'
```

### Status

**GET /v1/status**
```bash
curl http://localhost:8000/v1/status
```

Returns:
```json
{"status": "ok", "service": "MyceliumCortex API"}
```

### Host Management (with API key)

**List registered agents**
```bash
curl -X GET http://localhost:8000/v1/host/agents \
  -H "X-API-KEY: your-secret-key"
```

**Register new agent**
```bash
curl -X POST http://localhost:8000/v1/host/agents \
  -H "X-API-KEY: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent",
    "class_path": "src.agents.execution_agents.CustomAgent",
    "capabilities": ["execute"],
    "config": {}
  }'
```

**Enable agent**
```bash
curl -X POST http://localhost:8000/v1/host/agents/my-agent/enable \
  -H "X-API-KEY: your-secret-key"
```

**Disable agent**
```bash
curl -X POST http://localhost:8000/v1/host/agents/my-agent/disable \
  -H "X-API-KEY: your-secret-key"
```

## Logs and Debugging

### View Logs

The server logs to console and `./myceliumcortex.log`. Watch for:

```
[INFO] ControlCenter initialized
[INFO] MessageRouterAgent started
[INFO] TelegramAgent initialized (token present=True)
[INFO] Processing message from <chat_id>: What is...
[INFO] Telegram: Sending message to chat <chat_id>
```

### Database

Your conversation history is stored in SQLite:
```
./data/myceliumcortex.db
```

View with any SQLite viewer or:
```bash
sqlite3 ./data/myceliumcortex.db "SELECT * FROM messages;"
```

### Agent Registry

Registered host agents stored in:
```
~/.myceliumcortex/agents.json
```

## Troubleshooting

### Bot Not Responding

1. **Check token**: Verify `TELEGRAM_BOT_TOKEN` is set correctly
2. **Check webhook**: Confirm ngrok URL is correct and webhook is set
3. **Check logs**: Look for errors in server output
4. **Test endpoint**: `curl http://localhost:8000/v1/status`

### Command Not Executing

1. **Check format**: Use `/run command` (space after `/run`)
2. **Check permissions**: Some commands may need elevated privileges
3. **Check logs**: See what error ToolAgent reported

### LLM Not Responding

1. **Check API key**: Verify `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
2. **Check balance**: Ensure you have API credits
3. **Check network**: Verify internet connection

## Next Steps

- Add WhatsApp integration (similar to Telegram)
- Add Gmail agent to send/receive emails
- Add Slack/Discord integration
- Implement WebSocket for real-time push notifications
- Add command whitelist or rate limiting for security

See [CHANNELS.md](CHANNELS.md) for more channel integration details.
