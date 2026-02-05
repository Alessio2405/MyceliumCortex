"""
Example workflows using autonomous smart agents in MyceliumCortex.
Demonstrates real-world use cases for the new smart agents.
"""

import asyncio
from datetime import datetime, timedelta
from src.agents import (
    VisionAgent,
    HouseholdInventoryAgent,
    CalendarPromiseAgent,
    MonitoringAgent,
    GroupChatSummarizerAgent,
    BookingWorkflowAgent,
)
from src.core.types import AgentConfig, AgentLevel
import os


# ============================================================================
# Example 1: Freezer Inventory Management with Vision
# ============================================================================

async def example_freezer_inventory():
    """
    Scenario: You're stocking up at Costco and want to track freezer contents.
    
    Steps:
    1. Take photos of items in freezer
    2. Vision agent analyzes and extracts inventory
    3. Inventory agent stores the data
    4. Automatically update grocery list
    """
    
    print("\n=== Example 1: Freezer Inventory Management ===\n")
    
    # Initialize agents
    vision_config = AgentConfig(
        agent_id="vision_1",
        level=AgentLevel.EXECUTION,
        capabilities=["analyze_image", "inventory_scan"],
        config={
            "provider": "anthropic",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": "claude-3-5-sonnet-20241022"
        }
    )
    vision_agent = VisionAgent(vision_config)
    
    inventory_config = AgentConfig(
        agent_id="inventory_1",
        level=AgentLevel.EXECUTION,
        capabilities=["add_items", "get_inventory"],
        config={"db_path": "data/freezer_inventory.db"}
    )
    inventory_agent = HouseholdInventoryAgent(inventory_config)
    
    # Example: Vision agent analyzes freezer photos
    print("📸 Vision Agent: Analyzing freezer photos...")
    analysis = await vision_agent.execute_action("inventory_scan", {
        "image_paths": ["freezer_photo_1.jpg", "freezer_photo_2.jpg"],
        "category": "frozen_foods"
    })
    
    print(f"✓ Analysis complete: {analysis['status']}")
    
    # Example: Add detected items to inventory
    print("\n📋 Inventory Agent: Adding items...")
    frozen_items = [
        {"name": "Dumplings (shrimp)", "category": "frozen_foods", "quantity": 5, "unit": "boxes"},
        {"name": "Edamame", "category": "frozen_foods", "quantity": 2, "unit": "bags"},
        {"name": "Ice cream (vanilla)", "category": "frozen_foods", "quantity": 1, "unit": "container"},
        {"name": "Vegetables (mixed)", "category": "frozen_foods", "quantity": 3, "unit": "bags"},
    ]
    
    result = await inventory_agent.execute_action("add_items", {
        "items": frozen_items
    })
    
    print(f"✓ Added {result['items_added']} items: {result['items']}")
    
    # Get inventory snapshot
    inventory = await inventory_agent.execute_action("get_inventory", {
        "category": "frozen_foods"
    })
    
    print(f"\n📊 Current Frozen Inventory: {inventory['count']} items")


# ============================================================================
# Example 2: Automatic Calendar Event from Promise
# ============================================================================

async def example_calendar_promise():
    """
    Scenario: During a text conversation, you say "let me review this tomorrow".
    
    Steps:
    1. Promise agent detects commitment
    2. Calendar event is automatically created
    3. You get reminded at appropriate time
    """
    
    print("\n=== Example 2: Automatic Calendar from Promise ===\n")
    
    promise_config = AgentConfig(
        agent_id="promise_1",
        level=AgentLevel.EXECUTION,
        capabilities=["detect_promise", "create_event", "get_upcoming"],
        config={"db_path": "data/promises.db"}
    )
    promise_agent = CalendarPromiseAgent(promise_config)
    
    # Example: Text containing a promise
    conversation_text = """
    Hey! I have the report you asked for. Let me review it tonight and 
    get back to you with feedback tomorrow afternoon. Sound good?
    """
    
    print("📱 Incoming text message:")
    print(f"  {conversation_text.strip()}\n")
    
    # Detect the promise
    print("🔍 Promise Agent: Detecting commitments...")
    promise = await promise_agent.execute_action("detect_promise", {
        "text": conversation_text
    })
    
    if promise and "error" not in str(promise):
        print(f"✓ Promise detected: '{promise['text'][:50]}...'")
        print(f"  Due date: {promise['due_date']}")
        
        # Create calendar event
        print("\n📅 Creating calendar event...")
        event = await promise_agent.execute_action("create_event", {
            "promise": promise
        })
        
        print(f"✓ Event created: {event['event']['title']}")
    
    # Get upcoming promises
    print("\n📅 Upcoming promises (next 7 days):")
    upcoming = await promise_agent.execute_action("get_upcoming", {
        "days": 7
    })
    
    print(f"✓ You have {upcoming['count']} upcoming promises")


