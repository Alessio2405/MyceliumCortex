# MiniClaw - Complete Project Index

## 📖 Where to Start

**First time?** → **[GETTING_STARTED.md](GETTING_STARTED.md)**  
**Want quick overview?** → **[README.md](README.md)**  
**5-minute setup?** → **[QUICKSTART.md](QUICKSTART.md)**  

## 📚 Documentation Map

### For Users
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Step-by-step setup guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick commands reference
- **[README.md](README.md)** - Features and architecture overview

### For Developers
- **[ARCHITECTURE.txt](ARCHITECTURE.txt)** - Visual diagrams and flows
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical deep dive
- **[EXTENSIONS.md](EXTENSIONS.md)** - How to create custom agents
- **[CHANNELS.md](CHANNELS.md)** - Channel agents documentation

### For Reference
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Completion summary
- **[IDEA.md](IDEA.md)** - Your original architecture specification

### Code Examples
- **[examples.py](examples.py)** - 5 practical examples

## 🗂️ File Structure

```
miniclaw/
│
├─ 📄 Setup Files
│  ├── miniclaw.py          ← Main CLI entry point
│  ├── setup.py             ← Package installation
│  ├── pyproject.toml       ← Project metadata
│  └── requirements.txt     ← Python dependencies
│
├─ 📚 Documentation (Read These!)
│  ├── GETTING_STARTED.md   ← Start here
│  ├── QUICKSTART.md        ← Quick reference
│  ├── README.md            ← Overview
│  ├── ARCHITECTURE.txt     ← Diagrams
│  ├── IMPLEMENTATION.md    ← Technical details
│  ├── EXTENSIONS.md        ← Customization
│  ├── PROJECT_SUMMARY.md   ← Completion summary
│  └── IDEA.md              ← Your spec
│
├─ 🧪 Examples & Testing
│  └── examples.py          ← Code examples
│
└─ 📦 Source Code (Read These Too!)
   └── src/
       ├── main.py          ← Main class
       ├── core/            ← Agent base classes
       ├── agents/          ← Execution agents
       ├── supervisors/     ← Tactical & Strategic layers
       └── config/          ← Configuration system
```

## 🚀 Quick Start (30 seconds)

```bash
# 1. Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python miniclaw.py chat
```

## 📖 Reading Order

### Beginner (Want to use it)
1. [GETTING_STARTED.md](GETTING_STARTED.md) - How to install
2. [QUICKSTART.md](QUICKSTART.md) - Quick reference
3. [README.md](README.md) - What it does

### Intermediate (Want to understand it)
4. [ARCHITECTURE.txt](ARCHITECTURE.txt) - How it works
5. [examples.py](examples.py) - See it in action
6. [README.md](README.md) - Architecture section
7. [CHANNELS.md](CHANNELS.md) - Multi-channel messaging

### Advanced (Want to extend it)
8. [IMPLEMENTATION.md](IMPLEMENTATION.md) - Technical details
9. [EXTENSIONS.md](EXTENSIONS.md) - Create custom agents
10. [CHANNELS.md](CHANNELS.md) - Create custom channels
11. Source code in `src/` - Implementation

### Reference
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overview of everything
- [IDEA.md](IDEA.md) - Original architecture spec

## 🔍 Find What You Need

### "How do I install?"
→ [GETTING_STARTED.md](GETTING_STARTED.md)

### "How do I use it?"
→ [QUICKSTART.md](QUICKSTART.md)

### "What can it do?"
→ [README.md](README.md)

### "How does it work?"
→ [ARCHITECTURE.txt](ARCHITECTURE.txt)

### "How do I extend it?"
→ [EXTENSIONS.md](EXTENSIONS.md)

### "How do I add channels?"
→ [CHANNELS.md](CHANNELS.md)

### "I need examples"
→ [examples.py](examples.py)

### "Full technical details?"
→ [IMPLEMENTATION.md](IMPLEMENTATION.md)

### "Project overview?"
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## 💡 Key Concepts

### Architecture (3 Layers)
- **Strategic** - System coordination (ControlCenter)
- **Tactical** - Domain coordination (Supervisors)
- **Execution** - Actual work (Agents)

### Core Types
- **AgentMessage** - Message between agents
- **AgentReport** - Report from child to parent
- **UserMessage** - User input
- **ConversationContext** - Persistent conversation state

