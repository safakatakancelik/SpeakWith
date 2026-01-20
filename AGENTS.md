# SpeakWith - Agent Guide

## Project Purpose

SpeakWith is a communication assistant for people who cannot speak but can read. It listens to environmental audio, transcribes speech using local Whisper, and suggests contextual responses via LLM that the user can select to communicate.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ASYNC EVENT LOOP                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│   │   RECORDER   │───▶│ TRANSCRIBER  │───▶│  SUGGESTION  │         │
│   │   (10 sec)   │    │   (Whisper)  │    │  GENERATOR   │         │
│   └──────────────┘    └──────────────┘    └──────────────┘         │
│          │                   │                   │                  │
│          ▼                   ▼                   ▼                  │
│   ┌─────────────────────────────────────────────────────┐          │
│   │              SHARED STATE (Thread-safe)             │          │
│   │  - transcripts[]    - summary    - suggestions      │          │
│   │  - user_response    - status     - timestamp        │          │
│   └─────────────────────────────────────────────────────┘          │
│                              │                                      │
│          ┌───────────────────┼───────────────────┐                 │
│          ▼                   ▼                   ▼                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│   │   DISPLAY    │    │    INPUT     │    │   MEMORY     │         │
│   │  (renders)   │    │  (non-block) │    │  (summarize) │         │
│   └──────────────┘    └──────────────┘    └──────────────┘         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Map

| Module | Purpose | Key Files |
|--------|---------|-----------|
| `speakwith/` | Main package | `main.py`, `config.py`, `models.py` |
| `speakwith/audio/` | Audio recording | `recorder.py` |
| `speakwith/transcription/` | Whisper integration | `whisper_client.py` |
| `speakwith/llm/` | LLM abstraction | `base.py`, `openai_client.py` |
| `speakwith/memory/` | Conversation context | `conversation.py` |
| `speakwith/suggestions/` | Response generation | `generator.py` |
| `speakwith/profiles/` | User profile loading | `loader.py` |
| `speakwith/modes/` | Conversation modes | `conversation_modes.py` |
| `speakwith/cli/` | Terminal UI | `display.py`, `input_handler.py` |
| `speakwith/pipeline/` | Orchestration | `coordinator.py` |

## Data Flow

1. **AudioRecorder** captures 10-second chunks → yields `AudioChunk`
2. **WhisperClient** transcribes → produces `Transcript`
3. **ConversationMemory** stores transcript, updates summary
4. **SuggestionGenerator** generates `Suggestions` from context
5. **Display** renders current state to terminal
6. **InputHandler** captures user selection → updates state

## Key Types (models.py)

- `AudioChunk`: numpy audio data + metadata
- `Transcript`: text + timestamp
- `Suggestions`: reactions (3) + followups (3)
- `SharedState`: thread-safe central state with async locks
- `ConversationContext`: full context for LLM calls
- `UserProfile`: background + mood board

## Interfaces

### LLM Provider Interface (llm/base.py)
```python
class BaseLLMClient(ABC):
    async def generate(self, prompt: str, system: str = "") -> str
    async def generate_suggestions(self, context: ConversationContext) -> Suggestions
    async def generate_summary(self, transcripts: list[str], previous_summary: str) -> str
```

### Async Pattern
All long-running operations use `asyncio`:
- Recording: `async for chunk in recorder.stream()`
- Transcription: `await transcriber.transcribe(chunk)`
- LLM calls: `await llm.generate(...)`
- State updates: `await state.add_transcript(...)`

## Configuration

Environment variables (`.env`):
- `OPENAI_API_KEY` (required)
- `WHISPER_MODEL` (default: base)
- `LLM_MODEL` (default: gpt-4o-mini)
- `CHUNK_DURATION` (default: 10.0)

## Running

```bash
uv run speakwith
# or
uv run python -m speakwith.main
```

## Testing Areas

When testing changes:
1. **Audio**: Test with actual microphone input
2. **Transcription**: Can use pre-recorded audio files
3. **LLM**: Mock the OpenAI client for unit tests
4. **CLI**: Test input handling and display rendering

## Common Tasks

### Adding a new LLM provider
1. Create `speakwith/llm/new_provider.py`
2. Implement `BaseLLMClient` interface
3. Add factory logic in `pipeline/coordinator.py`

### Adding a new conversation mode
1. Add enum value to `ConversationMode` in `models.py`
2. Add `ModeConfig` entry in `modes/conversation_modes.py`

### Modifying suggestion format
1. Update `Suggestions` dataclass in `models.py`
2. Update prompt in `llm/openai_client.py`
3. Update display in `cli/display.py`