# ============================================================================
# Example 3: Price and Package Monitoring
# ============================================================================

async def example_monitoring():
    """
    Scenario: You're looking for a new laptop and tracking flights.
    
    Steps:
    1. Add URLs to monitor for price changes
    2. Add package tracking numbers
    3. System checks periodically and alerts you
    """
    
    print("\n=== Example 3: Monitoring Prices & Packages ===\n")
    
    monitor_config = AgentConfig(
        agent_id="monitor_1",
        level=AgentLevel.EXECUTION,
        capabilities=["add_price_monitor", "add_package_tracker", "check_monitor"],
        config={"db_path": "data/monitoring.db"}
    )
    monitor_agent = MonitoringAgent(monitor_config)
    
    # Add price monitors
    print("💰 Adding price monitors...\n")
    
    products = [
        {"url": "https://www.amazon.com/MacBook-Pro-14-inch", "interval": 6},
        {"url": "https://www.flighty.com/flight/UA123", "interval": 3},
    ]
    
    for product in products:
        monitor = await monitor_agent.execute_action("add_price_monitor", {
            "url": product["url"],
            "check_interval_hours": product["interval"]
        })
        print(f"✓ Monitoring: {product['url'][:50]}...")
        print(f"  Check every {monitor['check_interval_hours']} hours\n")
    
    # Add package tracker
    print("📦 Adding package tracker...\n")
    
    package = await monitor_agent.execute_action("add_package_tracker", {
        "tracking_number": "1Z999AA10123456784",
        "carrier": "UPS"
    })
    
    print(f"✓ Tracking package: {package['tracking_number']}")
    print(f"  Carrier: {package['carrier']}\n")
    
    # Check monitor status
    print("🔍 Checking monitor status...\n")
    
    status = await monitor_agent.execute_action("check_monitor", {
        "monitor_id": monitor["monitor_id"]
    })
    
    print(f"✓ Status: {status['monitor_type'].upper()}")
    print(f"  Last checked: {status['last_checked']}\n")
    
    # View all monitors
    all_monitors = await monitor_agent.execute_action("get_all_monitors", {})
    
    print(f"📊 Total active monitors: {all_monitors['count']}")


# ============================================================================
# Example 4: Group Chat Summarization
# ============================================================================