### Agent Types
- **BaseAgent** - Foundation for all agents
- **ExecutionAgent** - Workers (LLMAgent, MemoryAgent, etc.)
- **TacticalSupervisor** - Coordinators (ConversationSupervisor, ToolSupervisor)
- **StrategicCoordinator** - System orchestrator (ControlCenter)

### Main Classes
- **MiniClawAssistant** - Main entry point
- **ControlCenter** - Strategic layer coordinator
- **ConversationSupervisor** - Conversation orchestrator
- **ToolSupervisor** - Tool orchestrator
- **LLMAgent** - Calls Claude/GPT
- **MemoryAgent** - Manages conversation history
- **ToolAgent** - Executes tools
- **PersonaAgent** - Manages personas

## 🎯 Common Tasks

### Start Using MiniClaw
1. Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. Run `pip install -r requirements.txt`
3. Set `ANTHROPIC_API_KEY` environment variable
4. Run `python miniclaw.py chat`

### Understand How It Works
1. Read [ARCHITECTURE.txt](ARCHITECTURE.txt)
2. Look at [IMPLEMENTATION.md](IMPLEMENTATION.md)
3. Review [examples.py](examples.py)
4. Read source code in `src/`

### Create a Custom Agent
1. Read [EXTENSIONS.md](EXTENSIONS.md)
2. See examples in [EXTENSIONS.md](EXTENSIONS.md)
3. Check [examples.py](examples.py) for structure
4. Look at `src/agents/execution_agents.py` for reference

### Add a New Command
1. See [EXTENSIONS.md](EXTENSIONS.md) - Creating Custom Supervisors
2. Look at `miniclaw.py` for CLI structure
3. Study `src/supervisors/tactical_supervisors.py`

### Troubleshoot Issues
1. Check [GETTING_STARTED.md](GETTING_STARTED.md) - Common Issues section
2. Verify setup with [QUICKSTART.md](QUICKSTART.md)
3. Check `examples.py` for expected behavior
4. Review [ARCHITECTURE.txt](ARCHITECTURE.txt) for concepts

## 📊 Statistics

| Aspect | Details |
|--------|---------|
| **Total Files** | 13 source + 9 documentation |
| **Lines of Code** | ~2,500 |
| **Core Agents** | 4 |
| **Channel Agents** | 5 |
| **Supervisors** | 3 |
| **Base Classes** | 4 |
| **Message Types** | 4 |
| **CLI Commands** | 5 |
| **Examples** | 5 |

## 🔗 Related Files

### By Category

**Entry Points**
- [miniclaw.py](miniclaw.py) - CLI
- [src/main.py](src/main.py) - Main class

**Architecture**
- [src/core/agent.py](src/core/agent.py) - Base classes
- [src/core/types.py](src/core/types.py) - Message types

**Agents**
- [src/agents/execution_agents.py](src/agents/execution_agents.py) - Execution layer

**Supervisors**
- [src/supervisors/tactical_supervisors.py](src/supervisors/tactical_supervisors.py) - Tactical layer
- [src/supervisors/strategic.py](src/supervisors/strategic.py) - Strategic layer

**Configuration**
- [src/config/config.py](src/config/config.py) - Config management
- [requirements.txt](requirements.txt) - Python dependencies

## ✨ What's Included

✅ Complete hierarchical multi-agent system  
✅ LLM integration (Claude & OpenAI)  
✅ Conversation memory management  
✅ Tool execution framework  
✅ CLI interface with 5 commands  
✅ Comprehensive documentation  
✅ Working examples  
✅ Easy extension system  

## 🚀 Next Steps

1. **Start**: [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Learn**: [README.md](README.md)
3. **Understand**: [ARCHITECTURE.txt](ARCHITECTURE.txt)
4. **Extend**: [EXTENSIONS.md](EXTENSIONS.md)
5. **Code**: Look at `src/`

## 📞 Questions?

- **Setup issues?** → [GETTING_STARTED.md](GETTING_STARTED.md)
- **How to use?** → [QUICKSTART.md](QUICKSTART.md)
- **How it works?** → [ARCHITECTURE.txt](ARCHITECTURE.txt)
- **Code examples?** → [examples.py](examples.py)
- **Full details?** → [IMPLEMENTATION.md](IMPLEMENTATION.md)

---

**Happy coding!** 🎉

Start with [GETTING_STARTED.md](GETTING_STARTED.md) if this is your first time.
