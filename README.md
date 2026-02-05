# MyceliumCortex: Host-Mode Hierarchical Multi-Agent AI Assistant

A hierarchical multi-agent AI system that runs on your PC, processes messages from Telegram, and executes commands or generates AI responses. Built from scratch following IDEA.md architecture principles.

> **Note on Inspiration**: MyceliumCortex is inspired by OpenClaw/Clawdbot-style autonomous workflows, but differs in that it uses explicit hierarchical orchestration among specialized agents, instead of relying primarily on a single primary agent's context to coordinate work. This results in specialized agent responsibilities, scoped memories, and clearer boundaries between decision-making layers.

**Key Features:**
- 🏠 **Host Mode**: Your PC runs the agent system; agents are configurable and persist
- 💬 **Multi-Channel**: Telegram (real Bot API integration), WhatsApp, Gmail, Slack, Discord
- 🧠 **LLM-Powered**: Calls Anthropic Claude or OpenAI GPT; conversation memory persists
- 🔧 **Shell Commands**: Send `/run command` from Telegram to execute on your host
- 📚 **Persistent Memory**: SQLite database stores all conversations
- 🚌 **Message Bus**: Async pub/sub routing between agents
- ⚡ **Async-First**: Python asyncio throughout for high concurrency
- 🖼️ **Vision Analysis**: Photo-based inventory scanning, recipe extraction, image analysis
- 📦 **Smart Tracking**: Price monitoring, package tracking, household inventory
- 📅 **Autonomous Automation**: Detect promises, create calendar events, book restaurants
- 💬 **Chat Summarization**: Intelligently summarize high-volume group chats

## Smart Agent Capabilities

Inspired by OpenClaw/Clawdbot autonomous workflows, MyceliumCortex implements specialized agents with hierarchical orchestration rather than a single primary agent managing shared workspace context.

**Vision & Image Analysis**
- Analyze freezer/pantry contents from photos
- Extract recipe ingredients from images
- Automatic household inventory tracking
- Product identification and metadata extraction

**Autonomous Monitoring**
- Track prices on products (Amazon, flights, hotels)
- Monitor package delivery (UPS, FedEx, USPS)
- Automatic alerts for changes
- 30+ concurrent monitors


**Smart Calendar Integration**
- Detect promises in conversations ("let me review tomorrow")
- Auto-create calendar events with reminders
- Cross-calendar availability checking
- Meeting coordination

**Booking Automation**
- Restaurant reservations with preference matching
- Medical/service appointment scheduling
- Hotel availability checking
- Preference learning and deduplication

**Group Chat Intelligence**
- Summarize 100+ message/day chats
- Extract key topics and decisions
- Daily digests instead of message overload
- Works with WhatsApp, Telegram, Slack

## Architecture

MyceliumCortex uses a **hierarchical coordinator→specialists model** with scoped agent contexts, whereas approaches like OpenClaw typically feature a primary agent that orchestrates tools and sub-agents around a shared workspace-based memory. This explicit separation of concerns yields clearer agent boundaries and simpler extensibility.

```
┌─────────────────────────────────────────┐
│        STRATEGIC LAYER                  │
│      (ControlCenter)                    │
│   Orchestrates what work needs doing    │
├─────────────────────────────────────────┤
│        TACTICAL LAYER                   │
│   (ConversationSupervisor,              │
│    ToolSupervisor,                      │
│    ChannelSupervisor,                   │
│    TaskSupervisor)                      │
│   Plans HOW work gets done              │
├─────────────────────────────────────────┤
│        EXECUTION LAYER                  │
│  Core Agents:                           │
│  - LLMAgent, MemoryAgent, ToolAgent     │
│  - PersonaAgent                         │
│  - WhatsApp, Telegram, Gmail,           │
│    Slack, Discord                       │
│                                         │
│  Smart Agents:                          │
│  - VisionAgent (photo analysis)         │
│  - HouseholdInventoryAgent              │
│  - CalendarPromiseAgent                 │
│  - MonitoringAgent (prices/packages)    │
│  - GroupChatSummarizerAgent             │
│  - BookingWorkflowAgent                 │
│   Does the work                         │
└─────────────────────────────────────────┘
```

