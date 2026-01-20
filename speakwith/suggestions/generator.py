"""Response suggestion generator using LLM."""

import asyncio

from speakwith.config import Config
from speakwith.llm.base import BaseLLMClient
from speakwith.models import PipelineStatus, SharedState, Suggestions


class SuggestionGenerator:
    """Generates contextual response suggestions using LLM.

    Watches for new transcripts and generates suggestions based on
    the current conversation context.
    """

    def __init__(self, config: Config, llm: BaseLLMClient, state: SharedState):
        self.config = config
        self.llm = llm
        self.state = state
        self._running = False
        self._last_transcript_count = 0

    async def generate(self) -> Suggestions:
        """Generate suggestions based on current conversation context."""
        context = self.state.get_context()
        return await self.llm.generate_suggestions(context)

    async def run(self) -> None:
        """Background task that generates suggestions when new transcripts arrive."""
        self._running = True
        try:
            while self._running:
                # Wait for state changes
                await self.state.wait_for_change()

                # Check if we have new transcripts
                current_count = len(self.state.transcripts)
                if current_count > self._last_transcript_count:
                    self._last_transcript_count = current_count

                    # Generate new suggestions
                    await self.state.set_status(PipelineStatus.GENERATING)
                    try:
                        suggestions = await self.generate()
                        await self.state.set_suggestions(suggestions)
                    except Exception:
                        # Keep old suggestions on error
                        pass
                    await self.state.set_status(PipelineStatus.IDLE)

        except asyncio.CancelledError:
            pass
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop the background generation task."""
        self._running = False
