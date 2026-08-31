from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    # Optional second Groq key — conversation.py rotates to it when the first
    # hits a rate limit, instead of just sleeping and retrying the same key.
    groq_api_key_2: str | None = None
    groq_model: str = "openai/gpt-oss-120b"
    groq_stt_model: str = "whisper-large-v3"
    groq_tts_model: str = "canopylabs/orpheus-v1-english"
    groq_tts_voice: str = "tara"
    database_url: str = "postgresql://postgres:password@localhost:5432/financial_advisor"

    # Optional: route the conversation (chat/tool-calling) model through
    # OpenRouter instead of Groq. STT/TTS stay on Groq either way — OpenRouter
    # is only used for the chat completions in conversation.py. Set
    # CHAT_PROVIDER=openrouter and OPENROUTER_API_KEY to enable; the qwen
    # model on Groq's on_demand tier was found to be unreliable at multi-tool
    # orchestration (the final budget-delivery turn especially), and a
    # stronger model via OpenRouter follows tool-calling instructions far
    # more consistently.
    chat_provider: str = "groq"
    openrouter_api_key: str | None = None
    openrouter_model: str = "nvidia/nemotron-3-super-120b-a12b:free"

    # Gemini via Google's OpenAI-compatible endpoint (generativelanguage.
    # googleapis.com/v1beta/openai/) — a third option alongside groq/
    # openrouter. Set CHAT_PROVIDER=gemini and GEMINI_API_KEY to enable.
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-flash-lite-latest"

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
