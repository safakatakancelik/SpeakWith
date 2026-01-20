"""Local Whisper transcription client using faster-whisper."""

import asyncio

import numpy as np

from speakwith.config import Config
from speakwith.models import AudioChunk, Transcript


class WhisperClient:
    """Transcribes audio using faster-whisper model.

    Uses CTranslate2 backend for efficient inference.
    Loads the model lazily on first use to avoid startup delay.
    Runs transcription in executor to avoid blocking the event loop.
    """

    def __init__(self, config: Config):
        self.model_name = config.whisper_model
        self._model = None

    def _load_model(self):
        """Load the Whisper model (lazy initialization)."""
        if self._model is None:
            from faster_whisper import WhisperModel

            # Use CPU by default, can be changed to "cuda" for GPU
            self._model = WhisperModel(
                self.model_name,
                device="cpu",
                compute_type="int8",  # Efficient for CPU
            )
        return self._model

    async def transcribe(self, chunk: AudioChunk) -> Transcript:
        """Transcribe an audio chunk to text.

        Args:
            chunk: AudioChunk containing audio data.

        Returns:
            Transcript with the transcribed text.
        """
        loop = asyncio.get_event_loop()

        def _transcribe() -> str:
            model = self._load_model()
            # faster-whisper expects float32 audio normalized to [-1, 1]
            audio = chunk.data.astype(np.float32)

            segments, _ = model.transcribe(
                audio,
                language="en",
                beam_size=5,
                vad_filter=True,  # Filter out silence
            )

            # Combine all segments
            text = " ".join(segment.text.strip() for segment in segments)
            return text.strip()

        text = await loop.run_in_executor(None, _transcribe)

        return Transcript(
            text=text,
            timestamp=chunk.timestamp,
            duration=chunk.duration,
        )

    async def initialize(self) -> None:
        """Pre-load the model (optional, for faster first transcription)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_model)
