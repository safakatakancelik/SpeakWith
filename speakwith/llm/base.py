"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod

from speakwith.models import ConversationContext, Suggestions


class BaseLLMClient(ABC):
    """Abstract interface for LLM providers.

    All LLM implementations must inherit from this class and implement
    the abstract methods. This allows swapping providers without changing
    the rest of the application.
    """

    @abstractmethod
    async def generate(self, prompt: str, system: str = "") -> str:
        """Generate a text response from a prompt.

        Args:
            prompt: The user prompt to respond to.
            system: Optional system message for context.

        Returns:
            The generated text response.
        """
        pass

    @abstractmethod
    async def generate_suggestions(self, context: ConversationContext) -> Suggestions:
        """Generate response suggestions based on conversation context.

        Args:
            context: The current conversation context including transcripts,
                    summary, user profile, and mode.

        Returns:
            Suggestions containing reactions and follow-ups.
        """
        pass

    @abstractmethod
    async def generate_summary(self, transcripts: list[str], previous_summary: str) -> str:
        """Generate or update a conversation summary.

        Args:
            transcripts: Recent transcript texts.
            previous_summary: The existing summary to update.

        Returns:
            Updated summary string.
        """
        pass
