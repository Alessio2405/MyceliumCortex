"""Base agent class and agent lifecycle management."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

from .types import AgentLevel, AgentMessage, AgentReport, AgentConfig


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        """
        Initialize a base agent.
        
        Args:
            config: Agent configuration
            parent_agent_id: ID of parent supervisor (if applicable)
        """
        self.agent_id = config.agent_id
        self.level = config.level
        self.capabilities = config.capabilities
        self.config = config.config
        self.parent_agent_id = parent_agent_id
        
        self.is_running = False
        self.created_at = datetime.now()
        self.message_queue: asyncio.Queue = asyncio.Queue()
        
        logger.info(f"Created {self.level} agent: {self.agent_id}")

    async def start(self):
        """Start the agent."""
        self.is_running = True
        logger.info(f"Started agent: {self.agent_id}")
        
        # Start listening for messages
        try:
            await self._message_loop()
        except asyncio.CancelledError:
            logger.info(f"Agent {self.agent_id} cancelled")
            await self.stop()

    async def stop(self):
        """Stop the agent."""
        self.is_running = False
        logger.info(f"Stopped agent: {self.agent_id}")
        await self.cleanup()

    async def send_message(self, message: AgentMessage):
        """Send a message to this agent."""
        await self.message_queue.put(message)

    async def _message_loop(self):
        """Main message processing loop."""
        while self.is_running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                await self.on_message(message)
            except asyncio.TimeoutError:
                # No message, continue
                pass
            except Exception as e:
                logger.error(f"Error in message loop for {self.agent_id}: {e}")

    @abstractmethod
    async def on_message(self, message: AgentMessage):
        """Handle incoming message. Must be implemented by subclasses."""
        pass

    async def report_to_parent(self, report: AgentReport):
        """Report results to parent supervisor."""
        if self.parent_agent_id:
            logger.debug(f"{self.agent_id} reporting to {self.parent_agent_id}: {report.action}")
            # In a real system, this would send to parent through message bus
            # For now, we'll implement this in supervisors

    async def cleanup(self):
        """Cleanup resources. Override in subclasses if needed."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.agent_id}, level={self.level})"


class ExecutionAgent(BaseAgent):
    """Base class for execution layer agents (do actual work)."""

    async def on_message(self, message: AgentMessage):
        """Handle incoming directive."""
        action = message.action
        payload = message.payload

        try:
            result = await self.execute_action(action, payload)
            
            # Report success
            report = AgentReport(
                agent_id=self.agent_id,
                action=action,
                status="success",
                data=result
            )
            await self.report_to_parent(report)
            
        except Exception as e:
            logger.error(f"{self.agent_id} failed on {action}: {e}")
            
            report = AgentReport(
                agent_id=self.agent_id,
                action=action,
                status="failed",
                data={},
                error=str(e)
            )
            await self.report_to_parent(report)

    @abstractmethod
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action. Must be implemented by subclasses."""
        pass


class TacticalSupervisor(BaseAgent):
    """Base class for tactical layer supervisors (coordinate execution agents)."""

    def __init__(self, config: AgentConfig, parent_agent_id: Optional[str] = None):
        super().__init__(config, parent_agent_id)
        self.children: Dict[str, BaseAgent] = {}

    async def on_message(self, message: AgentMessage):
        """Handle incoming message or directive from parent."""
        await self.on_directive(message)

    async def delegate(self, child_id: str, message: AgentMessage) -> Optional[AgentReport]:
        """
        Delegate a task to a child agent.
        
        This is simplified - in a real system would use message bus with callbacks.
        """
        if child_id not in self.children:
            raise ValueError(f"Child agent {child_id} not found")
        
        child = self.children[child_id]
        await child.send_message(message)
        # In real system, would wait for response via message bus
        return None

    async def spawn_child(self, config: AgentConfig, agent_class):
        """Spawn a new child agent."""
        agent = agent_class(config, parent_agent_id=self.agent_id)
        self.children[config.agent_id] = agent
        logger.info(f"{self.agent_id} spawned child: {config.agent_id}")
        return agent

    async def on_directive(self, message: AgentMessage):
        """Handle directive from parent. Override in subclasses."""
        pass

    async def cleanup(self):
        """Cleanup child agents."""
        for child in self.children.values():
            await child.stop()


class StrategicCoordinator(BaseAgent):
    """Base class for strategic layer coordinators."""

    def __init__(self, config: AgentConfig):
        super().__init__(config, parent_agent_id=None)
        self.supervisors: Dict[str, TacticalSupervisor] = {}

    async def on_message(self, message: AgentMessage):
        """Handle incoming message."""
        await self.on_directive(message)

    async def delegate_to_supervisor(self, supervisor_id: str, message: AgentMessage):
        """Delegate to a supervisor."""
        if supervisor_id not in self.supervisors:
            raise ValueError(f"Supervisor {supervisor_id} not found")
        
        supervisor = self.supervisors[supervisor_id]
        await supervisor.send_message(message)

    async def register_supervisor(self, supervisor: TacticalSupervisor):
        """Register a tactical supervisor."""
        self.supervisors[supervisor.agent_id] = supervisor
        logger.info(f"Coordinator {self.agent_id} registered supervisor: {supervisor.agent_id}")

    async def on_directive(self, message: AgentMessage):
        """Handle directive. Override in subclasses."""
        pass

    async def cleanup(self):
        """Cleanup supervisors."""
        for supervisor in self.supervisors.values():
            await supervisor.stop()
