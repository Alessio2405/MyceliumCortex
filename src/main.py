"""Main entry point for the miniclaw AI assistant."""

import asyncio
import logging
import json
import os
from pathlib import Path
from typing import Optional

from .core.types import AgentConfig, AgentLevel, UserMessage
from .supervisors.strategic import ControlCenter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MiniClawAssistant:
    """Main AI assistant class."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the assistant."""
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.control_center: Optional[ControlCenter] = None

    def _get_default_config_path(self) -> str:
        """Get default config path."""
        home = Path.home()
        config_dir = home / ".miniclaw"
        config_file = config_dir / "config.json"
        
        if not config_file.exists():
            logger.warning(f"Config file not found at {config_file}. Using defaults.")
            return str(config_file)
        
        return str(config_file)

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                return self._get_default_config()
        
        return self._get_default_config()

    def _get_default_config(self) -> dict:
        """Get default configuration."""
        return {
            "llm": {
                "provider": "anthropic",
                "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
                "model": "claude-3-5-sonnet-20241022"
            },
            "system": {
                "log_level": "INFO"
            }
        }

    async def initialize(self):
        """Initialize the assistant."""
        logger.info("Initializing MiniClaw Assistant...")

        # Create control center
        control_center_config = AgentConfig(
            agent_id="control-center",
            level=AgentLevel.STRATEGIC,
            capabilities=["process_message", "manage_resources"],
            config={}
        )

        self.control_center = ControlCenter(control_center_config, self.config["llm"])
        await self.control_center.initialize()
        
        # Start control center
        asyncio.create_task(self.control_center.start())
        asyncio.create_task(self.control_center.health_check())
        
        logger.info("MiniClaw Assistant initialized")

    async def chat(self, message: str, user_id: str = "user", conversation_id: Optional[str] = None) -> str:
        """Send a message and get a response."""
        if not self.control_center:
            raise RuntimeError("Assistant not initialized. Call initialize() first.")

        user_message = UserMessage(
            text=message,
            channel="terminal",
            user_id=user_id,
            conversation_id=conversation_id
        )

        response = await self.control_center.process_user_message(user_message)
        return response or "No response"

    async def interactive_chat(self, user_id: str = "user"):
        """Start interactive chat session."""
        if not self.control_center:
            raise RuntimeError("Assistant not initialized. Call initialize() first.")

        conversation_id = f"{user_id}_{int(__import__('time').time())}"
        
        print("\n🤖 MiniClaw Assistant (type 'exit' to quit)")
        print("=" * 50)

        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Assistant: Goodbye!")
                    break
                
                if not user_input:
                    continue

                # For now, return a simple response
                # In production, this would wait for actual LLM response
                user_message = UserMessage(
                    text=user_input,
                    channel="terminal",
                    user_id=user_id,
                    conversation_id=conversation_id
                )

                response = await self.control_center.process_user_message(user_message)
                print(f"\nAssistant: {response}")

            except KeyboardInterrupt:
                print("\n\nAssistant: Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"Error: {e}")

    async def shutdown(self):
        """Shutdown the assistant."""
        if self.control_center:
            await self.control_center.stop()
        logger.info("MiniClaw Assistant shut down")


async def main():
    """Main entry point."""
    assistant = MiniClawAssistant()
    
    try:
        await assistant.initialize()
        await assistant.interactive_chat()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await assistant.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
