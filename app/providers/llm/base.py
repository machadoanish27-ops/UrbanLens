"""Base interface and typed response structures for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LLMStatus(str, Enum):
    """Execution status for LLM operations."""

    SUCCESS = "success"
    ERROR = "error"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class LLMResponse:
    """Typed execution result from an LLM provider."""

    text: str
    provider: str
    model: str
    usage: dict[str, int] | None = None
    finish_reason: str | None = None
    latency_ms: float = 0.0
    status: LLMStatus = LLMStatus.SUCCESS
    warnings: tuple[str, ...] = field(default_factory=tuple)


class BaseLLMProvider(ABC):
    """Abstract interface defining LLM provider generation."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate completion asynchronously given system and user prompts."""
        ...
