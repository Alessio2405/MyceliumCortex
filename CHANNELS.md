# Channel Agents Documentation

## Overview

Channel agents are execution layer agents that handle communication through various platforms like WhatsApp, Telegram, Gmail, Slack, and Discord. They are managed by the `ChannelSupervisor` tactical agent.

## Architecture

```
ControlCenter (Strategic)
    ↓
ChannelSupervisor (Tactical)
    ├── WhatsAppAgent (Execution)
    ├── TelegramAgent (Execution)
    ├── GmailAgent (Execution)
    ├── SlackAgent (Execution)
    └── DiscordAgent (Execution)
```

## Supported Channels

### WhatsApp

**Agent:** `WhatsAppAgent`

**Capabilities:**
- `send_message` - Send text messages
- `send_media` - Send images, videos, files
- `get_status` - Check connection status

**Usage Example:**
```python
await channel_supervisor.send_message({
    "channel": "whatsapp",
    "recipient": "+1234567890",
    "message": "Hello from MiniClaw!"
})
```

**Configuration:**
```json
{
  "channels": {
    "whatsapp": {
      "api_key": "your-whatsapp-business-api-key",
      "phone_number_id": "your-phone-number-id"
    }
  }
}
```

**API Integration:**
- Twilio WhatsApp API
- WhatsApp Business API
- whatsapp-web.js (for browser automation)

### Telegram

**Agent:** `TelegramAgent`

**Capabilities:**
- `send_message` - Send text messages with formatting (HTML/Markdown)
- `send_media` - Send photos, videos, documents
- `get_status` - Check bot connection status

**Usage Example:**
```python
await channel_supervisor.send_message({
    "channel": "telegram",
    "chat_id": "123456789",
    "message": "Hello from MiniClaw!",
    "parse_mode": "HTML"
})
```

**Configuration:**
```json
{
  "channels": {
    "telegram": {
      "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
      "webhook_url": "https://your-domain.com/webhook"
    }
  }
}
```

**API Integration:**
- python-telegram-bot
- Official Telegram Bot API

### Gmail

**Agent:** `GmailAgent`

**Capabilities:**
- `send_email` - Send emails with attachments
- `get_inbox` - Retrieve inbox messages
- `get_email` - Get specific email content

**Usage Example:**
```python
await channel_supervisor.send_message({
    "channel": "gmail",
    "recipient": "user@example.com",
    "subject": "Hello from MiniClaw",
    "body": "This is a test email"
})
```

**Configuration:**
```json
{
  "channels": {
    "gmail": {
      "email": "your-email@gmail.com",
      "credentials_file": "~/.gmail/credentials.json"
    }
  }
}
```

**API Integration:**
- Google Gmail API v1
- google-auth-oauthlib
- google-auth-httplib2

### Slack

**Agent:** `SlackAgent`

**Capabilities:**
- `send_message` - Send messages to channels or DMs
- `send_media` - Upload files and snippets
- `send_reaction` - Add emoji reactions
- `get_channel_info` - Get channel information

**Usage Example:**
```python
await channel_supervisor.send_message({
    "channel": "slack",
    "channel_id": "C1234567890",
    "message": "Hello from MiniClaw!"
})
```

**Configuration:**
```json
{
  "channels": {
    "slack": {
      "bot_token": "xoxb-your-token",
      "workspace_id": "T1234567890"
    }
  }
}
```

**API Integration:**
- slack-sdk
- Official Slack Web API

### Discord

**Agent:** `DiscordAgent`

**Capabilities:**
- `send_message` - Send messages to channels
- `send_media` - Upload files
- `add_role` - Add roles to members
- `get_server_info` - Get server information

**Usage Example:**
```python
await channel_supervisor.send_message({
    "channel": "discord",
    "channel_id": "1234567890",
    "message": "Hello from MiniClaw!"
})
```

**Configuration:**
```json
{
  "channels": {
    "discord": {
      "bot_token": "your-bot-token",
      "guild_id": "1234567890"
    }
  }
}
```

**API Integration:**
- discord.py
- Official Discord API

## Message Flow

### Sending a Message

```
User Request
    ↓
ControlCenter
    ↓
ChannelSupervisor.send_message()
    ├─ Check if channel agent exists
    ├─ Spawn if needed
    └─ Send AgentMessage
        ↓
    ChannelAgent.execute_action()
        ↓
    _send_message() / _send_media() / _get_status()
        ↓
    Report to ChannelSupervisor
        ↓
    Report to ControlCenter
        ↓
    Response returned
```

## Message Payloads

### send_message

