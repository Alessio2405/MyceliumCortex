import sys
import os
import time
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Patch LLMAgent before importing the app so ConversationSupervisor spawns the mock
import src.supervisors.tactical_supervisors as ts
from src.core.agent import ExecutionAgent
from src.core.types import AgentConfig

llm_calls = []

class MockLLMAgent(ExecutionAgent):
    def __init__(self, config: AgentConfig, parent_agent_id=None):
        super().__init__(config, parent_agent_id)

    async def execute_action(self, action: str, payload: dict):
        llm_calls.append((action, payload))
        # Return a mocked response
        return {"response": "mocked response", "action": action}

# Replace the real LLMAgent used by the supervisor
ts.LLMAgent = MockLLMAgent

from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_full_flow_routes_to_llm():
    # Start the app (TestClient triggers startup)
    with client:
        payload = {
            "update_id": 20000,
            "message": {
                "message_id": 2,
                "from": {"id": 54321, "is_bot": False, "first_name": "E2E"},
                "chat": {"id": 54321, "type": "private"},
                "date": 0,
                "text": "E2E test message"
            }
        }
        res = client.post("/v1/webhook/telegram", json=payload)
        assert res.status_code == 200

        # Give background tasks a moment to process
        time.sleep(1.0)

    # After shutdown, ensure LLMAgent received a generate request
    assert any(call[0] in ("generate", "generate") for call in llm_calls), f"No LLMAgent calls recorded: {llm_calls}"
