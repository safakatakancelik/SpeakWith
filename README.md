# SpeakWith

**Draft - Not functional yet**

A communication assistant for people who cannot speak but can read.

## Concept

SpeakWith listens to conversations, transcribes speech in real-time, and suggests contextual responses the user can select to communicate.

This repository is **the brain only** - core logic intended to be integrated into apps, devices, or other interfaces later.

```
Audio → Transcription → LLM Suggestions → User Selection → Loop
```

## Vision

```
╔══════════════════════════════════════════════════════════════════╗
║  SPEAKWITH - Friendly Mode                          [00:01:23]   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📝 SUMMARY                                                      ║
║  Friend greeted me after not seeing me for a while. They asked   ║
║  about my weekend and mentioned they tried a new coffee shop.    ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🎙️ RECENT TRANSCRIPT                                            ║
║  [00:00:40] "Hey, how are you doing? Haven't seen you in         ║
║             a while!"                                            ║
║  [00:00:50] "I was wondering if you had any plans this           ║
║             weekend. We should hang out!"                        ║
║  [00:01:00] "Oh by the way, I tried that new coffee shop         ║
║             downtown. It was amazing!"                           ║
║                                                                  ║
║  💬 YOUR LAST RESPONSE                                           ║
║  "I've been doing well! Good to see you too."                    ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ⚡ QUICK REACTIONS                                               ║
║  [1] That sounds great!    [2] Really?    [3] Tell me more       ║
║                                                                  ║
║  💭 FOLLOW-UPS                                                    ║
║  [4] I'd love to check out that coffee shop! Where is it?        ║
║  [5] This weekend works for me. What did you have in mind?       ║
║  [6] I've been meaning to explore downtown more lately.          ║
║                                                                  ║
║  [c] Custom response                                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
> _
```

## Status

Early development. See [STATUS.md](STATUS.md) for implementation progress.

## License

MIT
