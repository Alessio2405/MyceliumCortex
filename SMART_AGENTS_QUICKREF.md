# Quick Reference: Autonomous Smart Agents

## Overview
MyceliumCortex includes **6 powerful smart agents** that handle complex, multi-step autonomous workflows for household management, monitoring, scheduling, and booking.

**Inspiration**: MyceliumCortex is inspired by OpenClaw/Clawdbot-style autonomous workflows, but uses explicit hierarchical orchestration among specialized agents (coordinator→specialists with scoped contexts) rather than a primary agent managing shared workspace memory.

---

## 1. 🖼️ VisionAgent - Photo Analysis

**What it does:** Analyzes images and extracts information using Claude's vision.

**Use cases:**
- Take photos of freezer → get inventory list
- Snap recipe → extract ingredients
- Picture of product → get details and URL

**Key methods:**
```python
analyze_image(image_path, prompt)      # Analyze with custom prompt
execute_action("inventory_scan", {...})  # Scan for inventory
execute_action("extract_recipe", {...})  # Extract recipe data
```

**Example:**
```python
agent = VisionAgent(config)
result = await agent.analyze_image("freezer.jpg", 
    "List all frozen items and quantities")
```

---

## 2. 📦 HouseholdInventoryAgent - Item Tracking

**What it does:** Tracks household items, quantities, and categories.

**Use cases:**
- Track what's in your freezer/pantry/fridge
- Update quantities as you use items
- Query inventory by category

**Key methods:**
```python
execute_action("add_items", {"items": [...]})     # Add items
execute_action("get_inventory", {"category": "..."}) # Query
execute_action("update_quantity", {...})          # Update counts
execute_action("remove_item", {"item_name": "..."}) # Remove
```

**Example:**
```python
agent = HouseholdInventoryAgent(config)
await agent.execute_action("add_items", {
    "items": [
        {"name": "Dumplings", "quantity": 5, "category": "frozen"}
    ]
})
```

---

## 3. 📅 CalendarPromiseAgent - Smart Scheduling

**What it does:** Detects promises in text and creates calendar events automatically.

**Use cases:**
- "Let me review this tomorrow" → creates calendar event
- "Call you next week" → reminder set
- Detect all temporal commitments in conversation

**Key methods:**
```python
execute_action("detect_promise", {"text": "..."}) # Detect commitment
execute_action("create_event", {...})            # Create calendar event
execute_action("get_upcoming", {"days": 7})      # See upcoming promises
```

**Example:**
```python
agent = CalendarPromiseAgent(config)
promise = await agent.execute_action("detect_promise", {
    "text": "Let me review this tomorrow and get back to you"
})
# Auto-creates calendar event for tomorrow
```

---

## 4. 🔍 MonitoringAgent - Price & Package Tracking

**What it does:** Continuously monitors prices, packages, and availability.

**Use cases:**
- Track Amazon product prices (check every 6 hours)
- Monitor flight prices for trips
- Track package deliveries (UPS, FedEx, USPS)
- Run 30+ simultaneous monitors

**Key methods:**
```python
execute_action("add_price_monitor", {...})      # Start tracking a URL
execute_action("add_package_tracker", {...})     # Track shipment
execute_action("check_monitor", {...})          # Check status
execute_action("get_all_monitors", {})          # View all monitors
```

**Example:**
```python
agent = MonitoringAgent(config)

# Monitor product price
await agent.execute_action("add_price_monitor", {
    "url": "https://amazon.com/macbook",
    "check_interval_hours": 6  # Check every 6 hours
})

# Track package
await agent.execute_action("add_package_tracker", {
    "tracking_number": "1Z999AA10123456784",
    "carrier": "UPS"
})
```

---

## 5. 💬 GroupChatSummarizerAgent - Chat Intelligence

**What it does:** Summarizes high-volume group chats (100+ msgs/day).

**Use cases:**
- Get daily digest of team Slack instead of reading all messages
- Summarize WhatsApp group chats
- Identify key decisions and discussions
- Catch important mentions

**Key methods:**
```python
execute_action("summarize_chat", {...})        # Summarize messages
execute_action("get_recent_summaries", {...})  # View past summaries
```

**Example:**
```python
agent = GroupChatSummarizerAgent(config)

summary = await agent.execute_action("summarize_chat", {
    "messages": [msg1, msg2, msg3, ...],
    "chat_name": "team-projects"
})
# Returns: key topics, important messages, decisions
```

---

## 6. 🎫 BookingWorkflowAgent - Reservation Automation

**What it does:** Handles complex booking workflows with preference matching.

