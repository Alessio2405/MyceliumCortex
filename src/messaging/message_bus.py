import asyncio
from typing import Dict, Any, AsyncIterator, Callable


class InMemoryMessageBus:
    """A simple topic-based in-memory pub/sub message bus using asyncio queues.

    - `publish(topic, message)` publishes a message to a topic.
    - `subscribe(topic)` returns an async iterator yielding messages for that topic.

    This is intended for local/single-process use. Swap in Redis/Redis Streams or
    a message broker (RabbitMQ/Kafka) for distributed deployments.
    """

    def __init__(self):
        self._topics: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def _get_queue(self, topic: str) -> asyncio.Queue:
        async with self._lock:
            q = self._topics.get(topic)
            if q is None:
                q = asyncio.Queue()
                self._topics[topic] = q
            return q

    async def publish(self, topic: str, message: Any):
        q = await self._get_queue(topic)
        await q.put(message)

    async def subscribe(self, topic: str) -> AsyncIterator[Any]:
        q = await self._get_queue(topic)

        while True:
            msg = await q.get()
            yield msg


# Global singleton bus instance for simple projects.
bus = InMemoryMessageBus()


def set_global_bus(new_bus):
    """Replace the global bus implementation (e.g., with a Redis-backed bus)."""
    global bus
    bus = new_bus

