# Autonomous Smart Features for MyceliumCortex

This document outlines the autonomous smart agent features integrated into MyceliumCortex for complex, multi-step workflows.

> **Inspiration**: These features are inspired by OpenClaw/Clawdbot-style autonomous workflows, but MyceliumCortex uses a hierarchical coordinator→specialists model with scoped contexts, whereas OpenClaw's common pattern is a primary agent that orchestrates tools (and optionally sub-agents) around a workspace-based memory model.


## Vision & Image Analysis

### VisionAgent
Analyzes images and extracts information using Claude's vision capabilities.

**Capabilities:**
- Image analysis with custom prompts
- Household inventory scanning (freezer, pantry, fridge)
- Recipe ingredient extraction from photos
- Product identification and details extraction

**Usage Example:**
```python
from src.agents import VisionAgent
from src.core.types import AgentConfig, AgentLevel

config = AgentConfig(
    agent_id="vision_1",
    level=AgentLevel.EXECUTION,
    capabilities=["analyze_image", "inventory_scan", "extract_recipe"],
    config={
        "provider": "anthropic",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "claude-3-5-sonnet-20241022"
    }
)

agent = VisionAgent(config)

# Analyze freezer inventory
result = await agent.analyze_image(
    image_path="freezer.jpg",
    prompt="List all frozen items and estimate quantities"
)

# Scan multiple images for inventory
inventory = await agent.execute_action("inventory_scan", {
    "image_paths": ["freezer1.jpg", "freezer2.jpg"],
    "category": "frozen_foods"
})

# Extract recipe ingredients
recipe = await agent.execute_action("extract_recipe", {
    "image_path": "recipe.jpg"
})
```

## Household Inventory Management

### HouseholdInventoryAgent
Tracks household inventory, quantities, and status.

**Features:**
- Add/remove items with metadata (category, quantity, status)
- Update quantities as items are used
- Query inventory by category
- Integration with vision agent for photo-based inventory scanning

**Usage Example:**
```python
from src.agents import HouseholdInventoryAgent

config = AgentConfig(
    agent_id="inventory_1",
    level=AgentLevel.EXECUTION,
    capabilities=["add_items", "get_inventory", "update_quantity"],
    config={"db_path": "household_inventory.db"}
)

agent = HouseholdInventoryAgent(config)

# Add items after scanning freezer
await agent.execute_action("add_items", {
    "items": [
        {"name": "Dumplings (frozen)", "category": "frozen_foods", "quantity": 5, "unit": "boxes"},
        {"name": "Ice cream", "category": "frozen_foods", "quantity": 2, "unit": "containers"},
        {"name": "Vegetables (mixed)", "category": "frozen_foods", "quantity": 3, "unit": "bags"}
    ]
})

# Get all items in a category
frozen = await agent.execute_action("get_inventory", {
    "category": "frozen_foods"
})

# Update quantity as items are used
await agent.execute_action("update_quantity", {
    "item_name": "Dumplings (frozen)",
    "quantity": 3
})
```

## Autonomous Promise & Calendar Management

### CalendarPromiseAgent
Detects promises in conversations and automatically creates calendar events.

**Features:**
- Detect temporal commitments ("let me review this tomorrow")
- Auto-create calendar events for promises
- Track upcoming promises
- Integration with calendar systems

**Usage Example:**
```python
from src.agents import CalendarPromiseAgent

config = AgentConfig(
    agent_id="promise_1",
    level=AgentLevel.EXECUTION,
    capabilities=["detect_promise", "create_event", "get_upcoming"],
    config={"db_path": "promises.db"}
)

agent = CalendarPromiseAgent(config)

# Detect promise in text
promise = await agent.execute_action("detect_promise", {
    "text": "Let me review this document tomorrow and get back to you"
})

# Get upcoming promises
upcoming = await agent.execute_action("get_upcoming", {
    "days": 7
})
```

## Monitoring & Automation

### MonitoringAgent
Monitors prices, packages, and other items for changes.

