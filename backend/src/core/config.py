from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_MODEL: str = "qwen2.5:7b"
    LLM_API_KEY: str = "ollama"

    SIRCHMUNK_LLM_API_KEY: str = "ollama"
    SIRCHMUNK_LLM_BASE_URL: str = "http://localhost:11434/v1"
    SIRCHMUNK_LLM_MODEL: str = "qwen2.5:7b"
    SIRCHMUNK_SEARCH_PATHS: str = "./data/sample_docs"
    SIRCHMUNK_MAX_CONCURRENT_SEARCHES: int = 3

    DATABASE_URL: str = "sqlite:///data/msis.db"
    LOG_LEVEL: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