**Key Differences from Monolithic Systems:**
- **No giant context window**: Each agent has its own specialized memory
- **Hierarchical decision-making**: Supervisors coordinate, agents execute
- **Scalable**: Add more agents without hitting context limits
- **Understandable**: Each layer has clear responsibilities (WHAT → HOW → DO)
- **Extensible**: Drop in new agent types without retraining everything

### Layer Responsibilities

**Strategic (ControlCenter)**
- System-wide coordination
- Resource allocation
- Long-term planning (hours to days)
- Routes user messages to appropriate supervisors

**Tactical (Supervisors)**
- Domain-specific coordination
- Agent spawning and lifecycle management
- Task routing and load balancing
- Time horizon: minutes to hours

**Execution (Agents)**
- Perform actual work
- Call LLM APIs, manage memory, execute tools
- Report results to supervisors
- Time horizon: milliseconds to seconds

## Components

### Core Execution Layer Agents

- **LLMAgent**: Calls Claude or other LLM providers
- **MemoryAgent**: Stores and retrieves conversation history
- **ToolAgent**: Executes system tools (shell, file operations)
- **PersonaAgent**: Manages conversation personas/styles

### Channel Agents (Communication)

- **WhatsAppAgent**: WhatsApp messaging via Twilio/WhatsApp Business API
- **TelegramAgent**: Telegram bot integration
- **GmailAgent**: Email sending and retrieval
- **SlackAgent**: Slack workspace messaging
- **DiscordAgent**: Discord server messaging

### Smart Execution Layer Agents (NEW)

- **VisionAgent**: Analyzes images and extracts information
  - Photo-based inventory scanning (freezer, pantry, fridge)
  - Recipe ingredient extraction
  - Product identification and metadata
  
- **HouseholdInventoryAgent**: Manages household inventory
  - Track items, quantities, and status
  - Add/remove/update inventory
  - Category-based queries
  - Integration with vision agent
  
- **CalendarPromiseAgent**: Detects promises and creates calendar events
  - Parse temporal commitments in conversations
  - Auto-create calendar events
  - Track upcoming promises
  - Cross-calendar coordination
  
- **MonitoringAgent**: Monitors prices, packages, and events
  - Price tracking with customizable intervals
  - Package tracking across carriers
  - Alert generation for changes
  - 30+ concurrent monitors
  
- **GroupChatSummarizerAgent**: Summarizes high-volume group chats
  - Daily digests of key topics
  - Highlight important discussions
  - Works with WhatsApp, Telegram, Slack
  - Reduces information overload
  
- **BookingWorkflowAgent**: Handles complex booking processes
  - Restaurant reservations with preference matching
  - Medical/service appointment scheduling
  - Hotel and flight availability checking
  - Preference learning and deduplication

## Knowledge Management & RAG

MyceliumCortex includes a built-in **Retrieval-Augmented Generation (RAG)** system for adding your own knowledge base.

**Features:**
- 📚 **Vector Database**: SQLite or Chroma-backed embeddings storage
- 🔍 **Semantic Search**: Find relevant documents using embeddings
- 📄 **Multi-Format Ingestion**: Support for `.txt`, `.md`, `.json`, and directories
- 🧠 **Smart Chunking**: Automatic text splitting with overlap for optimal retrieval
- 🔌 **Multiple Embeddings Providers**: OpenAI, Local (sentence-transformers), or Anthropic
- 🚀 **Production-Ready**: Async operations, persistence, and performance tuning

**Quick Example:**
```python
from src.rag import SQLiteVectorStore, OpenAIEmbeddings, RAGSystem, DocumentIngester

# Setup
rag = RAGSystem(
    SQLiteVectorStore(VectorStoreConfig(db_path="knowledge.db")),
    OpenAIEmbeddings()
)

# Ingest documents
await DocumentIngester.ingest_directory("./company_docs", rag)

# Query with context
result = await rag.generate_with_context(
    query="What's our vacation policy?",
    top_k=3,
    use_llm=True
)
```

**See [RAG_GUIDE.md](RAG_GUIDE.md) for detailed documentation and examples.**

### Tactical Layer Supervisors

- **ConversationSupervisor**: Manages conversation flow with LLM
  - Spawns: LLMAgent, MemoryAgent, PersonaAgent
  - Coordinates conversation turns

