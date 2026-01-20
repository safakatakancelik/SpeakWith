"""Shared data models used across all modules."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import asyncio
import time

import numpy as np


class ConversationMode(Enum):
    """Available conversation modes that affect suggestion style."""
    FRIENDLY = "friendly"
    SHOPPING = "shopping"


class PipelineStatus(Enum):
    """Current status of the processing pipeline."""
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    GENERATING = "generating"


@dataclass
class AudioChunk:
    """A chunk of recorded audio data."""
    data: np.ndarray
    sample_rate: int
    timestamp: float
    duration: float = 10.0


@dataclass
class Transcript:
    """A transcription result from audio processing."""
    text: str
    timestamp: float
    duration: float

    @property
    def is_empty(self) -> bool:
        """Check if transcript contains meaningful speech."""
        return not self.text or self.text.strip() == ""


@dataclass
class Suggestions:
    """Response suggestions for the user."""
    reactions: list[str] = field(default_factory=lambda: ["Yes", "No", "Tell me more"])
    followups: list[str] = field(default_factory=list)

    @classmethod
    def default(cls) -> "Suggestions":
        """Create default suggestions when no context is available."""
        return cls(
            reactions=["Yes", "No", "Tell me more"],
            followups=[
                "Could you repeat that?",
                "I'm listening.",
                "Go on.",
            ]
        )


@dataclass
class UserProfile:
    """User profile loaded from markdown files."""
    background: str
    mood_board: str

    @classmethod
    def empty(cls) -> "UserProfile":
        """Create an empty profile."""
        return cls(background="", mood_board="")


@dataclass
class ConversationContext:
    """Full context for generating suggestions."""
    mode: ConversationMode
    profile: UserProfile
    summary: str
    recent_transcripts: list[Transcript]
    user_last_response: Optional[str]


@dataclass
class SharedState:
    """Thread-safe shared state for the async pipeline.

    All mutations should go through the provided methods to ensure
    proper synchronization.
    """
    # Configuration
    mode: ConversationMode = ConversationMode.FRIENDLY
    profile: UserProfile = field(default_factory=UserProfile.empty)

    # Conversation state
    transcripts: list[Transcript] = field(default_factory=list)
    summary: str = ""
    suggestions: Suggestions = field(default_factory=Suggestions.default)
    user_response: Optional[str] = None

    # Pipeline state
    status: PipelineStatus = PipelineStatus.IDLE
    start_time: float = field(default_factory=time.time)

    # Synchronization
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)
    _state_changed: asyncio.Event = field(default_factory=asyncio.Event, repr=False)

    # Configuration
    max_transcripts: int = 3

    async def add_transcript(self, transcript: Transcript) -> None:
        """Add a transcript, maintaining circular buffer of last N."""
        async with self._lock:
            self.transcripts.append(transcript)
            if len(self.transcripts) > self.max_transcripts:
                self.transcripts = self.transcripts[-self.max_transcripts:]
            self._state_changed.set()

    async def set_suggestions(self, suggestions: Suggestions) -> None:
        """Update current suggestions."""
        async with self._lock:
            self.suggestions = suggestions
            self._state_changed.set()

    async def set_user_response(self, response: str) -> None:
        """Record user's selected/typed response."""
        async with self._lock:
            self.user_response = response
            self._state_changed.set()

    async def set_summary(self, summary: str) -> None:
        """Update conversation summary."""
        async with self._lock:
            self.summary = summary
            self._state_changed.set()

    async def set_status(self, status: PipelineStatus) -> None:
        """Update pipeline status."""
        async with self._lock:
            self.status = status
            self._state_changed.set()

    async def wait_for_change(self) -> None:
        """Wait for any state change."""
        await self._state_changed.wait()
        self._state_changed.clear()

    def get_context(self) -> ConversationContext:
        """Get current conversation context for suggestion generation."""
        return ConversationContext(
            mode=self.mode,
            profile=self.profile,
            summary=self.summary,
            recent_transcripts=list(self.transcripts),
            user_last_response=self.user_response,
        )

    @property
    def elapsed_time(self) -> float:
        """Seconds since session started."""
        return time.time() - self.start_time

    @property
    def elapsed_formatted(self) -> str:
        """Elapsed time as MM:SS string."""
        elapsed = int(self.elapsed_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"
