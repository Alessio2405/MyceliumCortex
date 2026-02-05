# Channel Implementation Guide

## Quick Start - Adding a New Channel

### 1. Create the Agent

In `src/agents/execution_agents.py`, inherit from `ChannelAgent`:

```python
class MyChannelAgent(ChannelAgent):
    """My custom channel integration."""
    
    channel_name = "mychannel"
    
    def __init__(self, config, parent_agent_id=None):
        super().__init__(config, parent_agent_id)
        # Initialize your API client
        logger.info("MyChannelAgent initialized")
    
    async def _send_message(self, payload):
        """Send a message."""
        recipient = payload.get("recipient")
        message = payload.get("message")
        
        if not recipient or not message:
            raise ValueError("recipient and message required")
        
        # Call your API
        result = await self.your_api_call(recipient, message)
        
        return {
            "status": "sent",
            "channel": "mychannel",
            "recipient": recipient,
            "message_id": result.id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _send_media(self, payload):
        """Send media."""
        # Similar implementation
        pass
```

### 2. Register the Agent

In `src/supervisors/tactical_supervisors.py`:

```python
# Add import
from ..agents import MyChannelAgent

# Update channel_mapping in ChannelSupervisor._spawn_channel_agent()
channel_mapping = {
    "whatsapp": WhatsAppAgent,
    "telegram": TelegramAgent,
    # ... other channels ...
    "mychannel": MyChannelAgent,  # Add your channel
}
```

### 3. Add Configuration

In `~/.miniclaw/config.json`:

```json
{
  "channels": {
    "mychannel": {
      "api_key": "your-api-key",
      "account_id": "your-account-id"
    }
  }
}
```

### 4. Use It

```python
await channel_supervisor.send_message({
    "channel": "mychannel",
    "recipient": "user@example.com",
    "message": "Hello!"
})
```

## Implementation Details

### ChannelAgent Base Class

All channel agents inherit from `ChannelAgent` which provides:

**Required:**
- `channel_name` - String identifying the channel type
- `__init__()` - Initialize API client

**To implement:**
- `_send_message()` - Send text message
- `_send_media()` - Send media (optional, inherited default OK)
- `_get_status()` - Check connection (optional)

**Automatically handled:**
- `send_message` - Routes to `_send_message()`
- `send_media` - Routes to `_send_media()`
- `get_status` - Routes to `_get_status()`

### Full Implementation Checklist

```python
class FullChannelExample(ChannelAgent):
    """Complete channel implementation."""
    
    channel_name = "example"
    
    # ✅ Set channel name
    def __init__(self, config, parent_agent_id=None):
        super().__init__(config, parent_agent_id)
        # ✅ Initialize API client
        # ✅ Load credentials from config
        # ✅ Log initialization
    
    # ✅ Implement required methods
    async def _send_message(self, payload):
        # Get recipient and message
        # Validate inputs
        # Call API
        # Return status + metadata
        pass
    
    # ✅ Implement optional methods
    async def _send_media(self, payload):
        # Get media details
        # Validate
        # Call API
        # Return status
        pass
    
    # ✅ Optional: Override for channel-specific actions
    async def execute_action(self, action, payload):
        if action == "my_custom_action":
            return await self._my_custom_action(payload)
        return await super().execute_action(action, payload)
    
    async def _my_custom_action(self, payload):
        # Implement custom action
        pass
```

## API Integration Examples

### Synchronous API

```python
import requests

async def _send_message(self, payload):
    recipient = payload.get("recipient")
    message = payload.get("message")
    
    # Use asyncio.to_thread for blocking I/O
    response = await asyncio.to_thread(
        requests.post,
        f"https://api.example.com/send",
        json={
            "to": recipient,
            "text": message,
            "auth": self.api_key
        }
    )
    
    data = response.json()
    
    return {
        "status": "sent" if response.status_code == 200 else "failed",
        "channel": self.channel_name,
        "recipient": recipient,
        "message_id": data.get("id"),
        "timestamp": datetime.now().isoformat()
    }
```

### Asynchronous API

```python
import aiohttp

async def _send_message(self, payload):
    recipient = payload.get("recipient")
    message = payload.get("message")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.example.com/send",
            json={
                "to": recipient,
                "text": message
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        ) as resp:
            data = await resp.json()
            
            return {
                "status": "sent" if resp.status == 200 else "failed",
                "channel": self.channel_name,
                "recipient": recipient,
                "message_id": data.get("id"),
                "timestamp": datetime.now().isoformat()
            }
```

### SDK-based API

