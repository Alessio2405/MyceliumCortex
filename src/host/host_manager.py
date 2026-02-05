import asyncio
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from ..core.types import AgentConfig

logger = logging.getLogger("myceliumcortex.host")


class HostManager:
    """Manage agent configurations and spawn/stop agents locally.

    Stores agent definitions in `~/.myceliumcortex/agents.json` and can spawn
    agents as asyncio tasks in-process. This is a minimal host-mode manager
    supporting autonomous agent workflows.
    """

    def __init__(self, storage_path: Optional[str] = None):
        home = Path.home()
        cfg_dir = Path(storage_path) if storage_path else home / ".myceliumcortex"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        self.cfg_file = cfg_dir / "agents.json"
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._load()

    def _load(self):
        if self.cfg_file.exists():
            try:
                with open(self.cfg_file, "r", encoding="utf-8") as f:
                    self._agents = json.load(f)
            except Exception:
                logger.exception("Failed to load agents.json")
                self._agents = {}

    def _save(self):
        try:
            with open(self.cfg_file, "w", encoding="utf-8") as f:
                json.dump(self._agents, f, indent=2)
            # restrict permissions
            try:
                os.chmod(self.cfg_file, 0o600)
            except Exception:
                pass
        except Exception:
            logger.exception("Failed to save agents.json")

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        return self._agents.copy()

    def register_agent(self, agent_id: str, config: Dict[str, Any]):
        self._agents[agent_id] = config
        self._save()

    def update_agent(self, agent_id: str, config: Dict[str, Any]):
        if agent_id not in self._agents:
            raise KeyError(agent_id)
        self._agents[agent_id].update(config)
        self._save()

    def remove_agent(self, agent_id: str):
        if agent_id in self._agents:
            self._agents.pop(agent_id)
            self._save()

    async def enable_agent(self, agent_id: str):
        """Start an agent according to its configuration (in-process task)."""
        async with self._lock:
            if agent_id in self._running_tasks:
                return
            cfg = self._agents.get(agent_id)
            if not cfg:
                raise KeyError(agent_id)

            # For minimal implementation, we can instantiate a class by dotted path
            class_path = cfg.get("class")
            if not class_path:
                raise ValueError("Agent config must include 'class' path")

            module_name, _, class_name = class_path.rpartition('.')
            if not module_name:
                raise ValueError("Invalid class path")

            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
            except Exception as e:
                logger.exception("Failed to import agent class %s: %s", class_path, e)
                raise

            # Build AgentConfig
            agent_cfg = AgentConfig(
                agent_id=agent_id,
                level=cfg.get("level", None) or AgentConfig.__annotations__.get('level'),
                capabilities=cfg.get("capabilities", []),
                config=cfg.get("config", {})
            )

            # Instantiate and start in a task
            try:
                agent = cls(agent_cfg)
                task = asyncio.create_task(agent.start())
                self._running_tasks[agent_id] = task
            except Exception:
                logger.exception("Failed to start agent %s", agent_id)
                raise

    async def disable_agent(self, agent_id: str):
        async with self._lock:
            task = self._running_tasks.get(agent_id)
            if not task:
                return
            # Attempt to cancel and stop
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception("Error stopping agent %s", agent_id)
            finally:
                self._running_tasks.pop(agent_id, None)

    async def stop_all(self):
        async with self._lock:
            ids = list(self._running_tasks.keys())
        for aid in ids:
            await self.disable_agent(aid)
