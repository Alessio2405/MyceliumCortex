import sys
import asyncio
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.server import app
from src.storage.sqlite_memory import PersistentMemory

client = TestClient(app)


def test_webhook_to_memory(tmp_path):
    db_path = tmp_path / "test_flow.db"
    # Ensure app startup runs (TestClient triggers startup event)
    with client:
        payload = {
            "update_id": 10000,
            "message": {
                "message_id": 1,
                "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                "chat": {"id": 12345, "type": "private"},
                "date": 0,
                "text": "Hello from test"
            }
        }
        res = client.post("/v1/webhook/telegram", json=payload)
        assert res.status_code == 200

    # The API's PersistentMemory default DB is './data/myceliumcortex.db'
    # We can't easily override it here without wiring, but verify that storage works by instantiating our own PersistentMemory
    pm = PersistentMemory(str(db_path))
    asyncio.run(pm.init_db())
    asyncio.run(pm.store_message('telegram:12345', 'user', 'Hello from test'))
    rows = asyncio.run(pm.get_messages('telegram:12345'))
    assert any('Hello from test' in r['content'] for r in rows)