```python
import telegram
from telegram.error import TelegramError

async def _send_message(self, payload):
    chat_id = payload.get("recipient")
    message = payload.get("message")
    
    try:
        msg = await self.bot.send_message(
            chat_id=chat_id,
            text=message
        )
        
        return {
            "status": "sent",
            "channel": "telegram",
            "recipient": chat_id,
            "message_id": msg.message_id,
            "timestamp": datetime.now().isoformat()
        }
    
    except TelegramError as e:
        return {
            "status": "failed",
            "channel": "telegram",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

## Common Patterns

### Error Handling

```python
async def _send_message(self, payload):
    try:
        # Validate inputs
        recipient = payload.get("recipient")
        if not recipient:
            raise ValueError("recipient required")
        
        message = payload.get("message")
        if not message:
            raise ValueError("message required")
        
        # Call API
        result = await self.api_client.send(recipient, message)
        
        # Return success
        return {
            "status": "sent",
            "channel": self.channel_name,
            "recipient": recipient,
            "message_id": result.id,
            "timestamp": datetime.now().isoformat()
        }
    
    except ValueError as e:
        # Input validation error
        logger.error(f"{self.channel_name}: {e}")
        raise
    
    except ConnectionError as e:
        # Network error - might be temporary
        logger.error(f"{self.channel_name}: Connection failed - {e}")
        return {
            "status": "failed",
            "error": "Connection failed",
            "retryable": True
        }
    
    except Exception as e:
        # Unexpected error
        logger.error(f"{self.channel_name}: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "retryable": False
        }
```

### Rate Limiting

```python
import asyncio
from datetime import datetime, timedelta

class RateLimitedChannelAgent(ChannelAgent):
    """Channel agent with built-in rate limiting."""
    
    def __init__(self, config, parent_agent_id=None):
        super().__init__(config, parent_agent_id)
        self.rate_limit = config.config.get("rate_limit", 10)  # msgs/second
        self.last_request = None
        self.min_interval = 1.0 / self.rate_limit
    
    async def _send_message(self, payload):
        # Rate limit
        if self.last_request:
            elapsed = (datetime.now() - self.last_request).total_seconds()
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
        
        self.last_request = datetime.now()
        
        # Send message...
        return {...}
```

### Retries with Exponential Backoff

```python
import asyncio

async def _send_with_retry(self, payload, max_retries=3):
    """Send message with exponential backoff retry."""
    
    for attempt in range(max_retries):
        try:
            result = await self._send_message_impl(payload)
            
            if result.get("status") == "sent":
                return result
            
            # Retryable error
            if not result.get("retryable", False):
                return result
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise
    
    return {"status": "failed", "error": "Max retries exceeded"}
```

## Testing Your Channel

```python
import asyncio
from src.main import MiniClawAssistant

async def test_my_channel():
    """Test your custom channel implementation."""
    
    # Initialize
    assistant = MiniClawAssistant()
    await assistant.initialize()
    
    # Get channel supervisor
    channel_sup = assistant.control_center.supervisors.get("channel-supervisor")
    
    # Send message
    message = {
        "channel": "mychannel",
        "recipient": "test@example.com",
        "message": "Test message"
    }
    
    await channel_sup.send_message(message)
    
    # Send media
    media = {
        "channel": "mychannel",
        "recipient": "test@example.com",
        "media_type": "image",
        "media_path": "/path/to/image.png",
        "caption": "Test image"
    }
    
    await channel_sup.send_media(media)
    
    # Shutdown
    await assistant.shutdown()

# Run test
asyncio.run(test_my_channel())
```

## Best Practices

1. **Input Validation**
   - Always validate required fields
   - Provide helpful error messages

2. **Error Handling**
   - Catch specific exceptions
   - Log errors with context
   - Return meaningful error responses

3. **Rate Limiting**
   - Be aware of API rate limits
   - Implement backoff strategies
   - Document limits in your agent

4. **Async/Await**
   - Use `asyncio.to_thread()` for blocking I/O
   - Never block the event loop
   - Use async context managers

5. **Logging**
   - Log important events (sent, failed, etc.)
   - Include relevant context (recipient, message ID)
   - Use appropriate log levels

6. **Documentation**
   - Document required config fields
   - Explain any API-specific behavior
   - Provide usage examples

7. **Testing**
   - Test with real API when possible
   - Have fallback for testing without API
   - Test error cases

## Troubleshooting

### "Agent not spawning"
- Check `channel_mapping` includes your agent
- Check spelling of channel name
- Check agent class is imported

### "Messages not being sent"
- Check API key in config
- Check API endpoint is correct
- Check error logs for API errors
- Test API directly with curl

### "Rate limiting issues"
- Check API rate limit documentation
- Implement rate limiting in agent
- Add exponential backoff retry

### "Memory/performance issues"
- Don't load entire message history
- Clean up old messages periodically
- Use pagination for large requests

## Next Steps

1. Create your custom channel agent
2. Add to ChannelSupervisor
3. Configure API credentials
4. Test with examples.py
5. Integrate with your workflow

See [CHANNELS.md](CHANNELS.md) for detailed channel documentation.
