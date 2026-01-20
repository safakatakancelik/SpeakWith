# Memory Module

## Purpose

Manages conversation context: transcript history and LLM-generated summaries.

## Files

- `conversation.py` - Conversation memory manager

## Key Class

### ConversationMemory

```python
class ConversationMemory:
    def __init__(self, config: Config, llm: BaseLLMClient, state: SharedState)
    async def add_transcript(self, transcript: Transcript) -> None
    async def record_user_response(self, response: str) -> None
    async def run_summary_task(self, interval: float = 30.0) -> None
    def stop(self) -> None
```

## Data Flow

```
Transcript → Memory → SharedState.transcripts (circular buffer)
                  ↓
              LLM summary → SharedState.summary
```

## Memory Model

### Transcript Buffer
- Circular buffer of last N transcripts (default: 3)
- Stored in `SharedState.transcripts`
- Newest transcripts replace oldest

### Summary
- LLM-generated summary of conversation
- Updated every N transcripts (configurable)
- Also updated by periodic background task

## Dependencies

- `BaseLLMClient` for summary generation
- `SharedState` for storage

## Configuration

From `config.py`:
- `max_transcripts` (default: 3)
- `summary_update_interval` (default: 3 transcripts)

## Background Task

`run_summary_task()` periodically updates the summary even if no new transcripts arrive. Useful for long pauses in conversation.

## Integration Points

- Called by `PipelineCoordinator` after each transcription
- Summary used by `SuggestionGenerator` for context