- **ToolSupervisor**: Manages tool execution
  - Spawns: ToolAgent instances
  - Handles tool requests from LLM

- **ChannelSupervisor**: Manages communication channels
  - Spawns: WhatsAppAgent, TelegramAgent, GmailAgent, SlackAgent, DiscordAgent
  - Handles multi-platform messaging

- **TaskSupervisor** (NEW): Coordinates complex workflows
  - Orchestrates smart agents
  - Manages multi-step automations
  - Handles agent coordination and synchronization

### Strategic Layer

- **ControlCenter**: Coordinates all supervisors
  - Routes user messages to conversation supervisor
  - Monitors system health
  - Allocates resources
  - Manages HostManager for agent registration
  - Triggers workflow automations

### Supporting Systems

- **Message Bus**: In-memory topic-based pub/sub (or Redis-backed for distributed deployments)
  - Decouples webhook endpoints from agent processing
  - Enables async message routing
- **PersistentMemory**: SQLite-backed storage
  - Stores conversation history
  - Caches for fast retrieval
  - Inventory and booking tracking
- **HostManager**: Local agent registry and lifecycle management

  - Persists agent configs to `~/.myceliumcortex/agents.json`
  - Starts/stops agents as asyncio tasks
- **SecretsStore**: File-based secrets (API keys, tokens)
  - Stored in `~/.myceliumcortex/secrets.json`
  - Optional encryption support

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables (Windows PowerShell)

```powershell
# Telegram bot token (get from BotFather)
$env:TELEGRAM_BOT_TOKEN = "123456:ABC-DEF-GHI..."

# LLM provider API key
$env:ANTHROPIC_API_KEY = "sk-ant-..."
# OR
$env:OPENAI_API_KEY = "sk-..."

# Optional: API key for management endpoints
$env:ADMIN_API_KEY = "your-secret-key"
```

Or on Windows `cmd`:
```batch
set TELEGRAM_BOT_TOKEN=123456:ABC-DEF-GHI...
set ANTHROPIC_API_KEY=sk-ant-...
set ADMIN_API_KEY=your-secret-key
```

### 3. Start the Server

```bash
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```

The server initializes:
- ✓ ControlCenter (strategic coordinator)
- ✓ HostManager (agent registry)
- ✓ Tactical supervisors (Conversation, Tool, Channel)
- ✓ MessageRouterAgent (webhook → agent routing)
- ✓ PersistentMemory (SQLite database)

### 4. Expose to Internet (ngrok)

Telegram needs a public webhook URL:

```bash
ngrok http 8000
```

You'll see: `https://abc123def456.ngrok.io -> http://localhost:8000`

### 5. Configure Telegram Webhook

```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://abc123def456.ngrok.io/v1/webhook/telegram"
```

### 6. Send a Message

Open Telegram and message your bot. The flow:

1. Webhook → `/v1/webhook/telegram` endpoint
2. Message stored in SQLite
3. Published to message bus
4. MessageRouterAgent routes to ControlCenter
5. ConversationSupervisor calls LLMAgent
6. Response generated and sent back via Telegram Bot API

**See [USAGE.md](USAGE.md) for detailed walkthrough and examples.**

## Project Structure

