# Pipeline Module

## Purpose

Orchestrates all async tasks in the SpeakWith system.

## Files

- `coordinator.py` - Main pipeline coordinator

## Key Class

### PipelineCoordinator

```python
class PipelineCoordinator:
    def __init__(self, config: Config, mode: ConversationMode)
    async def initialize(self) -> None  # Pre-load models
    async def run(self) -> None         # Start all tasks
    async def stop(self) -> None        # Graceful shutdown
```

## Task Orchestration

Creates and manages these concurrent tasks:

1. **Recording Task** (`_recording_task`)
   - Streams audio chunks from recorder
   - Sends to transcriber
   - Updates memory with transcripts

2. **Suggestions Task** (`suggestion_gen.run`)
   - Watches for new transcripts
   - Generates new suggestions

3. **Display Task** (`display.run`)
   - Renders UI on state changes

4. **Input Task** (`input_handler.run`)
   - Captures user selections

5. **Summary Task** (`memory.run_summary_task`)
   - Periodically updates conversation summary

## Task Lifecycle

```
initialize() → run() → [all tasks running] → stop()
                              ↑
                    Ctrl+C or error triggers stop
```

## Shutdown Sequence

1. Set `_running = False`
2. Call `stop()` on all components
3. Cancel all tasks
4. Wait for tasks to finish

## Error Handling

- Individual task errors don't crash the system
- LLM/transcription errors logged, continue with previous state
- KeyboardInterrupt triggers graceful shutdown

## Component Initialization

```python
# Order matters for dependencies
self.state = SharedState(mode=mode)           # First
self.state.profile = profile_loader.load()    # Load profile into state
self.llm = OpenAIClient(config)               # Needed by memory/suggestions
self.memory = ConversationMemory(..., self.llm, self.state)
self.suggestion_gen = SuggestionGenerator(..., self.llm, self.state)
```

## Customization Points

- Swap LLM provider by changing `OpenAIClient` instantiation
- Add new tasks to `self._tasks` list
- Modify recording callback for different audio sources
