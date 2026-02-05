from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, status
from pydantic import BaseModel
import asyncio
import logging
from typing import Optional, Dict, Any
import hmac
import hashlib

from src.storage.sqlite_memory import PersistentMemory
from src.messaging.message_bus import bus, set_global_bus
from src.messaging.redis_bus import RedisMessageBus
import os
from src.supervisors.strategic import ControlCenter
from src.core.types import AgentConfig, AgentLevel
from src.host.host_manager import HostManager

# Host manager (registry + runner)
host_manager: Optional[HostManager] = None

# Keep a reference to a running ControlCenter for routing and lifecycle
control_center = None

logger = logging.getLogger("myceliumcortex.api")
app = FastAPI(title="MyceliumCortex API")

# Security: Load whitelist and token for Telegram webhook verification
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_CHAT_IDS = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",") if os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS") else []
SHELL_COMMAND_WHITELIST = os.environ.get("SHELL_COMMAND_WHITELIST", "").split(",") if os.environ.get("SHELL_COMMAND_WHITELIST") else []
SHELL_COMMAND_BLACKLIST = os.environ.get("SHELL_COMMAND_BLACKLIST", "rm,del,format,dd").split(",")  # Default dangerous commands

def verify_telegram_webhook(request_body: str, telegram_signature: Optional[str]) -> bool:
    """Verify Telegram webhook signature using HMAC-SHA256.
    
    Telegram sends X-Telegram-Bot-Api-Secret-Hash header for webhook verification.
    """
    if not TELEGRAM_BOT_TOKEN or not telegram_signature:
        # No token = skip verification (for testing only)
        logger.warning("Telegram webhook signature verification skipped (no token set)")
        return True
    
    try:
        secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
        expected_hash = hmac.new(secret_key, request_body.encode(), hashlib.sha256).hexdigest()
        is_valid = hmac.compare_digest(expected_hash, telegram_signature)
        
        if not is_valid:
            logger.warning("Invalid Telegram webhook signature")
        return is_valid
    except Exception as e:
        logger.exception("Error verifying Telegram webhook: %s", e)
        return False

def is_chat_allowed(chat_id: str) -> bool:
    """Check if chat_id is in whitelist (if whitelist is set)."""
    if not TELEGRAM_ALLOWED_CHAT_IDS or TELEGRAM_ALLOWED_CHAT_IDS == ['']:
        # No whitelist = allow all
        return True
    return str(chat_id) in TELEGRAM_ALLOWED_CHAT_IDS

def is_command_safe(command: str) -> bool:
    """Check if shell command is in whitelist (if set) and not in blacklist."""
    cmd_lower = command.lower().split()[0] if command else ""
    
    # Check blacklist first (always enforced)
    for blocked in SHELL_COMMAND_BLACKLIST:
        if blocked.strip() and cmd_lower.startswith(blocked.strip()):
            return False
    
    # If whitelist exists, only allow whitelisted commands
    if SHELL_COMMAND_WHITELIST and SHELL_COMMAND_WHITELIST != ['']:
        for allowed in SHELL_COMMAND_WHITELIST:
            if allowed.strip() and cmd_lower.startswith(allowed.strip()):
                return True
        return False
    
    # No whitelist = allow (but not blacklisted)
    return True

# Initialize a persistent memory instance for the API to use
mem = PersistentMemory("./data/myceliumcortex.db")


class IncomingMessage(BaseModel):
    conversation_id: str
    channel: Optional[str]
    sender: Optional[str]
    message: str


async def process_message_background(payload: Dict[str, Any]):
    # Store message in persistent memory
    try:
        await mem.store_message(payload.get("conversation_id", "global"), payload.get("sender", "external"), payload.get("message", ""))
    except Exception as e:
        logger.exception("Failed to store incoming message: %s", e)

    # Publish the normalized payload to the internal message bus so agents/supervisors can subscribe.
    try:
        await bus.publish("incoming.message", payload)
    except Exception:
        logger.exception("Failed to publish message to bus")