**Features:**
- Price monitoring with periodic checks
- Package tracking across multiple carriers
- Customizable check intervals
- Alert generation for changes

**Usage Example:**
```python
from src.agents import MonitoringAgent

config = AgentConfig(
    agent_id="monitor_1",
    level=AgentLevel.EXECUTION,
    capabilities=["add_price_monitor", "add_package_tracker", "check_monitor"],
    config={"db_path": "monitoring.db"}
)

agent = MonitoringAgent(config)

# Add price monitor for a product
monitor = await agent.execute_action("add_price_monitor", {
    "url": "https://www.amazon.com/product-xyz",
    "check_interval_hours": 6
})

# Track a package
package = await agent.execute_action("add_package_tracker", {
    "tracking_number": "1Z999AA10123456784",
    "carrier": "UPS"
})

# Check specific monitor status
status = await agent.execute_action("check_monitor", {
    "monitor_id": monitor["monitor_id"]
})

# Get all monitors
all_monitors = await agent.execute_action("get_all_monitors", {})
```

## Group Chat Summarization

### GroupChatSummarizerAgent
Summarizes high-volume group chat messages to key topics.

**Features:**
- Summarize group chats (WhatsApp, Telegram, Slack)
- Identify key discussion topics
- Extract important mentions
- Highlight relevant messages

**Usage Example:**
```python
from src.agents import GroupChatSummarizerAgent

config = AgentConfig(
    agent_id="summarizer_1",
    level=AgentLevel.EXECUTION,
    capabilities=["summarize_chat", "get_recent_summaries"],
    config={"db_path": "summaries.db"}
)

agent = GroupChatSummarizerAgent(config)

# Summarize group messages
summary = await agent.execute_action("summarize_chat", {
    "messages": [
        {"text": "Hey, we should meet tomorrow", "timestamp": "2026-02-05T10:00Z"},
        {"text": "How about 3pm?", "timestamp": "2026-02-05T10:05Z"},
        # ... more messages
    ],
    "chat_name": "team-planning"
})

# Get recent summaries
recent = await agent.execute_action("get_recent_summaries", {
    "chat_name": "team-planning",
    "days": 7
})
```

## Complex Booking Workflows

### BookingWorkflowAgent
Handles multi-step booking processes (restaurants, appointments, hotels, etc).

**Features:**
- Restaurant reservations (with Resy/OpenTable integration)
- Medical/service appointments
- Flight bookings
- Hotel reservations
- Availability checking
- Preference matching

**Usage Example:**
```python
from src.agents import BookingWorkflowAgent

config = AgentConfig(
    agent_id="booking_1",
    level=AgentLevel.EXECUTION,
    capabilities=["book_restaurant", "book_appointment", "check_availability"],
    config={"db_path": "bookings.db"}
)

agent = BookingWorkflowAgent(config)

# Check availability
available = await agent.execute_action("check_availability", {
    "service_type": "restaurant",
    "date_range": {
        "start": "2026-02-10",
        "end": "2026-02-20"
    }
})

# Book restaurant
booking = await agent.execute_action("book_restaurant", {
    "restaurant_name": "The Italian Place",
    "date": "2026-02-15",
    "party_size": 4,
    "preferences": {
        "no_pullout_beds": True,
        "quiet_section": True
    }
})

# Book appointment
appointment = await agent.execute_action("book_appointment", {
    "service_type": "dentist_cleaning",
    "provider": "Dr. Smith DDS",
    "preferred_date": "2026-02-20"
})
```

## Integration Architecture

These agents integrate with the existing MyceliumCortex hierarchy:

