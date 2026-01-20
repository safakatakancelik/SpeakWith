# Audio Module

## Purpose

Captures environmental audio in 10-second batches for transcription.

## Files

- `recorder.py` - Async audio recorder using sounddevice

## Key Class

### AudioRecorder

```python
class AudioRecorder:
    def __init__(self, config: Config)
    async def record_chunk(self) -> AudioChunk
    async def stream(self) -> AsyncIterator[AudioChunk]
    def stop(self) -> None
```

## Data Flow

```
Microphone → sounddevice → numpy array → AudioChunk → Queue for transcription
```

## Dependencies

- `sounddevice` for audio capture
- `numpy` for audio data
- Uses `run_in_executor` to avoid blocking async loop

## Produces

- `AudioChunk` (defined in `models.py`):
  - `data: np.ndarray` - Audio samples
  - `sample_rate: int` - Hz
  - `timestamp: float` - Recording start time
  - `duration: float` - Chunk length in seconds

## Configuration

From `config.py`:
- `sample_rate` (default: 16000 Hz)
- `chunk_duration` (default: 10.0 seconds)

## Testing

Test with actual microphone or mock `sounddevice.rec()` for unit tests.

## Common Issues

1. **No audio device**: Check `sounddevice.query_devices()`
2. **Blocking event loop**: Recording runs in executor
3. **Sample rate mismatch**: Whisper expects 16kHz
