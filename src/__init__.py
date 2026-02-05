"""Package initialization."""

__version__ = "0.1.0"
__author__ = "MiniClaw Team"

from .main import MiniClawAssistant
from .core.types import UserMessage, ConversationContext

__all__ = [
    "MiniClawAssistant",
    "UserMessage",
    "ConversationContext",
]