**Use cases:**
- Book restaurant with preference matching
- Schedule medical appointments
- Check hotel/flight availability
- Coordinate with multiple calendars

**Key methods:**
```python
execute_action("check_availability", {...})  # Check open slots
execute_action("book_restaurant", {...})     # Make reservation
execute_action("book_appointment", {...})    # Schedule appointment
```

**Example:**
```python
agent = BookingWorkflowAgent(config)

# Check availability
available = await agent.execute_action("check_availability", {
    "service_type": "restaurant",
    "date_range": {"start": "2026-02-10", "end": "2026-02-15"}
})

# Book restaurant
booking = await agent.execute_action("book_restaurant", {
    "restaurant_name": "Chez Maurice",
    "date": "2026-02-12",
    "party_size": 4,
    "preferences": {
        "quiet": True,
        "window_seating": True
    }
})
```

---

## Complete Workflow Example

**Scenario: Update freezer inventory after Costco trip**

```python
# 1. Take photos of freezer
photos = ["freezer1.jpg", "freezer2.jpg", "freezer3.jpg"]

# 2. Vision agent analyzes
vision_agent = VisionAgent(vision_config)
analysis = await vision_agent.execute_action("inventory_scan", {
    "image_paths": photos,
    "category": "frozen_foods"
})

# 3. Extract items from analysis
items = parse_analysis(analysis)

# 4. Add to inventory tracking
inventory_agent = HouseholdInventoryAgent(inventory_config)
await inventory_agent.execute_action("add_items", {
    "items": items
})

# 5. Auto-remove redundant grocery list items
# (don't buy ice cream again if you have 3 containers)
```

---

## Configuration Templates

### VisionAgent
```json
{
  "agent_id": "vision_1",
  "level": "execution",
  "capabilities": ["analyze_image", "inventory_scan", "extract_recipe"],
  "config": {
    "provider": "anthropic",
    "api_key": "sk-ant-...",
    "model": "claude-3-5-sonnet-20241022"
  }
}
```

### HouseholdInventoryAgent
```json
{
  "agent_id": "inventory_1",
  "level": "execution",
  "capabilities": ["add_items", "get_inventory", "update_quantity"],
  "config": {
    "db_path": "data/inventory.db"
  }
}
```

### MonitoringAgent
```json
{
  "agent_id": "monitor_1",
  "level": "execution",
  "capabilities": ["add_price_monitor", "add_package_tracker"],
  "config": {
    "db_path": "data/monitoring.db",
    "default_check_interval": 6
  }
}
```

---

## Architecture Approach: Coordinator→Specialists vs. Primary Agent + Workspace

MyceliumCortex uses **hierarchical three-layer coordination** inspired by OpenClaw/Clawdbot, with a different organizational model.

| Aspect | OpenClaw/Clawdbot (Primary Agent + Workspace) | MyceliumCortex (Coordinator→Specialists) |
|--------|----------|---|
| **Orchestration Model** | Primary agent with tools/sub-agents around shared workspace | Hierarchical supervisors coordinating specialized agents |
| **Memory Scope** | Shared workspace context (primary agent sees everything) | Scoped per agent + supervisor views |
| **Scaling** | Limited by primary agent's context window | Agents scale independently |
| **Adding Features** | Add new tools/skills, retrain prompts | Add new agent types, connect to supervisor |
| **Debuggability** | Trace primary agent's reasoning | Trace coordinator decisions + agent boundaries |
| **Coordination Logic** | Primarily in primary agent's reasoning | Explicit in supervisors (tactical/strategic layers) |

---

## Documentation

- **Full Details**: See [AUTONOMOUS_FEATURES.md](AUTONOMOUS_FEATURES.md)
- **Working Examples**: See [examples_smart_agents.py](examples_smart_agents.py)
- **Architecture**: See [ARCHITECTURE.txt](ARCHITECTURE.txt)


---

## Next Steps

1. **Configure your API keys** (ANTHROPIC_API_KEY env var)
2. **Initialize agents** with your config
3. **Run examples** with `python examples_smart_agents.py`
4. **Integrate** into your workflows with message bus or supervisors
5. **Extend** with custom prompts and behaviors

---

## Support & Extension

Each agent is built on the base `ExecutionAgent` class, making them easy to extend:

```python
class MyCustomAgent(ExecutionAgent):
    async def on_message(self, message: AgentMessage):
        # Handle incoming messages
        pass
    
    async def execute_action(self, action: str, payload: Dict):
        # Execute custom actions
        pass
```

See [EXTENSIONS.md](EXTENSIONS.md) for full extension guide.