@app.on_event("startup")
async def startup_event():
    await mem.init_db()
    # Initialize ControlCenter for the API process so MessageRouterAgent can route messages
    try:
        global control_center
        # Initialize host manager
        global host_manager
        host_manager = HostManager()
        logger.info("HostManager initialized: %s", host_manager.cfg_file)
        # Optionally switch to Redis-backed bus if requested via env
        use_redis = os.environ.get("USE_REDIS_BUS", "false").lower() in ("1", "true", "yes")
        if use_redis:
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            try:
                redis_bus = RedisMessageBus(redis_url)
                set_global_bus(redis_bus)
                logger.info("RedisMessageBus set as global bus")
            except Exception:
                logger.exception("Failed to initialize RedisMessageBus; falling back to in-memory bus")
        control_center_config = AgentConfig(
            agent_id="control-center",
            level=AgentLevel.STRATEGIC,
            capabilities=["process_message", "manage_resources"],
            config={}
        )
        control_center = ControlCenter(control_center_config, llm_config={})
        await control_center.initialize()
        asyncio.create_task(control_center.start())
        asyncio.create_task(control_center.health_check())
    except Exception as e:
        logger.exception("Failed to initialize ControlCenter in API startup: %s", e)

    # Expose host manager on app state for external use
    try:
        app.state.host_manager = host_manager
    except Exception:
        pass


@app.on_event("shutdown")
async def shutdown_event():
    # Graceful shutdown: stop the control center and its supervisors
    try:
        global control_center
        if control_center:
            await control_center.stop()
            logger.info("ControlCenter stopped during shutdown")
    except Exception:
        logger.exception("Error during ControlCenter shutdown")
    # stop host manager agents
    try:
        global host_manager
        if host_manager:
            await host_manager.stop_all()
            logger.info("HostManager stopped all agents during shutdown")
    except Exception:
        logger.exception("Error shutting down host manager")


@app.post("/v1/message")
async def receive_message(msg: IncomingMessage, background_tasks: BackgroundTasks):
    payload = msg.dict()
    asyncio.create_task(process_message_background(payload))
    return {"status": "accepted", "conversation_id": msg.conversation_id}


@app.get("/v1/status")
async def status():
    return {"status": "ok", "service": "MyceliumCortex API"}


@app.post("/v1/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # Security: Verify webhook signature
    request_body = await request.body()
    telegram_signature = request.headers.get("X-Telegram-Bot-Api-Secret-Hash")
    
    if not verify_telegram_webhook(request_body.decode(), telegram_signature):
        logger.warning("Rejected invalid Telegram webhook")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Telegram webhook payload structure: see Telegram docs
    text = None
    chat_id = None
    try:
        message = data.get("message") or data.get("edited_message")
        if message:
            text = message.get("text")
            chat = message.get("chat", {})
            chat_id = chat.get("id")
    except Exception:
        pass
    
    if not text or not chat_id:
        return {"status": "ok"}
    
    # Security: Check if chat_id is allowed
    if not is_chat_allowed(str(chat_id)):
        logger.warning("Rejected message from unauthorized chat_id: %s", chat_id)
        return {"status": "rejected", "reason": "unauthorized"}
    
    payload = {"conversation_id": f"telegram:{chat_id}", "channel": "telegram", "sender": str(chat_id), "message": text}
    asyncio.create_task(process_message_background(payload))
    return {"status": "ok"}


@app.post("/v1/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.form()
    # Twilio sends form-encoded webhook values like 'Body' and 'From'
    text = data.get("Body")
    sender = data.get("From")
    if text:
        payload = {"conversation_id": f"whatsapp:{sender}", "channel": "whatsapp", "sender": sender, "message": text}
        asyncio.create_task(process_message_background(payload))
    return {"status": "ok"}
