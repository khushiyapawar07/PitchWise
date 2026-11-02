from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    gemini_timeout_ms: int = 120_000
    ai_max_question_length: int = 500
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    data_raw_dir: Path = Path("../data/raw")
    data_processed_dir: Path = Path("../data/processed")
    data_metadata_dir: Path = Path("../data/metadata")

    def resolve_paths(self, base_dir: Path | None = None) -> "Settings":
        """Resolve relative data paths from the backend package root."""
        root = base_dir or Path(__file__).resolve().parents[1]
        object.__setattr__(self, "data_raw_dir", (root / self.data_raw_dir).resolve())
        object.__setattr__(self, "data_processed_dir", (root / self.data_processed_dir).resolve())
        object.__setattr__(self, "data_metadata_dir", (root / self.data_metadata_dir).resolve())
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    return Settings().resolve_paths()