```python
{
    "channel": "whatsapp",          # Required: channel name
    "recipient": "+1234567890",     # Required: recipient identifier
    "message": "Hello!",            # Required: message text
    "thread_ts": None,              # Optional: for threaded replies (Slack)
    "parse_mode": "HTML"            # Optional: formatting (Telegram)
}
```

### send_media

```python
{
    "channel": "telegram",          # Required: channel name
    "recipient": "123456789",       # Required: recipient identifier
    "media_type": "image",          # Required: image, video, file, etc.
    "media_path": "/path/to/file",  # Required: local file path
    "caption": "Image caption"       # Optional: caption/description
}
```

### get_channel_status

```python
{
    "channel": "slack"              # Required: channel name
}
```

## Response Format

All channel agents return responses in this format:

```python
{
    "status": "sent",               # sent, failed, pending
    "channel": "whatsapp",          # channel name
    "recipient": "+1234567890",     # recipient identifier
    "message_id": "msg_123",        # unique message identifier
    "timestamp": "2026-02-05T10:30:00",
    # ... channel-specific fields ...
}
```

## Creating Custom Channel Agents

### Step 1: Inherit from ChannelAgent

```python
from src.core.agent import ExecutionAgent
from src.core.types import AgentConfig, AgentLevel
from src.agents import ChannelAgent
from typing import Any, Dict, Optional

class SignalAgent(ChannelAgent):
    """Signal messenger integration."""
    
    channel_name = "signal"
    
    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        # Initialize Signal client
        logger.info("SignalAgent initialized")
    
    async def _send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send Signal message."""
        recipient = payload.get("recipient")
        message = payload.get("message")
        
        if not recipient or not message:
            raise ValueError("recipient and message required")
        
        # Implement Signal API call here
        logger.info(f"Signal: Sending message to {recipient}")
        
        return {
            "status": "sent",
            "channel": "signal",
            "recipient": recipient,
            "message_id": f"signal-{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        }
```

### Step 2: Register in ChannelSupervisor

Update `src/supervisors/tactical_supervisors.py`:

```python
async def _spawn_channel_agent(self, channel: str):
    """Spawn a channel agent."""
    channel_mapping = {
        "whatsapp": WhatsAppAgent,
        "telegram": TelegramAgent,
        "gmail": GmailAgent,
        "slack": SlackAgent,
        "discord": DiscordAgent,
        "signal": SignalAgent,  # Add your new channel
    }
    
    # ... rest of the method ...
```

### Step 3: Add Configuration

```json
{
  "channels": {
    "signal": {
      "phone_number": "+1234567890",
      "api_key": "your-signal-api-key"
    }
  }
}
```

## Configuration File

Add channel configurations to `~/.miniclaw/config.json`:

```json
{
  "channels": {
    "whatsapp": {
      "api_key": "your-key",
      "phone_number_id": "id"
    },
    "telegram": {
      "bot_token": "your-token"
    },
    "gmail": {
      "email": "your-email@gmail.com",
      "credentials_file": "~/.gmail/credentials.json"
    },
    "slack": {
      "bot_token": "xoxb-token",
      "workspace_id": "id"
    },
    "discord": {
      "bot_token": "token",
      "guild_id": "id"
    }
  }
}
```

## Error Handling

Each channel agent handles errors gracefully:

```python
{
    "status": "failed",
    "channel": "whatsapp",
    "error": "Invalid recipient format",
    "timestamp": "2026-02-05T10:30:00"
}
```

## Rate Limiting

Channels have different rate limits:
- WhatsApp: 80 messages/second (API limit)
- Telegram: No strict limit (1000s/second possible)
- Gmail: 50 emails/second per user
- Slack: 1 request/second (app rate limit)
- Discord: 50 messages/second per channel

The supervisor can implement rate limiting per channel in the future.

## Testing Channels

Run the examples:

```bash
python examples.py
```

Or test manually:

```python
import asyncio
from src.main import MiniClawAssistant

async def test_channels():
    assistant = MiniClawAssistant()
    await assistant.initialize()
    
    # Get channel supervisor
    channel_sup = assistant.control_center.supervisors.get("channel-supervisor")
    
    # Send test message
    await channel_sup.send_message({
        "channel": "telegram",
        "chat_id": "123456789",
        "message": "Test message"
    })

asyncio.run(test_channels())
```

## Future Enhancements

- [ ] WhatsApp webhook for receiving messages
- [ ] Telegram message handlers
- [ ] Gmail label management
- [ ] Slack scheduled messages
- [ ] Discord voice channel support
- [ ] Signal message encryption
- [ ] Matrix protocol support
- [ ] IRC support
- [ ] XMPP support
- [ ] SMS (Twilio)