```
MyceliumCortex/
├── src/
│   ├── core/
│   │   ├── types.py              # AgentConfig, AgentMessage, etc.
│   │   └── agent.py              # BaseAgent, ExecutionAgent, TacticalSupervisor, StrategicCoordinator
│   │
│   ├── agents/
│   │   ├── execution_agents.py   # LLMAgent, MemoryAgent, ToolAgent, PersonaAgent
│   │   │                          # WhatsAppAgent, TelegramAgent, GmailAgent, SlackAgent, DiscordAgent
│   │   ├── aux_agents.py         # MessageRouterAgent, WebhookReceiverAgent
│   │   └── integrations.py       # Channel API helpers (Telegram, WhatsApp, etc.)
│   │
│   ├── supervisors/
│   │   ├── tactical_supervisors.py  # ConversationSupervisor, ToolSupervisor, ChannelSupervisor
│   │   └── strategic.py             # ControlCenter
│   │
│   ├── messaging/
│   │   ├── message_bus.py        # InMemoryMessageBus (pub/sub)
│   │   └── redis_bus.py          # RedisMessageBus (optional, distributed)
│   │
│   ├── storage/
│   │   └── sqlite_memory.py      # PersistentMemory (SQLite with async/sync fallback)
│   │
│   ├── host/
│   │   ├── host_manager.py       # HostManager (agent registry & lifecycle)
│   │   └── secrets.py            # SecretsStore (API keys, tokens)
│   │
│   └── api/
│       └── server.py             # FastAPI gateway (webhooks, HTTP endpoints)
│
├── tests/
│   ├── test_flow.py              # Webhook → memory flow test
│   └── test_e2e.py               # End-to-end LLM integration test
│
├── myceliumcortex.py             # CLI wrapper (agent management commands)
├── requirements.txt              # Python dependencies
├── USAGE.md                      # Detailed usage guide
├── CHANNELS.md                   # Channel integration guide
├── README.md                     # This file
└── IDEA.md                       # Architecture principles
```

## Message Flow

### Incoming Message (Telegram/WhatsApp)

```
Webhook → PersistentMemory (stored) → MessageBus (published) 
  → MessageRouterAgent → ControlCenter → ConversationSupervisor 
    → (MemoryAgent, PersonaAgent, LLMAgent) → ChannelSupervisor 
      → TelegramAgent (sends via Bot API) → User receives response
```

### Shell Command Execution (/run)

```
/run command → ConversationSupervisor (detect /run prefix)
  → ToolSupervisor → ToolAgent (execute shell)
    → MemoryAgent (store command + result)
      → ChannelSupervisor → TelegramAgent (send result)
        → User receives output
```

## Features Implemented

✅ **Fully Functional**
- Hierarchical 3-layer agent architecture (Strategic/Tactical/Execution)
- Message bus for async routing
- Persistent SQLite memory with conversation history
- Real Telegram Bot API integration (sendMessage)
- Shell command execution from chat (`/run`, `/exec`, `/shell`)
- Host-mode agent registry and management
- FastAPI webhook endpoints
- Optional Redis message bus for distributed deployments

⏳ **Planned**
- WhatsApp/Twilio real integration (sendMessage + webhook parsing)
- Gmail agent (send/receive emails)
- Slack/Discord real integrations
- WebSocket push notifications to mobile
- Webhook signature verification for security
- Rate limiting and command whitelisting
- Encryption for stored secrets
- Multi-model support (GPT etc.)

## Configuration

### Environment Variables

```bash
# LLM Provider
ANTHROPIC_API_KEY=sk-ant-...     # for Claude
OPENAI_API_KEY=sk-...             # for GPT

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC...

# Security
ADMIN_API_KEY=your-secret-key     # for management API

# Telegram Security: Chat ID whitelist (comma-separated; if empty, allows all)
TELEGRAM_ALLOWED_CHAT_IDS=123456789,987654321

# Shell Command Security
# Whitelist (comma-separated; if empty, allows all non-blacklisted commands)
SHELL_COMMAND_WHITELIST=ls,dir,python,echo,pwd

# Blacklist (default blocks dangerous commands)
SHELL_COMMAND_BLACKLIST=rm,del,format,dd,mkfs

# Optional: Message Bus
USE_REDIS_BUS=true                # enable Redis (default: in-memory)
REDIS_URL=redis://localhost:6379/0
```

### Persistent Files

- **Agent registry**: `~/.myceliumcortex/agents.json`
- **Secrets**: `~/.myceliumcortex/secrets.json`
- **Database**: `./data/myceliumcortex.db`
- **Logs**: `./myceliumcortex.log`

## Security

### Telegram Webhook Verification

✅ **Enabled by default** (requires `TELEGRAM_BOT_TOKEN`)

- Verifies HMAC-SHA256 signature in `X-Telegram-Bot-Api-Secret-Hash` header
- Rejects unsigned or tampered webhooks with 401 Unauthorized
- **Setup**: Set your webhook with a secret token via Telegram Bot API

```bash
# Include secret_token when setting webhook
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<URL>&secret_token=<SECRET>"
```

### Chat ID Whitelist

**Optional but recommended**

