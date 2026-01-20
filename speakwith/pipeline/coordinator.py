"""Async pipeline orchestration for all SpeakWith tasks."""

import asyncio
from typing import Optional

from speakwith.audio import AudioRecorder
from speakwith.cli import Display, InputHandler
from speakwith.config import Config
from speakwith.llm import OpenAIClient
from speakwith.memory import ConversationMemory
from speakwith.models import ConversationMode, PipelineStatus, SharedState
from speakwith.profiles import ProfileLoader
from speakwith.suggestions import SuggestionGenerator
from speakwith.transcription import WhisperClient


class PipelineCoordinator:
    """Orchestrates all async tasks in the SpeakWith pipeline.

    Manages:
    - Audio recording (10-second batches)
    - Transcription (Whisper)
    - Suggestion generation (LLM)
    - Memory/summary updates
    - Display rendering
    - User input handling

    All tasks run concurrently in the async event loop.
    """

    def __init__(self, config: Config, mode: ConversationMode):
        self.config = config
        self.mode = mode

        # Initialize shared state
        self.state = SharedState(mode=mode)

        # Load user profile
        profile_loader = ProfileLoader(config)
        self.state.profile = profile_loader.load()

        # Initialize components
        self.recorder = AudioRecorder(config)
        self.transcriber = WhisperClient(config)
        self.llm = OpenAIClient(config)
        self.memory = ConversationMemory(config, self.llm, self.state)
        self.suggestion_gen = SuggestionGenerator(config, self.llm, self.state)
        self.display = Display(self.state)
        self.input_handler = InputHandler(self.state, self._on_user_response)

        # Task handles
        self._tasks: list[asyncio.Task] = []
        self._running = False

    async def _on_user_response(self, response: str) -> None:
        """Handle user response selection."""
        # Trigger new suggestions after user response
        try:
            suggestions = await self.suggestion_gen.generate()
            await self.state.set_suggestions(suggestions)
        except Exception:
            pass

    async def _recording_task(self) -> None:
        """Task that records audio and queues it for transcription."""
        try:
            async for chunk in self.recorder.stream():
                if not self._running:
                    break

                await self.state.set_status(PipelineStatus.RECORDING)

                # Transcribe the chunk
                await self.state.set_status(PipelineStatus.TRANSCRIBING)
                transcript = await self.transcriber.transcribe(chunk)

                # Add to memory (handles summary updates)
                await self.memory.add_transcript(transcript)

                await self.state.set_status(PipelineStatus.IDLE)

        except asyncio.CancelledError:
            pass

    async def initialize(self) -> None:
        """Initialize components (load models, etc.)."""
        # Pre-load Whisper model
        await self.transcriber.initialize()

    async def run(self) -> None:
        """Start all pipeline tasks and run until stopped."""
        self._running = True

        # Create tasks
        self._tasks = [
            asyncio.create_task(self._recording_task(), name="recording"),
            asyncio.create_task(self.suggestion_gen.run(), name="suggestions"),
            asyncio.create_task(self.display.run(), name="display"),
            asyncio.create_task(self.input_handler.run(), name="input"),
            asyncio.create_task(self.memory.run_summary_task(), name="summary"),
        ]

        try:
            # Wait for all tasks (or until one fails/is cancelled)
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop all pipeline tasks."""
        self._running = False

        # Stop components
        self.recorder.stop()
        self.suggestion_gen.stop()
        self.display.stop()
        self.input_handler.stop()
        self.memory.stop()

        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to finish
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks = []
