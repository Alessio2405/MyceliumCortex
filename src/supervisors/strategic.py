"""Strategic layer coordinator."""

import asyncio
import logging
from typing import Any, Dict, Optional

from ..core.agent import StrategicCoordinator
from ..core.types import AgentConfig, AgentLevel, AgentMessage, UserMessage
from .tactical_supervisors import ConversationSupervisor, ToolSupervisor, ChannelSupervisor
from ..agents.aux_agents import MessageRouterAgent


logger = logging.getLogger(__name__)


class ControlCenter(StrategicCoordinator):
    """
    Strategic layer coordinator.
    Manages high-level system goals, resource allocation, and supervisor coordination.
    """

    def __init__(self, config: AgentConfig, llm_config: Dict[str, Any]):
        super().__init__(config)
        self.llm_config = llm_config
        self.active_conversations = {}
        # Expose singleton-like instance for router convenience
        ControlCenter.instance = self
        # Prepare message router (will be started during initialize)
        self._message_router: Optional[MessageRouterAgent] = MessageRouterAgent()

    async def initialize(self):
        """Initialize the control center with supervisors."""
        
        # Spawn Conversation Supervisor
        conv_supervisor_config = AgentConfig(
            agent_id="conversation-supervisor",
            level=AgentLevel.TACTICAL,
            capabilities=["handle_turn", "manage_context"],
            config={}
        )
        conv_supervisor = ConversationSupervisor(conv_supervisor_config, parent_agent_id=self.agent_id)
        await self.register_supervisor(conv_supervisor)
        asyncio.create_task(conv_supervisor.start())
        
        # Spawn child agents for conversation supervisor
        await conv_supervisor.spawn_agents(self.llm_config)

        # Spawn Tool Supervisor
        tool_supervisor_config = AgentConfig(
            agent_id="tool-supervisor",
            level=AgentLevel.TACTICAL,
            capabilities=["execute_tool"],
            config={}
        )
        tool_supervisor = ToolSupervisor(tool_supervisor_config, parent_agent_id=self.agent_id)
        await self.register_supervisor(tool_supervisor)
        asyncio.create_task(tool_supervisor.start())
        
        # Spawn child agents for tool supervisor
        await tool_supervisor.spawn_agents()

        # Spawn Channel Supervisor
        channel_supervisor_config = AgentConfig(
            agent_id="channel-supervisor",
            level=AgentLevel.TACTICAL,
            capabilities=["send_message", "send_media", "get_channel_status"],
            config={}
        )
        channel_supervisor = ChannelSupervisor(channel_supervisor_config, parent_agent_id=self.agent_id)
        await self.register_supervisor(channel_supervisor)
        asyncio.create_task(channel_supervisor.start())
        
        # Spawn child agents for channel supervisor
        await channel_supervisor.spawn_agents()

        logger.info("ControlCenter initialized")
        # Start the message router so it can route incoming bus messages to this ControlCenter
        try:
            asyncio.create_task(self._message_router.start())
            logger.info("MessageRouterAgent started")
        except Exception:
            logger.exception("Failed to start MessageRouterAgent")

    async def on_directive(self, message: AgentMessage):
        """Handle incoming directive."""
        action = message.action
        
        if action == "process_user_message":
            await self._process_user_message(message.payload)
        else:
            logger.warning(f"Unknown directive: {action}")

    async def process_user_message(self, user_message: Any) -> Optional[str]:
        """
        Process a user message and return AI response.
        This is the main entry point for conversation.
        """
        # Accept either a UserMessage dataclass or a normalized dict coming from the message bus
        if isinstance(user_message, dict):
            text = user_message.get("message") or user_message.get("text")
            user_id = user_message.get("user_id") or user_message.get("sender")
            channel = user_message.get("channel")
            conversation_id = user_message.get("conversation_id") or user_id or "default"
        else:
            text = getattr(user_message, "text", None)
            user_id = getattr(user_message, "user_id", None)
            channel = getattr(user_message, "channel", None)
            conversation_id = getattr(user_message, "conversation_id", None) or user_id or "default"

        logger.info(f"Processing message from {user_id}: {str(text)[:50]}...")

        # Delegate to conversation supervisor
        conv_supervisor = self.supervisors.get("conversation-supervisor")
        if not conv_supervisor:
            logger.error("Conversation supervisor not found")
            return "Error: Conversation supervisor not initialized"

        # Send directive to conversation supervisor
        message = AgentMessage(
            sender_id=self.agent_id,
            action="handle_turn",
            payload={
                "message": text,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "channel": channel
            }
        )
        
        await conv_supervisor.send_message(message)
        
        # In a real implementation, we would wait for response from supervisor
        # For now, return a placeholder
        # This would be handled via a proper message bus with callbacks
        return "Processing message... (response will be sent async)"

    async def _process_user_message(self, payload: Dict[str, Any]):
        """Process user message directive."""
        message_text = payload.get("message")
        conversation_id = payload.get("conversation_id", "default")
        
        if not message_text:
            logger.error("No message provided")
            return

        logger.info(f"Directive: Process message for conversation {conversation_id}")

    async def on_directive(self, message: AgentMessage):
        """Handle incoming directive."""
        pass  # Override for strategic logic

    async def health_check(self):
        """Periodic health check."""
        while self.is_running:
            await asyncio.sleep(60)  # Check every minute
            
            logger.info("Health check: All supervisors active")
            
            for supervisor_id, supervisor in self.supervisors.items():
                if not supervisor.is_running:
                    logger.warning(f"Supervisor {supervisor_id} not running!")
                else:
                    logger.debug(f"Supervisor {supervisor_id} OK ({len(supervisor.children)} children)")