```bash
# Only allow specific chat IDs to send messages
$env:TELEGRAM_ALLOWED_CHAT_IDS = "123456789,987654321"
```

If not set, all users with access to the bot can message it. If set, only whitelisted IDs can interact.

### Shell Command Security

**Blacklist** (always enforced):
- Blocks: `rm`, `del`, `format`, `dd`, `mkfs` by default
- Prevents accidental data loss

**Whitelist** (optional, more restrictive):
```bash
# Only allow specific commands
$env:SHELL_COMMAND_WHITELIST = "ls,dir,python,echo,pwd"
```

If not set, all commands except blacklisted ones are allowed.
If set, **only** whitelisted commands execute.

### Example: Secure Setup

```powershell
# Set all security variables
$env:TELEGRAM_BOT_TOKEN = "123456:ABC..."
$env:TELEGRAM_ALLOWED_CHAT_IDS = "123456789"  # Your chat ID only
$env:SHELL_COMMAND_WHITELIST = "ls,pwd,echo"  # Safe commands only
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:ADMIN_API_KEY = "super-secret-key"
```

Then start the server:
```bash
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```

Now:
- ✓ Only your Telegram chat can send messages
- ✓ Only `ls`, `pwd`, `echo` commands are allowed
- ✓ Webhook signatures are verified
- ✓ Management API is protected with API key

## Design Principles (from IDEA.md)

1. **Hierarchy Mirrors Organization**
   - ControlCenter = C-suite (strategic decisions)
   - Supervisors = Department heads (tactical coordination)
   - Agents = Individual workers (execution)

2. **Temporal Stratification**
   - Strategic: Hours to days (long-term planning)
   - Tactical: Minutes to hours (coordination)
   - Execution: Milliseconds to seconds (doing work)

3. **Separation of Concerns**
   - Each layer has defined responsibilities
   - Minimal coupling between layers
   - Messages flow through well-defined channels

4. **Information Abstraction**
   - Higher layers don't need implementation details
   - Lower layers don't know about strategic goals
   - Each layer sees only what it needs

5. **Autonomy at Each Level**
   - No micromanagement
   - Agents make local decisions
   - Supervisors coordinate autonomously

## Usage Examples

### Chat with AI
```
User: What is the capital of France?
Bot: The capital of France is Paris...
```

### Execute Shell Commands
```
User: /run ipconfig
Bot: Windows IP Configuration
     Ethernet adapter Ethernet:
     IPv4 Address . . . . . . : 192.168.1.100
     ...
```

### Check Status
```
User: /run python --version
Bot: Python 3.10.0
```

## Documentation

- **[USAGE.md](USAGE.md)** — Detailed step-by-step walkthrough
- **[CHANNELS.md](CHANNELS.md)** — Channel integration (Telegram, WhatsApp, Gmail, etc.)
- **[IDEA.md](IDEA.md)** — Architecture principles
- **Code documentation** — Docstrings throughout `src/` modules

## API Reference

See [USAGE.md](USAGE.md) for HTTP endpoints:
- `POST /v1/message` — Send message
- `POST /v1/webhook/telegram` — Telegram webhook
- `POST /v1/webhook/whatsapp` — WhatsApp webhook
- `GET /v1/host/agents` — List agents
- `POST /v1/host/agents` — Register agent
- `POST /v1/host/agents/{id}/enable` — Start agent
- `POST /v1/host/agents/{id}/disable` — Stop agent

## Troubleshooting

**Bot not responding?**
- Check `TELEGRAM_BOT_TOKEN` is set
- Verify ngrok URL in webhook
- Check server logs: `tail -f myceliumcortex.log`

**Command not executing?**
- Verify format: `/run command` (space after `/run`)
- Check permissions (some commands need admin)
- View logs for error details

**LLM not responding?**
- Verify API key: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- Check API balance and rate limits
- Confirm internet connection

## Contributing

Contributions welcome! This is an educational project demonstrating hierarchical multi-agent architecture.

Areas for contribution:
- WhatsApp/Twilio integration
- Gmail agent implementation
- Discord/Slack real integrations
- WebSocket support
- Security hardening (webhook signing, encryption)
- Performance optimization
- Additional LLM providers

## License

MIT
