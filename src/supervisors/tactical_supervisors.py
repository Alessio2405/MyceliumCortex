"""Tactical layer supervisors."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.agent import TacticalSupervisor
from ..core.types import AgentConfig, AgentLevel, AgentMessage
from ..agents.execution_agents import (
    LLMAgent, MemoryAgent, ToolAgent, PersonaAgent,
    WhatsAppAgent, TelegramAgent, GmailAgent, SlackAgent, DiscordAgent
)


logger = logging.getLogger(__name__)


class ConversationSupervisor(TacticalSupervisor):
    """Manages conversation flow, context, memory, and LLM interaction."""

    async def on_directive(self, message: AgentMessage):
        """Handle directives from parent."""
        action = message.action
        
        if action == "handle_turn":
            await self._handle_conversation_turn(message.payload)
        else:
            logger.warning(f"Unknown directive for ConversationSupervisor: {action}")

    async def _handle_conversation_turn(self, payload: Dict[str, Any]):
        """Handle a user message and generate response."""
        user_message = payload.get("message")
        conversation_id = payload.get("conversation_id", "default")
        user_id = payload.get("user_id")
        channel = payload.get("channel")
        
        if not user_message:
            logger.error("No message provided")
            return

        # Quick commands: allow direct shell execution from chat (e.g., /run ls -la)
        if isinstance(user_message, str) and user_message.startswith(("/run ", "/exec ", "/shell ")):
            cmd = user_message.split(' ', 1)[1] if ' ' in user_message else ''
            logger.info(f"Received shell command from {user_id}: {cmd}")

            # Security: validate command before execution
            from src.api.server import is_command_safe
            if not is_command_safe(cmd):
                logger.warning(f"Blocked unsafe command from {user_id}: {cmd}")
                error_msg = "Command blocked (unsafe or not whitelisted)"
                
                # Store error in memory
                if memory_agent:
                    await memory_agent.send_message(AgentMessage(
                        sender_id=self.agent_id,
                        action="store",
                        payload={
                            "conversation_id": conversation_id,
                            "message": {"role": "assistant", "content": error_msg}
                        }
                    ))
                
                # Reply via channel
                try:
                    from src.supervisors.strategic import ControlCenter
                    cc = getattr(ControlCenter, "instance", None)
                    if cc:
                        channel_sup = cc.supervisors.get("channel-supervisor")
                        if channel_sup and channel and user_id:
                            await channel_sup.send_message(AgentMessage(
                                sender_id=self.agent_id,
                                action="send_message",
                                payload={
                                    "channel": channel,
                                    "recipient": user_id,
                                    "message": error_msg
                                }
                            ))
                except Exception:
                    logger.exception("Failed to send error message via channel supervisor")
                
                return

            try:
                # Locate tool supervisor and tool agent
                from src.supervisors.strategic import ControlCenter
                cc = getattr(ControlCenter, "instance", None)
                tool_result = None
                if cc:
                    tool_sup = cc.supervisors.get("tool-supervisor")
                    if tool_sup:
                        # Ensure a tool agent exists
                        if "tool-agent" not in tool_sup.children:
                            await tool_sup.spawn_agents()
                        tool_agent = tool_sup.children.get("tool-agent")
                        if tool_agent:
                            # Execute shell command synchronously via execute_action
                            try:
                                res = await tool_agent.execute_action("execute", {
                                    "tool_name": "shell",
                                    "action": "run",
                                    "parameters": {"command": cmd}
                                })
                                tool_result = res
                            except Exception:
                                logger.exception("Tool execution failed")

                # Store command and result in memory
                if memory_agent:
                    await memory_agent.send_message(AgentMessage(
                        sender_id=self.agent_id,
                        action="store",
                        payload={
                            "conversation_id": conversation_id,
                            "message": {"role": "user", "content": user_message}
                        }
                    ))

                    await memory_agent.send_message(AgentMessage(
                        sender_id=self.agent_id,
                        action="store",
                        payload={
                            "conversation_id": conversation_id,
                            "message": {"role": "assistant", "content": str(tool_result)}
                        }
                    ))

                # Reply back via channel supervisor
                try:
                    if cc:
                        channel_sup = cc.supervisors.get("channel-supervisor")
                        if channel_sup and channel and user_id:
                            reply_text = str(tool_result)
                            await channel_sup.send_message(AgentMessage(
                                sender_id=self.agent_id,
                                action="send_message",
                                payload={
                                    "channel": channel,
                                    "recipient": user_id,
                                    "message": reply_text
                                }
                            ))
                except Exception:
                    logger.exception("Failed to send tool result via channel supervisor")

            except Exception:
                logger.exception("Error handling shell command")

            return

        logger.info(f"Handling turn for conversation {conversation_id}")

        # Step 1: Retrieve conversation history from memory agent
        memory_agent = self.children.get("memory-agent")
        if memory_agent:
            await memory_agent.send_message(AgentMessage(
                sender_id=self.agent_id,
                action="retrieve",
                payload={"conversation_id": conversation_id, "limit": 10}
            ))
            # In real implementation, wait for response
            # For now, we'll simulate getting the history

        # Step 2: Store user message in memory
        if memory_agent:
            await memory_agent.send_message(AgentMessage(
                sender_id=self.agent_id,
                action="store",
                payload={
                    "conversation_id": conversation_id,
                    "message": {"role": "user", "content": user_message}
                }
            ))

        # Step 3: Get persona system prompt
        persona_agent = self.children.get("persona-agent")
        system_prompt = "You are a helpful AI assistant."
        
        # Step 4: Call LLM agent
        llm_agent = self.children.get("llm-agent")
        response_text = None
        if llm_agent:
            # Build messages for LLM
            messages = [
                {"role": "user", "content": user_message}
            ]

            try:
                # Call execute_action directly to get the response synchronously from this coroutine
                result = await llm_agent.execute_action("generate", {
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.7
                })
                response_text = result.get("response")
            except Exception:
                logger.exception("LLM generation failed")

        # If we have a response, store it and send back via channel supervisor
        if response_text:
            # Store assistant response in memory
            if memory_agent:
                await memory_agent.send_message(AgentMessage(
                    sender_id=self.agent_id,
                    action="store",
                    payload={
                        "conversation_id": conversation_id,
                        "message": {"role": "assistant", "content": response_text}
                    }
                ))

            # Send response back via ChannelSupervisor if channel/user information present
            try:
                from src.supervisors.strategic import ControlCenter
                cc = getattr(ControlCenter, "instance", None)
                if cc:
                    channel_supervisor = cc.supervisors.get("channel-supervisor")
                    if channel_supervisor and channel and user_id:
                        await channel_supervisor.send_message(AgentMessage(
                            sender_id=self.agent_id,
                            action="send_message",
                            payload={
                                "channel": channel,
                                "recipient": user_id,
                                "message": response_text
                            }
                        ))
            except Exception:
                logger.exception("Failed to send reply via channel supervisor")

        logger.info(f"Conversation turn completed for {conversation_id}")

    async def spawn_agents(self, llm_config: Dict[str, Any]):
        """Spawn child agents."""
        
        # Spawn LLM agent
        llm_agent_config = AgentConfig(
            agent_id="llm-agent",
            level=AgentLevel.EXECUTION,
            capabilities=["generate", "embed"],
            config=llm_config
        )
        llm_agent = await self.spawn_child(llm_agent_config, LLMAgent)
        asyncio.create_task(llm_agent.start())

        # Spawn Memory agent
        memory_agent_config = AgentConfig(
            agent_id="memory-agent",
            level=AgentLevel.EXECUTION,
            capabilities=["store", "retrieve", "clear"],
            config={}
        )
        memory_agent = await self.spawn_child(memory_agent_config, MemoryAgent)
        asyncio.create_task(memory_agent.start())

        # Spawn Persona agent
        persona_agent_config = AgentConfig(
            agent_id="persona-agent",
            level=AgentLevel.EXECUTION,
            capabilities=["select", "get_system_prompt"],
            config={}
        )
        persona_agent = await self.spawn_child(persona_agent_config, PersonaAgent)
        asyncio.create_task(persona_agent.start())

        logger.info("ConversationSupervisor agents spawned")


class ToolSupervisor(TacticalSupervisor):
    """Manages tool execution agents."""

    async def on_directive(self, message: AgentMessage):
        """Handle directives from parent."""
        action = message.action
        
        if action == "execute_tool":
            await self._execute_tool(message.payload)
        else:
            logger.warning(f"Unknown directive for ToolSupervisor: {action}")

    async def _execute_tool(self, payload: Dict[str, Any]):
        """Execute a tool."""
        tool_name = payload.get("tool_name")
        tool_action = payload.get("action")
        parameters = payload.get("parameters", {})
        
        if not tool_name:
            logger.error("No tool_name provided")
            return

        # Get or spawn tool agent
        if tool_name not in self.children:
            await self._spawn_tool_agent(tool_name)

        tool_agent = self.children[tool_name]
        
        await tool_agent.send_message(AgentMessage(
            sender_id=self.agent_id,
            action="execute",
            payload={
                "tool_name": tool_name,
                "action": tool_action,
                "parameters": parameters
            }
        ))

    async def _spawn_tool_agent(self, tool_name: str):
        """Spawn a tool agent."""
        tool_config = AgentConfig(
            agent_id=tool_name,
            level=AgentLevel.EXECUTION,
            capabilities=["execute"],
            config={"tools": {tool_name: {}}}
        )
        
        tool_agent = await self.spawn_child(tool_config, ToolAgent)
        asyncio.create_task(tool_agent.start())
        logger.info(f"Spawned tool agent: {tool_name}")

    async def spawn_agents(self):
        """Spawn initial tool agents."""
        # Spawn a general purpose tool agent
        tool_config = AgentConfig(
            agent_id="tool-agent",
            level=AgentLevel.EXECUTION,
            capabilities=["execute"],
            config={"tools": {"shell": {}, "file": {}}}
        )
        
        tool_agent = await self.spawn_child(tool_config, ToolAgent)
        asyncio.create_task(tool_agent.start())
        
        logger.info("ToolSupervisor agents spawned")


class ChannelSupervisor(TacticalSupervisor):
    """Manages communication channel agents (WhatsApp, Telegram, Gmail, Slack, Discord, etc.)"""

    async def on_directive(self, message: AgentMessage):
        """Handle directives from parent."""
        action = message.action
        
        if action == "send_message":
            await self._send_message(message.payload)
        elif action == "send_media":
            await self._send_media(message.payload)
        elif action == "get_channel_status":
            await self._get_channel_status(message.payload)
        else:
            logger.warning(f"Unknown directive for ChannelSupervisor: {action}")

    async def _send_message(self, payload: Dict[str, Any]):
        """Send message through specified channel."""
        channel = payload.get("channel")  # whatsapp, telegram, gmail, slack, discord
        recipient = payload.get("recipient")
        message = payload.get("message")
        
        if not channel or not recipient or not message:
            logger.error("channel, recipient, and message required")
            return

        # Get or spawn channel agent
        if channel not in self.children:
            await self._spawn_channel_agent(channel)

        channel_agent = self.children[channel]
        
        await channel_agent.send_message(AgentMessage(
            sender_id=self.agent_id,
            action="send_message",
            payload={
                "recipient": recipient,
                "message": message
            }
        ))

    async def _send_media(self, payload: Dict[str, Any]):
        """Send media through specified channel."""
        channel = payload.get("channel")
        recipient = payload.get("recipient")
        media_type = payload.get("media_type")  # image, file, video, etc.
        media_path = payload.get("media_path")
        caption = payload.get("caption", "")
        
        if not all([channel, recipient, media_type, media_path]):
            logger.error("channel, recipient, media_type, and media_path required")
            return

        # Get or spawn channel agent
        if channel not in self.children:
            await self._spawn_channel_agent(channel)

        channel_agent = self.children[channel]
        
        await channel_agent.send_message(AgentMessage(
            sender_id=self.agent_id,
            action="send_media",
            payload={
                "recipient": recipient,
                "media_type": media_type,
                "media_path": media_path,
                "caption": caption
            }
        ))

    async def _get_channel_status(self, payload: Dict[str, Any]):
        """Get status of a channel."""
        channel = payload.get("channel")
        
        if not channel:
            logger.error("channel required")
            return

        if channel not in self.children:
            await self._spawn_channel_agent(channel)

        channel_agent = self.children[channel]
        
        await channel_agent.send_message(AgentMessage(
            sender_id=self.agent_id,
            action="get_status",
            payload={}
        ))

    async def _spawn_channel_agent(self, channel: str):
        """Spawn a channel agent."""
        channel_mapping = {
            "whatsapp": WhatsAppAgent,
            "telegram": TelegramAgent,
            "gmail": GmailAgent,
            "slack": SlackAgent,
            "discord": DiscordAgent,
        }
        
        if channel not in channel_mapping:
            logger.error(f"Unknown channel: {channel}")
            return

        agent_class = channel_mapping[channel]
        channel_config = AgentConfig(
            agent_id=f"{channel}-agent",
            level=AgentLevel.EXECUTION,
            capabilities=["send_message", "send_media", "get_status"],
            config={
                "api_key": "",  # Would be loaded from config
                "channel": channel
            }
        )
        
        channel_agent = await self.spawn_child(channel_config, agent_class)
        asyncio.create_task(channel_agent.start())
        # Ensure child is accessible by channel name (e.g., 'telegram')
        self.children[channel] = channel_agent
        # Remove the id-keyed entry to avoid duplicate keys
        self.children.pop(channel_config.agent_id, None)
        logger.info(f"Spawned channel agent: {channel}")

    async def spawn_agents(self):
        """Spawn initial channel agents."""
        channels = ["whatsapp", "telegram", "gmail", "slack", "discord"]
        
        for channel in channels:
            await self._spawn_channel_agent(channel)
        
        logger.info(f"ChannelSupervisor spawned {len(channels)} channel agents")
