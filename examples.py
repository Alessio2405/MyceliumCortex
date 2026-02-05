#!/usr/bin/env python3
"""
Example usage and testing script for MiniClaw.

This demonstrates:
1. Creating a MiniClaw instance
2. Sending messages
3. Accessing the agent hierarchy
4. Extending with custom agents
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.main import MiniClawAssistant
from src.core.types import AgentConfig, AgentLevel, UserMessage
from src.core.agent import ExecutionAgent
from typing import Any, Dict, Optional


class ExampleCustomAgent(ExecutionAgent):
    """Example custom agent for demonstration."""
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if action == "reverse_string":
            text = payload.get("text", "")
            return {"reversed": text[::-1]}
        elif action == "count_words":
            text = payload.get("text", "")
            return {"count": len(text.split())}
        else:
            raise ValueError(f"Unknown action: {action}")


async def example_basic_chat():
    """Example 1: Basic chat functionality."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Chat")
    print("="*60)
    
    # Initialize assistant
    assistant = MiniClawAssistant()
    await assistant.initialize()
    
    # Send a message
    response = await assistant.chat("Hello! What's your name?")
    print(f"\nUser: Hello! What's your name?")
    print(f"Assistant: {response}")
    
    # Cleanup
    await assistant.shutdown()


async def example_agent_hierarchy():
    """Example 2: Inspect agent hierarchy."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Agent Hierarchy")
    print("="*60)
    
    # Initialize assistant
    assistant = MiniClawAssistant()
    await assistant.initialize()
    
    # Access control center
    control_center = assistant.control_center
    print(f"\nControl Center: {control_center.agent_id}")
    print(f"Level: {control_center.level}")
    print(f"Status: {'Running' if control_center.is_running else 'Stopped'}")
    
    # List supervisors
    print(f"\nSupervisors ({len(control_center.supervisors)}):")
    for supervisor_id, supervisor in control_center.supervisors.items():
        print(f"  - {supervisor_id} ({supervisor.level})")
        print(f"    Children: {len(supervisor.children)}")
        for child_id, child in supervisor.children.items():
            print(f"      - {child_id} ({child.level})")
    
    # Cleanup
    await assistant.shutdown()


async def example_configuration():
    """Example 3: Work with configuration."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Configuration")
    print("="*60)
    
    from src.config import ConfigManager
    
    config = ConfigManager()
    print("\nLLM Provider:", config.get("llm.provider"))
    print("LLM Model:", config.get("llm.model"))
    print("Log Level:", config.get("system.log_level"))
    
    # Modify configuration
    print("\nModifying max_memory_per_conversation to 20...")
    config.set("system.max_memory_per_conversation", 20)
    config.save_config()
    
    print("New value:", config.get("system.max_memory_per_conversation"))


async def example_custom_agent():
    """Example 4: Create and register custom agent."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Agent")
    print("="*60)
    
    # Initialize assistant
    assistant = MiniClawAssistant()
    await assistant.initialize()
    
    # Create custom agent
    custom_config = AgentConfig(
        agent_id="example-custom-agent",
        level=AgentLevel.EXECUTION,
        capabilities=["reverse_string", "count_words"],
        config={}
    )
    
    custom_agent = ExampleCustomAgent(
        custom_config,
        parent_agent_id="tool-supervisor"
    )
    
    print(f"\nCreated custom agent: {custom_agent.agent_id}")
    print(f"Capabilities: {custom_agent.capabilities}")
    
    # Simulate sending a message to the agent
    from src.core.types import AgentMessage
    
    message = AgentMessage(
        sender_id="test",
        action="reverse_string",
        payload={"text": "Hello, World!"}
    )
    
    # In a real scenario, this would be async
    # For now, just demonstrate the structure
    print(f"\nSending message to agent...")
    print(f"  Action: {message.action}")
    print(f"  Payload: {message.payload}")
    
    # Cleanup
    await assistant.shutdown()


async def example_message_structure():
    """Example 5: Understand message structures."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Message Structures")
    print("="*60)
    
    from src.core.types import AgentMessage, AgentReport, UserMessage, ConversationContext
    
    # UserMessage
    user_msg = UserMessage(
        text="What is 2+2?",
        channel="terminal",
        user_id="user123",
        conversation_id="conv456"
    )
    print(f"\nUserMessage:")
    print(f"  text: {user_msg.text}")
    print(f"  channel: {user_msg.channel}")
    print(f"  user_id: {user_msg.user_id}")
    print(f"  conversation_id: {user_msg.conversation_id}")
    
    # AgentMessage
    agent_msg = AgentMessage(
        sender_id="conversation-supervisor",
        action="generate",
        payload={
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 1024
        }
    )
    print(f"\nAgentMessage:")
    print(f"  sender_id: {agent_msg.sender_id}")
    print(f"  action: {agent_msg.action}")
    print(f"  payload keys: {list(agent_msg.payload.keys())}")
    
    # AgentReport
    agent_report = AgentReport(
        agent_id="llm-agent",
        action="generate",
        status="success",
        data={
            "response": "4",
            "usage": {"input_tokens": 10, "output_tokens": 5}
        }
    )
    print(f"\nAgentReport:")
    print(f"  agent_id: {agent_report.agent_id}")
    print(f"  action: {agent_report.action}")
    print(f"  status: {agent_report.status}")
    print(f"  data keys: {list(agent_report.data.keys())}")
    
    # ConversationContext
    conv_context = ConversationContext(
        conversation_id="conv456",
        user_id="user123",
        channel="terminal",
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ]
    )
    print(f"\nConversationContext:")
    print(f"  conversation_id: {conv_context.conversation_id}")
    print(f"  user_id: {conv_context.user_id}")
    print(f"  channel: {conv_context.channel}")
    print(f"  message count: {len(conv_context.messages)}")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("MINICLAW EXAMPLES")
    print("="*60)
    
    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not set!")
        print("Set it with: export ANTHROPIC_API_KEY='sk-ant-...'")
        print("\nRunning examples that don't need API key...")
    
    try:
        # These don't need API key
        await example_configuration()
        await example_message_structure()
        await example_custom_agent()
        await example_agent_hierarchy()
        
        # This needs API key
        if api_key:
            await example_basic_chat()
        else:
            print("\n⏭️  Skipping Example 1 (requires ANTHROPIC_API_KEY)")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
