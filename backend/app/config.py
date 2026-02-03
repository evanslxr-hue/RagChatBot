from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./backend/data/app.db"
    chroma_persist_dir: str = "./backend/data/chroma"
    storage_root: str = "./backend/storage"
    max_pdf_mb: int = 10
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 5
    model_name: str = "google/flan-t5-base"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"


settings = Settings()


def ensure_directories() -> None:
    Path(settings.storage_root).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.database_url.replace("sqlite:///", "")).parent.mkdir(
        parents=True, exist_ok=True
    )
