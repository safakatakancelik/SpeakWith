"""Async audio recorder that captures 10-second batches."""

import asyncio
from typing import AsyncIterator

import numpy as np
import sounddevice as sd

from speakwith.config import Config
from speakwith.models import AudioChunk


class AudioRecorder:
    """Records audio in fixed-duration chunks asynchronously.

    Yields AudioChunk objects containing numpy arrays of audio data.
    Designed to run continuously, producing one chunk every `chunk_duration` seconds.
    """

    def __init__(self, config: Config):
        self.sample_rate = config.sample_rate
        self.chunk_duration = config.chunk_duration
        self._running = False

    @property
    def samples_per_chunk(self) -> int:
        """Number of samples in each audio chunk."""
        return int(self.sample_rate * self.chunk_duration)

    async def record_chunk(self) -> AudioChunk:
        """Record a single audio chunk.

        Returns:
            AudioChunk containing the recorded audio data.
        """
        import time

        loop = asyncio.get_event_loop()

        # Run blocking recording in executor
        def _record() -> np.ndarray:
            recording = sd.rec(
                self.samples_per_chunk,
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
            )
            sd.wait()
            return recording.flatten()

        timestamp = time.time()
        data = await loop.run_in_executor(None, _record)

        return AudioChunk(
            data=data,
            sample_rate=self.sample_rate,
            timestamp=timestamp,
            duration=self.chunk_duration,
        )

    async def stream(self) -> AsyncIterator[AudioChunk]:
        """Continuously record and yield audio chunks.

        Yields:
            AudioChunk objects, one every chunk_duration seconds.
        """
        self._running = True
        try:
            while self._running:
                chunk = await self.record_chunk()
                yield chunk
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop the recording stream."""
        self._running = False
