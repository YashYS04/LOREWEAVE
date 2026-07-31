"""Abstract AI provider interface.

All AI provider implementations must subclass ``AIProvider`` and implement
every abstract method.  Business logic must depend only on this interface —
never on a concrete provider — enabling future providers to be swapped
without changing the service layer.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationResult:
    """Encapsulates a completed AI generation response."""

    text: str
    model: str
    provider: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


@dataclass(frozen=True)
class ProviderHealth:
    """Reports the operational status of an AI provider."""

    healthy: bool
    provider_name: str
    model: str
    message: str
    version: str | None = None


class AIProvider(ABC):
    """Abstract base class for all LOREWEAVE AI providers.

    Concrete implementations are registered and injected by ``AIService``.
    No method here should contain HTTP logic — that belongs in the provider.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (e.g. 'Ollama (IBM Granite 3.3 2B)')."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        """Generate a complete response for the given prompt."""

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """Yield response tokens as an async generator."""

    @abstractmethod
    async def health(self) -> ProviderHealth:
        """Perform a connectivity/readiness probe against the provider."""
