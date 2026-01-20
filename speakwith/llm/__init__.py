"""LLM integration module with provider abstraction."""

from speakwith.llm.base import BaseLLMClient
from speakwith.llm.openai_client import OpenAIClient

__all__ = ["BaseLLMClient", "OpenAIClient"]
