# Transcription Module

## Purpose

Transcribes audio chunks to text using local Whisper model via faster-whisper.

## Files

- `whisper_client.py` - Whisper model wrapper using faster-whisper

## Key Class

### WhisperClient

```python
class WhisperClient:
    def __init__(self, config: Config)
    async def transcribe(self, chunk: AudioChunk) -> Transcript
    async def initialize(self) -> None  # Pre-load model
```

## Data Flow

```
AudioChunk → faster-whisper (CTranslate2) → Transcript
```

## Dependencies

- `faster-whisper` (CTranslate2 backend, efficient local inference)
- Runs transcription in executor to avoid blocking

## Consumes

- `AudioChunk` from audio module

## Produces

- `Transcript` (defined in `models.py`):
  - `text: str` - Transcribed speech
  - `timestamp: float` - When audio was recorded
  - `duration: float` - Audio length

## Configuration

From `config.py`:
- `whisper_model` (default: "base", options: tiny, base, small, medium, large-v3)

## Model Loading

- Lazy loading on first transcription
- Optional `initialize()` for pre-loading at startup
- Uses CPU with int8 compute by default (efficient)
- VAD filter enabled to skip silence

## Performance Notes

- faster-whisper is 4x faster than openai-whisper
- Model size vs speed tradeoff:
  - `tiny`: Fastest, least accurate
  - `base`: Good balance for real-time
  - `large-v3`: Most accurate, slower

## Common Issues

1. **First transcription slow**: Model download + loading. Use `initialize()` at startup.
2. **Memory usage**: Larger models use more RAM
3. **Empty transcripts**: Normal when no speech detected (VAD filters silence)
