"""Optional Redis-backed message bus implementation using aioredis.

This provides a drop-in replacement for the in-memory bus for multi-process
deployments. It's optional and used only if `aioredis` is available and the
project chooses to set it as the global bus via `set_global_bus`.
"""
import asyncio
from typing import AsyncIterator, Any

try:
    import aioredis
except Exception:
    aioredis = None


class RedisMessageBus:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        if aioredis is None:
            raise RuntimeError("aioredis not installed")
        self._redis_url = redis_url
        self._pub = None

    async def _get_pub(self):
        if self._pub is None:
            self._pub = aioredis.from_url(self._redis_url, decode_responses=True)
        return self._pub

    async def publish(self, topic: str, message: Any):
        pub = await self._get_pub()
        await pub.publish(topic, str(message))

    async def subscribe(self, topic: str) -> AsyncIterator[Any]:
        sub = aioredis.from_url(self._redis_url, decode_responses=True)
        pubsub = sub.pubsub()
        await pubsub.subscribe(topic)

        try:
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg is None:
                    # yield control and wait
                    await asyncio.sleep(0.1)
                    continue
                # msg has fields: type, channel, data
                yield msg.get("data")
        finally:
            await pubsub.unsubscribe(topic)
            await pubsub.close()
