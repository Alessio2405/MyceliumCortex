"""Execution layer agents."""

import asyncio
import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime
import time

from ..core.agent import ExecutionAgent
from ..core.types import AgentConfig, AgentLevel, AgentMessage, AgentReport
from ..storage.sqlite_memory import PersistentMemory
import os
import httpx


logger = logging.getLogger(__name__)


class LLMAgent(ExecutionAgent):
    """LLM execution agent - calls LLM APIs."""

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        
        # Initialize LLM client
        provider = self.config.get("provider", "anthropic")
        api_key = self.config.get("api_key")
        
        if provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
                self.model = self.config.get("model", "claude-3-5-sonnet-20241022")
                logger.info(f"LLMAgent initialized with Anthropic: {self.model}")
            except ImportError:
                logger.error("anthropic package not found. Install with: pip install anthropic")
                self.client = None
        elif provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.model = self.config.get("model", "gpt-4-turbo")
                logger.info(f"LLMAgent initialized with OpenAI: {self.model}")
            except ImportError:
                logger.error("openai package not found. Install with: pip install openai")
                self.client = None
        else:
            logger.error(f"Unknown LLM provider: {provider}")
            self.client = None

    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LLM actions."""
        
        if not self.client:
            raise RuntimeError("LLM client not initialized. Check API key and provider.")

        if action == "generate":
            return await self._generate(payload)
        elif action == "embed":
            return await self._embed(payload)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text using LLM."""
        start_time = time.time()
        
        messages = payload.get("messages", [])
        max_tokens = payload.get("max_tokens", 1024)
        temperature = payload.get("temperature", 0.7)
        
        if not messages:
            raise ValueError("messages required for generate action")

        try:
            # Call Anthropic or OpenAI
            response = await asyncio.to_thread(
                self._call_llm,
                messages,
                max_tokens,
                temperature
            )
            
            execution_time = time.time() - start_time
            
            return {
                "response": response["text"],
                "usage": response.get("usage", {}),
                "execution_time": execution_time,
                "model": self.model,
            }
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    def _call_llm(self, messages: list, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Call LLM (blocking, wrapped in asyncio.to_thread)."""
        
        # Determine which client we're using
        if hasattr(self.client, 'messages'):
            # Anthropic
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            
            return {
                "text": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            }
        else:
            # OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            
            return {
                "text": response.choices[0].message.content,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                }
            }

    async def _embed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embeddings (if supported)."""
        # This would be for services like OpenAI's embedding API
        # For now, return placeholder
        raise NotImplementedError("Embedding not yet implemented")


class MemoryAgent(ExecutionAgent):
    """Memory agent - stores and retrieves conversation history."""

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        self.memory: Dict[str, list] = {}  # in-memory cache: conversation_id -> messages
        db_path = config.config.get("db_path", "./data/myceliumcortex.db")
        self._persistent = PersistentMemory(db_path)

    async def start(self):
        # initialize persistent storage before running
        try:
            await self._persistent.init_db()
        except Exception:
            logger.exception("Failed to init persistent memory DB")
        await super().start()

    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory actions."""
        if action == "store":
            return await self._store(payload)
        elif action == "retrieve":
            return await self._retrieve(payload)
        elif action == "clear":
            return await self._clear(payload)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _store(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Store a message in persistent memory and update in-memory cache."""
        conversation_id = payload.get("conversation_id")
        message = payload.get("message")  # {"role": "user"|"assistant", "content": "..."}

        if not conversation_id or not message:
            raise ValueError("conversation_id and message required")

        # Persist each message as role/content in DB
        role = message.get("role", "user")
        content = message.get("content")
        await self._persistent.store_message(conversation_id, role, content)

        # Update in-memory cache
        if conversation_id not in self.memory:
            self.memory[conversation_id] = []
        self.memory[conversation_id].append(message)

        return {
            "stored": True,
            "conversation_id": conversation_id,
            "message_count": len(self.memory[conversation_id])
        }

    async def _retrieve(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve messages from persistent storage (with optional limit)."""
        conversation_id = payload.get("conversation_id")
        limit = payload.get("limit", None)

        if not conversation_id:
            raise ValueError("conversation_id required")

        # Try in-memory cache first
        messages = self.memory.get(conversation_id, [])
        if messages:
            if limit:
                messages = messages[-limit:]
            return {"messages": messages, "count": len(messages)}

        # Fallback to persistent DB
        rows = await self._persistent.get_messages(conversation_id, limit=limit)
        # Convert DB rows to message dicts
        out_msgs = []
        for r in rows:
            out_msgs.append({"role": r.get("role", "user"), "content": r.get("content")})

        # Warm the in-memory cache
        if out_msgs:
            self.memory[conversation_id] = out_msgs.copy()

        return {"messages": out_msgs, "count": len(out_msgs)}

    async def _clear(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Clear memory for a conversation (both in-memory and persistent)."""
        conversation_id = payload.get("conversation_id")

        if not conversation_id:
            raise ValueError("conversation_id required")

        if conversation_id in self.memory:
            del self.memory[conversation_id]

        await self._persistent.clear_conversation(conversation_id)
        return {"cleared": True}


class ToolAgent(ExecutionAgent):
    """Tool agent - executes tools like shell commands, file operations, etc."""

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        self.available_tools = config.config.get("tools", {})

    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool actions."""
        
        if action == "execute":
            return await self._execute_tool(payload)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _execute_tool(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        tool_name = payload.get("tool_name")
        tool_action = payload.get("action")
        parameters = payload.get("parameters", {})
        
        if not tool_name:
            raise ValueError("tool_name required")

        if tool_name == "shell":
            return await self._execute_shell(tool_action, parameters)
        elif tool_name == "file":
            return await self._execute_file(tool_action, parameters)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _execute_shell(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell command."""
        import subprocess
        
        if action == "run":
            command = params.get("command")
            if not command:
                raise ValueError("command required")
            
            try:
                result = await asyncio.to_thread(
                    subprocess.run,
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=params.get("timeout", 30)
                )
                
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "Command timed out"
                }
        
        raise ValueError(f"Unknown shell action: {action}")

    async def _execute_file(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operations."""
        import os
        
        if action == "read":
            path = params.get("path")
            if not path:
                raise ValueError("path required")
            
            if not os.path.exists(path):
                return {"success": False, "error": f"File not found: {path}"}
            
            with open(path, 'r') as f:
                content = f.read()
            
            return {"success": True, "content": content}
        
        elif action == "write":
            path = params.get("path")
            content = params.get("content")
            
            if not path or content is None:
                raise ValueError("path and content required")
            
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w') as f:
                f.write(content)
            
            return {"success": True, "path": path}
        
        else:
            raise ValueError(f"Unknown file action: {action}")


class PersonaAgent(ExecutionAgent):
    """Persona agent - manages different conversation personas/styles."""

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        self.personas = config.config.get("personas", {
            "default": "You are a helpful AI assistant.",
            "expert": "You are an expert with deep knowledge. Be concise and technical.",
            "friendly": "You are a friendly, casual assistant. Use humor when appropriate.",
        })

    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute persona actions."""
        
        if action == "select":
            return self._select_persona(payload)
        elif action == "get_system_prompt":
            return self._get_system_prompt(payload)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _select_persona(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate persona based on context."""
        requested = payload.get("persona", "default")
        
        if requested in self.personas:
            return {
                "selected": requested,
                "system_prompt": self.personas[requested]
            }
        
        # Default to default persona
        return {
            "selected": "default",
            "system_prompt": self.personas["default"]
        }

    def _get_system_prompt(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get system prompt for a persona."""
        persona = payload.get("persona", "default")
        
        if persona not in self.personas:
            persona = "default"
        
        return {
            "persona": persona,
            "system_prompt": self.personas[persona]
        }


# ============================================================================
# CHANNEL AGENTS - Communication Channel Integrations
# ============================================================================

class ChannelAgent(ExecutionAgent):
    """Base class for communication channel agents."""
    
    channel_name: str = "generic"
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute channel actions."""
        
        if action == "send_message":
            return await self._send_message(payload)
        elif action == "send_media":
            return await self._send_media(payload)
        elif action == "get_status":
            return await self._get_status(payload)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a text message."""
        recipient = payload.get("recipient")
        message = payload.get("message")
        
        if not recipient or not message:
            raise ValueError("recipient and message required")
        
        # This would be overridden by subclasses
        logger.info(f"{self.channel_name}: Sending message to {recipient}")
        
        return {
            "status": "sent",
            "channel": self.channel_name,
            "recipient": recipient,
            "message_id": f"{self.channel_name}-{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _send_media(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send media (image, file, etc.)."""
        recipient = payload.get("recipient")
        media_type = payload.get("media_type")  # image, file, video, etc.
        media_path = payload.get("media_path")
        caption = payload.get("caption", "")
        
        if not recipient or not media_type or not media_path:
            raise ValueError("recipient, media_type, and media_path required")
        
        logger.info(f"{self.channel_name}: Sending {media_type} to {recipient}")
        
        return {
            "status": "sent",
            "channel": self.channel_name,
            "recipient": recipient,
            "media_type": media_type,
            "message_id": f"{self.channel_name}-{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get channel status."""
        return {
            "channel": self.channel_name,
            "status": "connected",
            "connected_accounts": payload.get("accounts", 0)
        }


class WhatsAppAgent(ChannelAgent):
    """WhatsApp communication agent."""
    
    channel_name = "whatsapp"
    
    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        # Initialize WhatsApp client (would use whatsapp-web.js or official API)
        # self.client = WhatsAppClient(config.config.get("api_key"))
        logger.info("WhatsAppAgent initialized")
    
    async def _send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send WhatsApp message."""
        recipient = payload.get("recipient")  # Phone number like +1234567890
        message = payload.get("message")
        
        if not recipient or not message:
            raise ValueError("recipient and message required")
        
        # Mock WhatsApp sending
        logger.info(f"WhatsApp: Sending message to {recipient}")
        
        return {
            "status": "sent",
            "channel": "whatsapp",
            "recipient": recipient,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "message_id": f"whatsapp-{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "is_whatsapp_business": True
        }
    
    async def _send_media(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send WhatsApp media."""
        recipient = payload.get("recipient")
        media_type = payload.get("media_type")
        media_path = payload.get("media_path")
        caption = payload.get("caption", "")
        
        logger.info(f"WhatsApp: Sending {media_type} to {recipient}")
        
        return {
            "status": "sent",
            "channel": "whatsapp",
            "recipient": recipient,
            "media_type": media_type,
            "caption": caption,
            "message_id": f"whatsapp-{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        }


class TelegramAgent(ChannelAgent):
    """Telegram communication agent."""
    
    channel_name = "telegram"
    
    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        # Use Bot API via HTTP for minimal dependency
        self.bot_token = config.config.get("bot_token") or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        logger.info("TelegramAgent initialized (token present=%s)", bool(self.bot_token))
    
    async def _send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send Telegram message."""
        chat_id = payload.get("chat_id") or payload.get("recipient")  # Or recipient
        message = payload.get("message")
        parse_mode = payload.get("parse_mode", "HTML")  # HTML or Markdown
        
        if not chat_id or not message:
            raise ValueError("chat_id and message required")
        
        logger.info(f"Telegram: Sending message to chat {chat_id}")

        if not self.api_base:
            # No token configured — simulate send
            return {
                "status": "mocked",
                "channel": "telegram",
                "chat_id": chat_id,
                "message": message[:100] + "..." if len(message) > 100 else message,
                "message_id": int(time.time()),
                "parse_mode": parse_mode,
                "timestamp": datetime.now().isoformat()
            }

        # Call Telegram sendMessage API
        url = f"{self.api_base}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": parse_mode}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=data)
                resp.raise_for_status()
                j = resp.json()
                if not j.get("ok"):
                    raise RuntimeError(f"Telegram API error: {j}")
                result = j.get("result", {})

                return {
                    "status": "sent",
                    "channel": "telegram",
                    "chat_id": chat_id,
                    "message": result.get("text", message)[:100] + "..." if len(result.get("text", message)) > 100 else result.get("text", message),
                    "message_id": result.get("message_id"),
                    "parse_mode": parse_mode,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.exception("Telegram send failed: %s", e)
            return {"status": "failed", "error": str(e)}
    
    async def _send_media(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send Telegram media."""
        chat_id = payload.get("chat_id")
        media_type = payload.get("media_type")
        media_path = payload.get("media_path")
        caption = payload.get("caption", "")
        
        logger.info(f"Telegram: Sending {media_type} to chat {chat_id}")
        
        return {
            "status": "sent",
            "channel": "telegram",
            "chat_id": chat_id,
            "media_type": media_type,
            "caption": caption,
            "message_id": int(time.time()),
            "timestamp": datetime.now().isoformat()
        }


class GmailAgent(ChannelAgent):
    """Gmail email communication agent."""
    
    channel_name = "gmail"
    
    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        # Initialize Gmail client (would use google-auth and gmail API)
        # self.service = build('gmail', 'v1', credentials=credentials)
        logger.info("GmailAgent initialized")
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Gmail-specific actions."""
        
        if action == "send_email":
            return await self._send_email(payload)
        elif action == "get_inbox":
            return await self._get_inbox(payload)
        elif action == "get_email":
            return await self._get_email(payload)
        else:
            return await super().execute_action(action, payload)
    
    async def _send_email(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email."""
        recipient = payload.get("recipient")
        subject = payload.get("subject")
        body = payload.get("body")
        cc = payload.get("cc", [])
        bcc = payload.get("bcc", [])
        attachments = payload.get("attachments", [])
        
        if not recipient or not subject or not body:
            raise ValueError("recipient, subject, and body required")
        
        logger.info(f"Gmail: Sending email to {recipient}")
        
        return {
            "status": "sent",
            "channel": "gmail",
            "recipient": recipient,
            "subject": subject,
            "body_preview": body[:100] + "..." if len(body) > 100 else body,
            "cc_count": len(cc),
            "bcc_count": len(bcc),
            "attachments_count": len(attachments),
            "message_id": f"gmail-{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_inbox(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get Gmail inbox."""
        limit = payload.get("limit", 10)
        
        logger.info(f"Gmail: Fetching {limit} emails from inbox")
        
        return {
            "status": "success",
            "channel": "gmail",
            "inbox_count": 0,  # Would fetch actual count
            "unread_count": 0,
            "emails": []
        }
    
    async def _get_email(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific email."""
        message_id = payload.get("message_id")
        
        if not message_id:
            raise ValueError("message_id required")
        
        return {
            "status": "success",
            "channel": "gmail",
            "message_id": message_id,
            "email": {}
        }


class SlackAgent(ChannelAgent):
    """Slack communication agent."""
    
    channel_name = "slack"
    
    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        # Initialize Slack client (would use slack-sdk)
        # self.client = WebClient(token=config.config.get("bot_token"))
        logger.info("SlackAgent initialized")
    
    async def _send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send Slack message to channel or DM."""
        channel = payload.get("channel")  # Can be channel name or user ID
        message = payload.get("message")
        thread_ts = payload.get("thread_ts")  # For replying in thread
        
        if not channel or not message:
            raise ValueError("channel and message required")
        
        logger.info(f"Slack: Sending message to {channel}")
        
        return {
            "status": "sent",
            "channel": "slack",
            "channel_id": channel,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "ts": f"{int(time.time())}.000000",
            "in_thread": bool(thread_ts),
            "timestamp": datetime.now().isoformat()
        }
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack-specific actions."""
        
        if action == "send_reaction":
            return await self._send_reaction(payload)
        elif action == "get_channel_info":
            return await self._get_channel_info(payload)
        else:
            return await super().execute_action(action, payload)
    
    async def _send_reaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add emoji reaction to a message."""
        channel = payload.get("channel")
        timestamp = payload.get("timestamp")
        emoji = payload.get("emoji")
        
        logger.info(f"Slack: Adding :{emoji}: reaction")
        
        return {
            "status": "success",
            "channel": "slack",
            "reaction": emoji,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_channel_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get Slack channel information."""
        channel = payload.get("channel")
        
        if not channel:
            raise ValueError("channel required")
        
        return {
            "status": "success",
            "channel": "slack",
            "channel_id": channel,
            "member_count": 0,
            "topic": "",
            "description": ""
        }


class DiscordAgent(ChannelAgent):
    """Discord communication agent."""
    
    channel_name = "discord"
    
    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        # Initialize Discord client (would use discord.py)
        # self.bot = commands.Bot(command_prefix='!', token=config.config.get("bot_token"))
        logger.info("DiscordAgent initialized")
    
    async def _send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send Discord message."""
        channel_id = payload.get("channel_id")
        message = payload.get("message")
        
        if not channel_id or not message:
            raise ValueError("channel_id and message required")
        
        logger.info(f"Discord: Sending message to channel {channel_id}")
        
        return {
            "status": "sent",
            "channel": "discord",
            "channel_id": channel_id,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "message_id": int(time.time()),
            "timestamp": datetime.now().isoformat()
        }
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Discord-specific actions."""
        
        if action == "add_role":
            return await self._add_role(payload)
        elif action == "get_server_info":
            return await self._get_server_info(payload)
        else:
            return await super().execute_action(action, payload)
    
    async def _add_role(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add role to a Discord member."""
        user_id = payload.get("user_id")
        role_id = payload.get("role_id")
        
        logger.info(f"Discord: Adding role {role_id} to user {user_id}")
        
        return {
            "status": "success",
            "channel": "discord",
            "user_id": user_id,
            "role_id": role_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_server_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get Discord server information."""
        server_id = payload.get("server_id")
        
        if not server_id:
            raise ValueError("server_id required")
        
        return {
            "status": "success",
            "channel": "discord",
            "server_id": server_id,
            "member_count": 0,
            "role_count": 0,
            "channel_count": 0
        }


class VisionAgent(ExecutionAgent):
    """Vision agent - analyzes images and extracts information."""

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        
        # Initialize vision client
        provider = self.config.get("provider", "anthropic")
        api_key = self.config.get("api_key")
        
        if provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
                self.model = self.config.get("model", "claude-3-5-sonnet-20241022")
                logger.info(f"VisionAgent initialized with Anthropic: {self.model}")
            except ImportError:
                logger.error("anthropic package not found")
                self.client = None
        else:
            logger.error(f"Unknown vision provider: {provider}")
            self.client = None
    
    async def on_message(self, message: AgentMessage):
        """Handle incoming messages."""
        logger.info(f"VisionAgent received message: {message.data.get('type')}")
    
    async def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze an image with vision capabilities."""
        import base64
        import os
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")
        
        # Determine image type
        ext = os.path.splitext(image_path)[1].lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        media_type = media_type_map.get(ext, "image/jpeg")
        
        if not self.client:
            return {"error": "Vision client not initialized"}
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            return {
                "status": "success",
                "image": image_path,
                "analysis": message.content[0].text,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {
                "status": "error",
                "image": image_path,
                "error": str(e)
            }
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute vision-specific actions."""
        
        if action == "analyze_image":
            image_path = payload.get("image_path")
            prompt = payload.get("prompt", "What is in this image?")
            return await self.analyze_image(image_path, prompt)
        elif action == "inventory_scan":
            return await self._scan_inventory(payload)
        elif action == "extract_recipe":
            return await self._extract_recipe(payload)
        else:
            return await super().execute_action(action, payload)
    
    async def _scan_inventory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scan images for household inventory."""
        image_paths = payload.get("image_paths", [])
        category = payload.get("category", "general")
        
        prompt = f"""Analyze this image of {category} items and extract an inventory list.
        
        For each item visible, provide:
        1. Item name
        2. Estimated quantity
        3. Condition/Status
        
        Format as JSON with keys: item, quantity, status"""
        
        results = []
        for img_path in image_paths:
            result = await self.analyze_image(img_path, prompt)
            results.append(result)
        
        return {
            "status": "success",
            "category": category,
            "items_scanned": len(image_paths),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _extract_recipe(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract recipe ingredients from an image."""
        image_path = payload.get("image_path")
        
        prompt = """Extract all ingredients from this recipe image.
        
        Provide as JSON with:
        {
            "recipe_name": "...",
            "ingredients": [
                {"name": "...", "amount": "...", "unit": "..."},
                ...
            ],
            "servings": "...",
            "instructions": "..."
        }"""
        
        return await self.analyze_image(image_path, prompt)


class HouseholdInventoryAgent(ExecutionAgent):
    """Household inventory management agent."""

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        self.memory = PersistentMemory(db_path=self.config.get("db_path", "inventory.db"))
        logger.info("HouseholdInventoryAgent initialized")
    
    async def on_message(self, message: AgentMessage):
        """Handle incoming messages."""
        logger.info(f"HouseholdInventoryAgent received message: {message.data}")
    
    async def add_items(self, items: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Add items to inventory."""
        added = []
        for item in items:
            item["added_at"] = datetime.now().isoformat()
            self.memory.store(
                key=f"inventory:{item['name']}",
                data=item
            )
            added.append(item["name"])
        
        logger.info(f"Added {len(added)} items to inventory: {added}")
        
        return {
            "status": "success",
            "items_added": len(added),
            "items": added,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_inventory(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get current inventory."""
        # Retrieve all inventory items (simplified - would query DB)
        inventory = self.memory.retrieve(key="inventory:*", batch=True) or []
        
        if category:
            inventory = [
                item for item in inventory
                if item.get("category") == category
            ]
        
        return {
            "status": "success",
            "category": category,
            "items": inventory,
            "count": len(inventory),
            "timestamp": datetime.now().isoformat()
        }
    
    async def update_quantity(self, item_name: str, quantity: float) -> Dict[str, Any]:
        """Update quantity of an item."""
        key = f"inventory:{item_name}"
        item = self.memory.retrieve(key=key)
        
        if not item:
            return {
                "status": "error",
                "message": f"Item not found: {item_name}"
            }
        
        item["quantity"] = quantity
        item["updated_at"] = datetime.now().isoformat()
        self.memory.store(key=key, data=item)
        
        return {
            "status": "success",
            "item": item_name,
            "quantity": quantity,
            "timestamp": datetime.now().isoformat()
        }
    
    async def remove_item(self, item_name: str) -> Dict[str, Any]:
        """Remove item from inventory."""
        key = f"inventory:{item_name}"
        self.memory.delete(key=key)
        
        return {
            "status": "success",
            "item_removed": item_name,
            "timestamp": datetime.now().isoformat()
        }
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute inventory-specific actions."""
        
        if action == "add_items":
            items = payload.get("items", [])
            return await self.add_items(items)
        elif action == "get_inventory":
            category = payload.get("category")
            return await self.get_inventory(category)
        elif action == "update_quantity":
            item_name = payload.get("item_name")
            quantity = payload.get("quantity")
            return await self.update_quantity(item_name, quantity)
        elif action == "remove_item":
            item_name = payload.get("item_name")
            return await self.remove_item(item_name)
        else:
            return await super().execute_action(action, payload)
