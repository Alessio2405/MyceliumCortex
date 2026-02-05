"""Core type definitions for the agent system."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from .agent import BaseAgent


class AgentLevel(str, Enum):
    """Agent hierarchy levels."""
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    EXECUTION = "execution"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender_id: str
    action: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: Optional[str] = None


@dataclass
class AgentReport:
    """Report sent from child agent to parent supervisor."""
    agent_id: str
    action: str
    status: str  # success, failed, pending
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


@dataclass
class UserMessage:
    """User input message."""
    text: str
    channel: str  # "terminal", "telegram", "whatsapp"
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConversationContext:
    """Conversation history and metadata."""
    conversation_id: str
    user_id: str
    channel: str
    messages: List[Dict[str, str]] = field(default_factory=list)  # [{"role": "user"|"assistant", "content": "..."}]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolTask:
    """Task to be executed by a tool agent."""
    tool_name: str
    action: str
    parameters: Dict[str, Any]
    timeout: int = 30  # seconds


@dataclass
class ToolResult:
    """Result from tool execution."""
    tool_name: str
    action: str
    status: str  # success, failed
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_id: str
    level: AgentLevel
    capabilities: List[str]
    config: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """Registry to track all agents in the system."""
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Register an agent."""
        self.agents[agent.agent_id] = agent

    def unregister(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def get_by_level(self, level: AgentLevel) -> List[BaseAgent]:
        """Get all agents at a specific level."""
        return [a for a in self.agents.values() if a.level == level]

    def get_by_capability(self, capability: str) -> List[BaseAgent]:
        """Get all agents with a specific capability."""
        return [a for a in self.agents.values() if capability in a.capabilities]
