import asyncio
import logging
from typing import Any, Dict

from ..messaging.message_bus import bus

logger = logging.getLogger("myceliumcortex.aux_agents")


class MessageRouterAgent:
    """Subscribes to the internal bus and routes messages to the ControlCenter or supervisors.

    This agent demonstrates how to hook the bus to the higher-level orchestration layer.
    """

    def __init__(self):
        self._task = None

    async def start(self):
        if self._task:
            return
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        async for msg in bus.subscribe("incoming.message"):
            try:
                await self.handle_incoming(msg)
            except Exception:
                logger.exception("Failed to route message: %s", msg)

    async def handle_incoming(self, payload: Dict[str, Any]):
        # Normalize and route to ControlCenter if available
        try:
            from src.supervisors.strategic import ControlCenter
            cc = getattr(ControlCenter, "instance", None)
            if cc is None:
                cc = ControlCenter()
            if hasattr(cc, "process_user_message"):
                await cc.process_user_message(payload)
                return
        except Exception:
            logger.debug("ControlCenter unavailable; message dropped or logged.")

        # Fallback: log the message
        logger.info("Incoming message (no router): %s", payload)


class WebhookReceiverAgent:
    """Optional agent that listens on other bus topics to perform transformations.

    Not strictly necessary with FastAPI handlers, but provided as an example.
    """

    def __init__(self):
        self._task = None

    async def start(self):
        if self._task:
            return
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        async for msg in bus.subscribe("webhook.raw"):
            try:
                # Normalize raw webhook into incoming.message topic
                normalized = self._normalize(msg)
                if normalized:
                    await bus.publish("incoming.message", normalized)
            except Exception:
                logger.exception("Failed to process raw webhook: %s", msg)

    def _normalize(self, raw: Dict[str, Any]):
        # Basic example - pass through
        return raw
