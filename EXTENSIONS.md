"""
Example: Creating a Custom Agent

This file demonstrates how to extend MiniClaw with custom agents.
"""

from src.core.agent import ExecutionAgent
from src.core.types import AgentConfig, AgentLevel
from typing import Any, Dict, Optional


class WeatherAgent(ExecutionAgent):
    """
    Example custom execution agent that provides weather information.
    
    In a real implementation, this would call a weather API like OpenWeatherMap.
    """

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        # Initialize weather API client
        # self.weather_client = WeatherAPI(config.config.get("api_key"))

    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weather-related actions."""
        
        if action == "get_weather":
            return await self._get_weather(payload)
        elif action == "get_forecast":
            return await self._get_forecast(payload)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _get_weather(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get current weather for a location."""
        location = payload.get("location")
        
        if not location:
            raise ValueError("location required")
        
        # In real implementation:
        # weather = await self.weather_client.get_current(location)
        # return {"temperature": 72, "condition": "Sunny", "location": location}
        
        # Mock response
        return {
            "temperature": 72,
            "condition": "Sunny",
            "location": location,
            "humidity": 65,
            "wind_speed": 5
        }

    async def _get_forecast(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast for a location."""
        location = payload.get("location")
        days = payload.get("days", 5)
        
        if not location:
            raise ValueError("location required")
        
        # Mock forecast
        return {
            "location": location,
            "forecast": [
                {"day": "Monday", "high": 75, "low": 60, "condition": "Sunny"},
                {"day": "Tuesday", "high": 73, "low": 59, "condition": "Cloudy"},
                {"day": "Wednesday", "high": 70, "low": 58, "condition": "Rainy"},
                {"day": "Thursday", "high": 72, "low": 60, "condition": "Sunny"},
                {"day": "Friday", "high": 76, "low": 62, "condition": "Sunny"},
            ][:days]
        }


# Example: Creating a Custom Supervisor

from src.core.agent import TacticalSupervisor
import asyncio


class WebSearchSupervisor(TacticalSupervisor):
    """
    Example custom tactical supervisor that manages web search operations.
    
    This would coordinate multiple search-related execution agents.
    """

    async def on_directive(self, message):
        """Handle directives from parent."""
        action = message.action
        
        if action == "search":
            await self._perform_search(message.payload)
        elif action == "research":
            await self._perform_research(message.payload)
        else:
            self.logger.warning(f"Unknown directive: {action}")

    async def _perform_search(self, payload: Dict[str, Any]):
        """Perform a web search."""
        query = payload.get("query")
        max_results = payload.get("max_results", 5)
        
        if not query:
            raise ValueError("query required")
        
        # This supervisor would:
        # 1. Delegate to a BraveSearchAgent to perform the search
        # 2. Wait for results
        # 3. Parse and structure results
        # 4. Return to parent supervisor

    async def _perform_research(self, payload: Dict[str, Any]):
        """Perform in-depth research on a topic."""
        topic = payload.get("topic")
        
        if not topic:
            raise ValueError("topic required")
        
        # This supervisor would:
        # 1. Break topic into research questions
        # 2. Delegate searches for each question to search agents
        # 3. Coordinate multiple searches in parallel
        # 4. Aggregate results
        # 5. Format research summary
        # 6. Return to parent supervisor


# Example: Using Custom Agents in Your Application

async def example_usage():
    """
    Example of how to use custom agents in MiniClaw.
    """
    
    from src.main import MiniClawAssistant
    from src.core.types import AgentConfig
    
    # Initialize MiniClaw
    assistant = MiniClawAssistant()
    await assistant.initialize()
    
    # Get the tool supervisor
    tool_supervisor = assistant.control_center.supervisors.get("tool-supervisor")
    
    if tool_supervisor:
        # Spawn your custom weather agent
        weather_agent_config = AgentConfig(
            agent_id="weather-agent",
            level=AgentLevel.EXECUTION,
            capabilities=["get_weather", "get_forecast"],
            config={
                "api_key": "your-weather-api-key"  # Set your API key here
            }
        )
        
        # Create and start the agent
        weather_agent = WeatherAgent(weather_agent_config, parent_agent_id="tool-supervisor")
        await tool_supervisor.spawn_child(weather_agent_config, WeatherAgent)
        asyncio.create_task(weather_agent.start())
        
        # Now the LLM can use the weather tool!
        # When LLM decides it needs weather info, it will be delegated
        # to the tool supervisor, which will route to your weather agent


# Extension Points in MiniClaw

"""
You can extend MiniClaw at several points:

1. **Custom Execution Agents**
   - Inherit from ExecutionAgent
   - Implement execute_action() for your specific capability
   - Examples: WeatherAgent, DatabaseAgent, APIAgent
   - Add to supervisors via spawn_child()

2. **Custom Supervisors**
   - Inherit from TacticalSupervisor
   - Implement on_directive() for orchestration logic
   - Spawn and manage child execution agents
   - Can be registered in ControlCenter

3. **Custom LLM Providers**
   - Modify LLMAgent to support additional LLM APIs
   - Add provider detection in __init__()
   - Implement provider-specific API calls

4. **Custom Memory Backends**
   - Replace in-memory dict with database
   - Extend MemoryAgent to support persistence
   - Add query capabilities for semantic search

5. **Custom Tools**
   - Add new action types to ToolAgent
   - Implement _execute_<tool_name>() methods
   - Sandbox execution as needed

6. **Message Bus Implementation**
   - Replace simple async.Queue with message broker
   - Add request/response correlation
   - Implement publish/subscribe for events
   - Enable true async/await responses

7. **Conversation Flows**
   - Create specialized supervisor for specific workflows
   - Implement multi-turn planning and execution
   - Add state machines for complex interactions

8. **Custom Communication Channels**
   - Inherit from ChannelAgent
   - Implement send_message() and send_media()
   - Register in ChannelSupervisor
   - Configure API credentials
   - Examples: Signal, Matrix, XMPP, IRC
"""


# Example: Creating a Custom Channel Agent

from src.agents import ChannelAgent
from datetime import datetime
import time


class SignalAgent(ChannelAgent):
    """
    Custom channel agent for Signal messenger.
    
    Signal is an end-to-end encrypted messaging app.
    This example shows how to add support for a new channel.
    """
    
    channel_name = "signal"
    
    def __init__(self, config, parent_agent_id=None):
        super().__init__(config, parent_agent_id)
        # Initialize Signal client
        # Requires signal-cli or official Signal API
        # self.client = SignalClient(config.config.get("api_key"))
        logger.info("SignalAgent initialized")
    
    async def _send_message(self, payload):
        """Send Signal message."""
        recipient = payload.get("recipient")
        message = payload.get("message")
        
        if not recipient or not message:
            raise ValueError("recipient and message required")
        
        # In real implementation:
        # response = await self.client.send_message(recipient, message)
        
        logger.info(f"Signal: Sending message to {recipient}")
        
        return {
            "status": "sent",
            "channel": "signal",
            "recipient": recipient,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "message_id": f"signal-{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _send_media(self, payload):
        """Send Signal media."""
        recipient = payload.get("recipient")
        media_type = payload.get("media_type")
        media_path = payload.get("media_path")
        caption = payload.get("caption", "")
        
        logger.info(f"Signal: Sending {media_type} to {recipient}")
        
        return {
            "status": "sent",
            "channel": "signal",
            "recipient": recipient,
            "media_type": media_type,
            "caption": caption,
            "message_id": f"signal-{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        }


# To use this custom channel:

# 1. Add to tactical_supervisors.py:
# from .custom_agents import SignalAgent
# 
# channel_mapping = {
#     "signal": SignalAgent,
#     # ... existing channels ...
# }

# 2. Add to config.json:
# {
#   "channels": {
#     "signal": {
#       "api_key": "your-signal-api-key",
#       "phone_number": "+1234567890"
#     }
#   }
# }

# 3. Use in code:
# await channel_supervisor.send_message({
#     "channel": "signal",
#     "recipient": "+1234567890",
#     "message": "Hello from MiniClaw!"
# })
