"""Conversation memory management with summary and transcript history."""

import asyncio
from typing import Optional

from speakwith.config import Config
from speakwith.llm.base import BaseLLMClient
from speakwith.models import SharedState, Transcript


class ConversationMemory:
    """Manages conversation context including summary and transcript history.

    Handles:
    - Transcript circular buffer (last N transcripts)
    - Periodic summary updates via LLM
    - User response tracking
    """

    def __init__(self, config: Config, llm: BaseLLMClient, state: SharedState):
        self.config = config
        self.llm = llm
        self.state = state
        self._transcript_count = 0
        self._running = False

    async def add_transcript(self, transcript: Transcript) -> None:
        """Add a new transcript and potentially update summary."""
        if transcript.is_empty:
            return

        await self.state.add_transcript(transcript)
        self._transcript_count += 1

        # Update summary periodically
        if self._transcript_count % self.config.summary_update_interval == 0:
            await self._update_summary()

    async def _update_summary(self) -> None:
        """Update the conversation summary using LLM."""
        transcripts = [t.text for t in self.state.transcripts]
        if not transcripts:
            return

        try:
            new_summary = await self.llm.generate_summary(
                transcripts=transcripts,
                previous_summary=self.state.summary,
            )
            await self.state.set_summary(new_summary)
        except Exception:
            # Don't fail the pipeline if summary update fails
            pass

    async def record_user_response(self, response: str) -> None:
        """Record a user's response (selected or typed)."""
        await self.state.set_user_response(response)

    async def run_summary_task(self, interval: float = 30.0) -> None:
        """Background task that periodically updates the summary.

        Args:
            interval: Seconds between summary update checks.
        """
        self._running = True
        try:
            while self._running:
                await asyncio.sleep(interval)
                if self.state.transcripts:
                    await self._update_summary()
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop the background summary task."""
        self._running = False