async def example_group_chat_summary():
    """
    Scenario: You're in 3 high-volume group chats (100+ msgs/day).
    
    Steps:
    1. Agent automatically summarizes daily
    2. Shows key topics and discussions
    3. You stay informed without reading every message
    """
    
    print("\n=== Example 4: Group Chat Summarization ===\n")
    
    summarizer_config = AgentConfig(
        agent_id="summarizer_1",
        level=AgentLevel.EXECUTION,
        capabilities=["summarize_chat", "get_recent_summaries"],
        config={"db_path": "data/summaries.db"}
    )
    summarizer_agent = GroupChatSummarizerAgent(summarizer_config)
    
    # Simulate group chat messages
    messages = [
        {"text": "Did anyone see the meeting notes?", "timestamp": datetime.now().isoformat(), "sender": "alice"},
        {"text": "Yes, I uploaded them to the drive", "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(), "sender": "bob"},
        {"text": "Project deadline moved to next Friday", "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(), "sender": "manager"},
        {"text": "Oh, that's tight. We need to prioritize", "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(), "sender": "alice"},
        {"text": "Let's sync tomorrow morning", "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(), "sender": "bob"},
    ]
    
    print("📱 Received messages from group: 'team-projects'\n")
    print(f"  Total messages: {len(messages)}")
    
    # Summarize
    print("\n🤖 Chat Summarizer: Processing...")
    summary = await summarizer_agent.execute_action("summarize_chat", {
        "messages": messages,
        "chat_name": "team-projects"
    })
    
    print(f"\n✓ Summary complete")
    print(f"  Summary: {summary['summary']['summary']}")
    print(f"  Key participants: {len(messages)} messages")
    
    # Get recent summaries
    print("\n📊 Recent summaries (last 7 days):")
    recent = await summarizer_agent.execute_action("get_recent_summaries", {
        "chat_name": "team-projects",
        "days": 7
    })
    
    print(f"✓ {recent['count']} summaries available")


# ============================================================================
# Example 5: Complex Restaurant Booking Workflow
# ============================================================================

async def example_booking_workflow():
    """
    Scenario: You want to book dinner at a nice restaurant.
    
    Steps:
    1. Check your calendar availability
    2. Check restaurant availability
    3. Auto-match preferences
    4. Create reservation
    """
    
    print("\n=== Example 5: Restaurant Booking Workflow ===\n")
    
    booking_config = AgentConfig(
        agent_id="booking_1",
        level=AgentLevel.EXECUTION,
        capabilities=["book_restaurant", "check_availability"],
        config={"db_path": "data/bookings.db"}
    )
    booking_agent = BookingWorkflowAgent(booking_config)
    
    # Check availability
    print("🔍 Checking restaurant availability...\n")
    
    available = await booking_agent.execute_action("check_availability", {
        "service_type": "restaurant",
        "date_range": {
            "start": "2026-02-10",
            "end": "2026-02-15"
        }
    })
    
    print(f"✓ Found {len(available['available_slots'])} available slots:")
    for slot in available["available_slots"][:3]:
        print(f"  • {slot['date']} at {slot['time']}")
    
    # Book restaurant
    print("\n📅 Booking restaurant...\n")
    
    booking = await booking_agent.execute_action("book_restaurant", {
        "restaurant_name": "Chez Maurice",
        "date": "2026-02-12",
        "party_size": 4,
        "preferences": {
            "quiet": True,
            "window_seating": True,
            "no_children": True
        }
    })
    
    print(f"✓ Reservation confirmed!")
    print(f"  Restaurant: {booking['restaurant_name']}")
    print(f"  Date: {booking['date']}")
    print(f"  Party size: {booking['party_size']}")
    print(f"  Status: {booking['booking_type']}")


# ============================================================================
# Example 6: Recipe Extraction and Grocery List
# ============================================================================

async def example_recipe_extraction():
    """
    Scenario: You found a recipe you like and want to cook this weekend.
    
    Steps:
    1. Take photo of recipe
    2. Vision agent extracts ingredients
    3. Cross-reference with current inventory
    4. Add missing items to grocery list
    """
    
    print("\n=== Example 6: Recipe Extraction & Grocery Integration ===\n")
    
    vision_config = AgentConfig(
        agent_id="vision_2",
        level=AgentLevel.EXECUTION,
        capabilities=["extract_recipe"],
        config={
            "provider": "anthropic",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": "claude-3-5-sonnet-20241022"
        }
    )
    vision_agent = VisionAgent(vision_config)
    
    # Extract recipe
    print("📷 Extracting recipe from image...\n")
    
    recipe = await vision_agent.execute_action("extract_recipe", {
        "image_path": "recipe.jpg"
    })
    
    if recipe["status"] == "success":
        print(f"✓ Recipe extracted")
        print(f"  Image: {recipe['image']}")
        print(f"  Analysis: {recipe['analysis'][:200]}...")
    
    # In real app, would now:
    # 1. Parse extracted ingredients
    # 2. Check current inventory
    # 3. Add missing items to grocery list
    # 4. Dedup with existing items


# ============================================================================
# Main Demo Runner
# ============================================================================

async def main():
    """Run all examples."""
    
    print("=" * 70)
    print("MyceliumCortex - Autonomous Smart Agents Demo")
    print("=" * 70)
    
    # Run examples
    await example_freezer_inventory()
    await example_calendar_promise()
    await example_monitoring()
    await example_group_chat_summary()
    await example_booking_workflow()
    await example_recipe_extraction()
    
    print("\n" + "=" * 70)
    print("✓ All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