```
┌─────────────────────────────────────────┐
│        STRATEGIC LAYER                  │
│      (ControlCenter)                    │
└─────────────────────────────────────────┘
           ↓ Routes & Coordinates
┌─────────────────────────────────────────┐
│        TACTICAL LAYER                   │
│   (TaskSupervisor)                      │
│   - Orchestrates complex workflows      │
│   - Manages agent coordination          │
└─────────────────────────────────────────┘
           ↓ Spawns & Manages
┌─────────────────────────────────────────┐
│        EXECUTION LAYER                  │
│   Vision, Inventory, Promise,           │
│   Monitoring, Chat Summary, Booking     │
│   Agents + Original Agents              │
└─────────────────────────────────────────┘
```

## Example Workflows

### Complete Freezer Inventory Workflow

```python
async def update_freezer_inventory():
    """Take photos, analyze, and update inventory."""
    
    # 1. User takes photos of freezer contents
    freezer_photos = ["freezer1.jpg", "freezer2.jpg", "freezer3.jpg"]
    
    # 2. Vision agent analyzes
    vision_agent = VisionAgent(vision_config)
    analysis = await vision_agent.execute_action("inventory_scan", {
        "image_paths": freezer_photos,
        "category": "frozen_foods"
    })
    
    # 3. Extract items from vision analysis
    items = parse_vision_results(analysis)
    
    # 4. Update inventory
    inventory_agent = HouseholdInventoryAgent(inventory_config)
    await inventory_agent.execute_action("add_items", {
        "items": items
    })
    
    # 5. Generate grocery list adjustments
    # (dedup with existing items, remove redundant purchases)
```

### Restaurant Booking with Calendar Integration

```python
async def book_dinner_out():
    """Detect dinner plan and automatically book restaurant."""
    
    # 1. Monitoring detects availability on Resy
    monitor_agent = MonitoringAgent(monitor_config)
    
    # 2. Calendar agent checks mutual availability
    calendar_agent = CalendarPromiseAgent(calendar_config)
    upcoming = await calendar_agent.execute_action("get_upcoming", {"days": 7})
    
    # 3. Booking agent reserves
    booking_agent = BookingWorkflowAgent(booking_config)
    reservation = await booking_agent.execute_action("book_restaurant", {
        "restaurant_name": "Chez Maurice",
        "date": "2026-02-15",
        "party_size": 2,
        "preferences": {"quiet": True, "window_seating": True}
    })
```

### High-Volume Group Chat Management

```python
async def summarize_group_chats():
    """Daily summary of all group chats."""
    
    chats = ["team-planning", "family-group", "friends-weekend"]
    
    summarizer = GroupChatSummarizerAgent(summarizer_config)
    
    for chat_name in chats:
        messages = fetch_messages(chat_name, hours=24)
        summary = await summarizer.execute_action("summarize_chat", {
            "messages": messages,
            "chat_name": chat_name
        })
        
        # Send to user once daily
        send_notification(summary)
```

## Configuration Examples

### Vision Agent Config
```json
{
  "agent_id": "vision_main",
  "level": "execution",
  "capabilities": ["analyze_image", "inventory_scan", "extract_recipe"],
  "config": {
    "provider": "anthropic",
    "api_key": "sk-ant-...",
    "model": "claude-3-5-sonnet-20241022"
  }
}
```

### Household Inventory Config
```json
{
  "agent_id": "inventory_main",
  "level": "execution",
  "capabilities": ["add_items", "get_inventory", "update_quantity"],
  "config": {
    "db_path": "data/household_inventory.db"
  }
}
```

### Monitoring Config
```json
{
  "agent_id": "monitor_main",
  "level": "execution",
  "capabilities": ["add_price_monitor", "add_package_tracker"],
  "config": {
    "db_path": "data/monitoring.db",
    "default_check_interval": 6
  }
}
```

## Future Enhancements

- [ ] Vision: Photo QA for ambiguous items
- [ ] Inventory: Grocery list integration and deduplication
- [ ] Calendar: Smart time finding across calendars
- [ ] Monitoring: Web scraping and price comparison
- [ ] Booking: OAuth integrations for Resy, OpenTable, Airbnb
- [ ] Chat Summary: LLM-powered topic extraction
- [ ] Cross-agent workflows: Auto-trigger booking based on monitoring
